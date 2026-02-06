"""
ATT&CK Mapping Node

节点 2: 将告警映射到 MITRE ATT&CK 框架
"""

import json
from langchain_qwq import ChatQwen

from app.triage.state import TriageState, AttackMappingOutput
from app.utils.prompt_loader import render_prompt
from app.pkg.logger import logger


async def attack_mapping_node(state: TriageState, llm: ChatQwen) -> dict:
    """
    ATT&CK 映射节点 - 映射战术和技术

    Args:
        state: 当前工作流状态
        llm: ChatQwen LLM 实例

    Returns:
        状态更新字典
    """
    try:
        logger.info("Starting ATT&CK mapping node")
        alert_data = state["alert_data"]
        classification = state.get("classification")

        structured_llm = llm.with_structured_output(AttackMappingOutput)

        prompt_text = render_prompt(
            "attack_mapping.md",
            alert_data=json.dumps(
                alert_data, indent=2, default=str, ensure_ascii=False
            ),
            classification=json.dumps(
                classification.model_dump() if classification else {},
                indent=2,
                ensure_ascii=False,
            ),
        )

        result = await structured_llm.ainvoke(prompt_text)

        logger.info(f"ATT&CK mapping completed: {result.tactic}/{result.technique}")
        return {"attack_mapping": result}
    except Exception as e:
        logger.error(f"Attack mapping failed: {e}")
        return {"errors": [f"Attack mapping failed: {str(e)}"]}
