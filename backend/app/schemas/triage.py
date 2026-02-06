from datetime import datetime
from typing import Optional, List, Any, Literal
from pydantic import BaseModel, field_validator
from uuid import UUID


# Classification
class ClassificationResult(BaseModel):
    source_type: Literal["Endpoint", "Network"]
    category: Literal[
        "Ransomware",
        "Malware",
        "Command & Control",
        "Network Exploitation",
        "Credential Access",
        "Reconnaissance",
        "Phishing",
        "Data Exfiltration",
        "Network Anomaly",
    ]
    reasoning: Optional[str] = None


# ATT&CK Mapping
class AttackMappingResult(BaseModel):
    tactic: str
    technique: str
    reasoning: Optional[str] = None


# Entity Extraction
class ExtractedEntities(BaseModel):
    ips: List[str] = []
    domains: List[str] = []
    urls: List[str] = []
    hashes: List[str] = []
    file_paths: List[str] = []
    process_paths: List[str] = []
    cmdlines: List[str] = []
    accounts: List[str] = []
    emails: List[str] = []


# TI Matching
class TiMatchItem(BaseModel):
    entity_type: str
    entity_value: str
    malicious: int
    total: int


class TiMatchingResult(BaseModel):
    total_checked: int
    malicious_found: int
    results: List[TiMatchItem]


# Investigation Step
class InvestigationStep(BaseModel):
    step: int
    title: str
    details: str


# Analysis
class AnalysisResult(BaseModel):
    conclusion: Literal["malicious", "benign"]
    investigation_steps: List[InvestigationStep]


# Full Triage Result
class TriageAnalysisRequest(BaseModel):
    alert_data: dict


class TriageAnalysisResponse(BaseModel):
    alert_id: UUID
    classification: ClassificationResult
    attack_mapping: AttackMappingResult
    entities: ExtractedEntities
    ti_matching: TiMatchingResult
    analysis: AnalysisResult
    processing_time_ms: int
