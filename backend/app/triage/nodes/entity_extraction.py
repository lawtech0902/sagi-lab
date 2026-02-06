"""
Entity Extraction Node

节点 3: 从告警中提取 IOC 和实体
- IP 地址: 合并 base_info 和 LLM 提取结果
- 其他实体: LLM 提取 + 验证
"""

import json
from langchain_qwq import ChatQwen

from app.triage.state import TriageState, ExtractedEntitiesOutput
from app.utils.prompt_loader import render_prompt
from app.utils.common import (
    is_valid_ip,
    is_valid_domain,
    is_valid_url,
    is_valid_hash,
    is_valid_email,
)
from app.pkg.logger import logger


async def entity_extraction_node(state: TriageState, llm: ChatQwen) -> dict:
    """
    实体提取节点 - 提取 IOC 和实体
    - IP 地址: 合并 base_info 和 LLM 提取结果
    - 其他实体: LLM 提取 + 验证
    """
    try:
        logger.info("Starting entity extraction node")
        base_info = state.get("base_info")
        alert_data = state["alert_data"]

        # 1. 准备基础 IP (作为 LLM 输入的补充，或者直接合并到结果)
        # 这里我们把 base_info 里的 IP 作为已知信息提供给 LLM 上下文（如果 prompt 需要）
        # 或者直接在后处理阶段合并
        base_ips = set()
        if base_info:
            base_ips.update(base_info.src_ip or [])
            base_ips.update(base_info.dst_ip or [])
            base_ips.update(base_info.attacker_ip or [])
            base_ips.update(base_info.victim_ip or [])

        classification = state.get("classification")

        structured_llm = llm.with_structured_output(ExtractedEntitiesOutput)

        prompt_text = render_prompt(
            "entity_extraction.md",
            alert_data=json.dumps(
                alert_data, indent=2, default=str, ensure_ascii=False
            ),
            category=classification.category if classification else "unknown",
        )

        llm_result = await structured_llm.ainvoke(prompt_text)

        # 2. 验证和合并
        # IP: base_ips + llm_ips (经过验证)
        final_ips = set([ip for ip in base_ips if is_valid_ip(ip)])
        for ip in llm_result.ips:
            if is_valid_ip(ip):
                final_ips.add(ip)

        # Domains
        final_domains = set([d for d in llm_result.domains if is_valid_domain(d)])

        # URLs
        final_urls = set([u for u in llm_result.urls if is_valid_url(u)])

        # Hashes
        final_hashes = set([h for h in llm_result.hashes if is_valid_hash(h)])

        # Emails
        final_emails = set([e for e in llm_result.emails if is_valid_email(e)])

        # 构建最终结果
        result = ExtractedEntitiesOutput(
            ips=list(final_ips),
            domains=list(final_domains),
            urls=list(final_urls),
            hashes=list(final_hashes),
            file_paths=list(set(llm_result.file_paths)),
            process_paths=list(set(llm_result.process_paths)),
            cmdlines=list(set(llm_result.cmdlines)),
            accounts=list(set(llm_result.accounts)),
            emails=list(set(final_emails)),
        )

        logger.info(
            f"Entity extraction completed. IPs: {len(result.ips)}, Domains: {len(result.domains)}"
        )

        return {"entities": result}
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}")
        return {"errors": [f"Entity extraction failed: {str(e)}"]}
