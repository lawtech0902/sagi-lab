"""
Classification Node

节点 1: 对告警进行分类（来源类型和类别）
"""

import json
from langchain_qwq import ChatQwen

from app.triage.state import TriageState, ClassificationOutput
from app.utils.prompt_loader import render_prompt
from app.pkg.logger import logger


async def classify_node(state: TriageState, llm: ChatQwen) -> dict:
    """
    分类节点 - 确定告警类型
    """
    try:
        logger.info("Starting classification node")
        alert_data = state["alert_data"]
        base_info = state.get("base_info")

        structured_llm = llm.with_structured_output(ClassificationOutput)

        prompt_text = render_prompt(
            "classification.md",
            alert_data=json.dumps(
                alert_data, indent=2, default=str, ensure_ascii=False
            ),
        )

        result = await structured_llm.ainvoke(prompt_text)

        # 将 output 转换为 schema 对象 (如果需要，或者直接用 Pydantic model)
        # 这里 result 已经是 ClassificationOutput (Pydantic object)

        logger.info(f"Classification completed: {result.source_type}/{result.category}")
        return {"classification": result}
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return {"errors": [f"Classification failed: {str(e)}"]}
