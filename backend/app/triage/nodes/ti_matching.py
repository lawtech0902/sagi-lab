"""
Threat Intelligence Matching Node

节点 4: 使用 VirusTotal 进行威胁情报匹配
"""

import asyncio
from typing import Optional

from app.triage.state import (
    TriageState,
    TiMatchingOutput,
    TiMatchItem,
    ExtractedEntitiesOutput,
)
from app.pkg.virustotal.client import VirusTotalClient
from app.pkg.logger import logger


async def ti_matching_node(state: TriageState, vt_client: VirusTotalClient) -> dict:
    """
    TI 匹配节点 - 查询 VirusTotal 检查 IOC

    Args:
        state: 当前工作流状态
        vt_client: VirusTotal API 客户端

    Returns:
        状态更新字典
    """
    try:
        logger.info("Starting TI matching node")
        entities = state.get("entities")
        if not entities:
            logger.info("No entities to check, skipping TI matching")
            return {
                "ti_matching": TiMatchingOutput(
                    total_checked=0, malicious_found=0, results=[]
                ),
                "verdict": None,
            }

        ti_result = await _perform_ti_matching(entities, vt_client)

        # 根据 TI 结果判定 verdict
        verdict = _determine_verdict(state["alert_data"], entities, ti_result)

        logger.info(
            f"TI matching completed. Checked: {ti_result.total_checked}, Malicious: {ti_result.malicious_found}"
        )

        return {"ti_matching": ti_result, "verdict": verdict}
    except Exception as e:
        logger.error(f"TI matching failed: {e}")
        return {"errors": [f"TI matching failed: {str(e)}"]}


async def _perform_ti_matching(
    entities: ExtractedEntitiesOutput, vt_client: VirusTotalClient
) -> TiMatchingOutput:
    """执行 TI 匹配查询"""
    results = []
    total_checked = 0
    malicious_found = 0

    # 查询 IP
    for ip in entities.ips:
        # 排除 sensor_ips (虽然 entities 里没有 sensor_ips 字段了，但逻辑上我们只查外网 IP)
        # VirusTotalClient.check_ip 内部会检查 is_external_ip
        # 这里我们假设 entities.ips 已经是经过 extraction node 验证过的 IP
        result = await vt_client.check_ip(ip)
        if result:
            results.append(
                TiMatchItem(
                    entity_type="ip",
                    entity_value=ip,
                    malicious=result.positives,
                    total=result.total,
                )
            )
            total_checked += 1
            if result.detected:
                malicious_found += 1

    # 查询域名
    for domain in entities.domains:
        result = await vt_client.check_domain(domain)
        if result:
            results.append(
                TiMatchItem(
                    entity_type="domain",
                    entity_value=domain,
                    malicious=result.positives,
                    total=result.total,
                )
            )
            total_checked += 1
            if result.detected:
                malicious_found += 1

    # 查询 URL
    for url in entities.urls:
        result = await vt_client.check_url(url)
        if result:
            results.append(
                TiMatchItem(
                    entity_type="url",
                    entity_value=url,
                    malicious=result.positives,
                    total=result.total,
                )
            )
            total_checked += 1
            if result.detected:
                malicious_found += 1

    # 查询哈希 (Unified list)
    for hash_value in entities.hashes:
        result = await vt_client.check_hash(hash_value)
        if result:
            results.append(
                TiMatchItem(
                    entity_type="hash",
                    entity_value=hash_value,
                    malicious=result.positives,
                    total=result.total,
                )
            )
            total_checked += 1
            if result.detected:
                malicious_found += 1

    return TiMatchingOutput(
        total_checked=total_checked, malicious_found=malicious_found, results=results
    )


def _determine_verdict(
    alert_data: dict, entities: ExtractedEntitiesOutput, ti_result: TiMatchingOutput
) -> Optional[str]:
    """根据 TI 结果判定 verdict"""
    if ti_result.malicious_found > 0:
        return "malicious"

    # 检查是否为纯 IOC 类告警
    if _is_pure_ioc_alert(alert_data, entities) and ti_result.total_checked > 0:
        return "benign"

    return None


def _is_pure_ioc_alert(alert_data: dict, entities: ExtractedEntitiesOutput) -> bool:
    """检查是否为纯 IOC 类告警"""
    alert_name = str(alert_data.get("alert_name", "")).lower()
    alert_type = str(alert_data.get("type", "")).lower()

    ioc_keywords = [
        "ioc",
        "indicator",
        "threat intel",
        "ti match",
        "blacklist",
        "reputation",
    ]
    is_ioc_alert = any(kw in alert_name or kw in alert_type for kw in ioc_keywords)

    has_only_iocs = (
        (entities.ips or entities.domains or entities.urls or entities.hashes)
        and not entities.cmdlines
        and not entities.process_paths
    )

    return is_ioc_alert or has_only_iocs
