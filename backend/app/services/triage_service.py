import time
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.triage_result import TriageResult
from app.models.entity import ExtractedEntity
from app.models.ti_match import TiMatch
from app.triage.graph import TriageGraph
from app.schemas.triage import AnalysisResult, TriageAnalysisResponse
from app.triage.graph import create_triage_graph
from app.pkg.logger import logger


class TriageService:
    def __init__(self, db: AsyncSession, graph: TriageGraph):
        self.db = db
        self.graph = graph

    async def analyze_alert(self, alert: Alert) -> TriageAnalysisResponse:
        """Run triage graph workflow on alert"""
        # Run LangGraph workflow - returns dict with schema objects
        result = await self.graph.process(alert.raw_data)

        processing_time_ms = result.get("processing_time_ms", 0)
        classification = result.get("classification")
        attack_mapping = result.get("attack_mapping")
        entities = result.get("entities")
        ti_matching = result.get("ti_matching")
        analysis = result.get("analysis")

        # Save triage result to database
        # Save triage result to database
        triage_result = TriageResult(
            alert_id=alert.id,
            alert_source_type=classification.source_type if classification else None,
            alert_category=classification.category if classification else None,
            tactic=attack_mapping.tactic if attack_mapping else None,
            technique=attack_mapping.technique if attack_mapping else None,
            conclusion=analysis.conclusion if analysis else None,
            investigation_steps=(
                [step.model_dump() for step in analysis.investigation_steps]
                if analysis
                else []
            ),
            processing_time_ms=processing_time_ms,
        )
        self.db.add(triage_result)
        await self.db.flush()

        logger.info(f"Triage result saved for alert {alert_id}")

        # Save extracted entities
        if entities:
            # Map unified entities list to DB
            # We need to handle the new structure where we don't have separate lists for hashes_types etc in Schema
            # But DB ExtractedEntity expects entity_type.

            entity_count = 0
            entity_objects = {}

            # Helper to add entity
            async def add_entity(e_type, value, is_sensor=False):
                nonlocal entity_count
                entity = ExtractedEntity(
                    triage_result_id=triage_result.id,
                    entity_type=e_type,
                    entity_value=value,
                    is_sensor=is_sensor,
                )
                self.db.add(entity)
                await self.db.flush()
                entity_objects[f"{e_type}:{value}"] = entity
                entity_count += 1

            for ip in entities.ips:
                await add_entity("ip", ip)
            for domain in entities.domains:
                await add_entity("domain", domain)
            for url in entities.urls:
                await add_entity("url", url)
            for h in entities.hashes:
                # We don't know exact hash type (md5/sha1/sha256) from the unified list easily unless we check length
                # For now let's just call it "hash" or auto-detect if necessary.
                # Model probably doesn't enforce "hash_md5" enum.
                e_type = "hash"
                if len(h) == 32:
                    e_type = "hash_md5"
                elif len(h) == 40:
                    e_type = "hash_sha1"
                elif len(h) == 64:
                    e_type = "hash_sha256"
                await add_entity(e_type, h)

            for f in entities.file_paths:
                await add_entity("file_path", f)
            for p in entities.process_paths:
                await add_entity("process_path", p)
            for c in entities.cmdlines:
                await add_entity("cmdline", c)
            for a in entities.accounts:
                await add_entity("account", a)
            for e in entities.emails:
                await add_entity("email", e)

            logger.info(f"Saved {entity_count} entities for alert {alert_id}")

            # Save TI matches
            if ti_matching:
                matches_count = 0
                for ti_item in ti_matching.results:
                    # ti_item has entity_type and entity_value.
                    # Note: entity_type for hash in ti_matching results is likely "hash" unless we updated it.
                    # We need to match the key we used in entity_objects.

                    # Try direct match first
                    key = f"{ti_item.entity_type}:{ti_item.entity_value}"
                    entity = entity_objects.get(key)

                    # If not found and it's a hash, try matching by value only (since we might have stored it as hash_md5 etc)
                    if not entity and ti_item.entity_type == "hash":
                        for k, v in entity_objects.items():
                            if k.endswith(f":{ti_item.entity_value}"):
                                entity = v
                                break

                    if entity:
                        ti_match = TiMatch(
                            entity_id=entity.id,
                            vt_detected=ti_item.malicious > 0,
                            vt_positives=ti_item.malicious,
                            vt_total=ti_item.total,
                            vt_permalink=None,  # Not present in new TiMatchItem
                        )
                        self.db.add(ti_match)
                        matches_count += 1
                logger.info(f"Saved {matches_count} TI matches for alert {alert_id}")

        await self.db.commit()

        return TriageAnalysisResponse(
            alert_id=alert.id,
            classification=classification,
            attack_mapping=attack_mapping,
            entities=entities,
            ti_matching=ti_matching,
            analysis=analysis,
            processing_time_ms=processing_time_ms,
        )

    async def delete_triage_result(self, alert_id: UUID) -> None:
        """Delete existing triage result for an alert"""
        await self.db.execute(
            delete(TriageResult).where(TriageResult.alert_id == alert_id)
        )
        await self.db.commit()
