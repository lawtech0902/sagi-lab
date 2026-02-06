"""
Analysis Node

节点 5: 最终分析，生成结论和调查步骤
"""

import json
from langchain_qwq import ChatQwen

from app.triage.state import TriageState, AnalysisOutput
from app.utils.prompt_loader import render_prompt
from app.pkg.logger import logger


async def analysis_node(state: TriageState, llm: ChatQwen) -> dict:
    """
    分析节点 - 生成最终结论和调查步骤

    根据是否有 verdict 使用不同的 prompt:
    - 有 verdict: 使用简化 prompt，解释已确定的结论
    - 无 verdict: 使用完整 prompt，进行全面分析

    Args:
        state: 当前工作流状态
        llm: ChatQwen LLM 实例

    Returns:
        状态更新字典
    """
    try:
        logger.info("Starting analysis node")
        structured_llm = llm.with_structured_output(AnalysisOutput)

        verdict = state.get("verdict")
        classification = state.get("classification")
        attack_mapping = state.get("attack_mapping")
        entities = state.get("entities")
        ti_matching = state.get("ti_matching")

        if verdict:
            # Verdict 已由 TI 匹配确定 - 使用 malicious 专用 prompt 但移除 verdict 字段
            prompt_text = render_prompt(
                "analysis_malicious.md",
                alert_data=json.dumps(
                    state["alert_data"], indent=2, default=str, ensure_ascii=False
                ),
                classification=json.dumps(
                    classification.model_dump() if classification else {},
                    indent=2,
                    ensure_ascii=False,
                ),
                attack_mapping=json.dumps(
                    attack_mapping.model_dump() if attack_mapping else {},
                    indent=2,
                    ensure_ascii=False,
                ),
                ti_results=json.dumps(
                    ti_matching.model_dump() if ti_matching else {},
                    indent=2,
                    ensure_ascii=False,
                ),
            )
        else:
            # 需要完整分析
            prompt_text = render_prompt(
                "analysis_full.md",
                alert_data=json.dumps(
                    state["alert_data"], indent=2, default=str, ensure_ascii=False
                ),
                classification=json.dumps(
                    classification.model_dump() if classification else {},
                    indent=2,
                    ensure_ascii=False,
                ),
                attack_mapping=json.dumps(
                    attack_mapping.model_dump() if attack_mapping else {},
                    indent=2,
                    ensure_ascii=False,
                ),
                entities=json.dumps(
                    entities.model_dump() if entities else {},
                    indent=2,
                    ensure_ascii=False,
                ),
                ti_results=json.dumps(
                    ti_matching.model_dump() if ti_matching else {},
                    indent=2,
                    ensure_ascii=False,
                ),
            )

        result = await structured_llm.ainvoke(prompt_text)

        logger.info("Analysis completed")
        return {"analysis": result}
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"errors": [f"Analysis failed: {str(e)}"]}
