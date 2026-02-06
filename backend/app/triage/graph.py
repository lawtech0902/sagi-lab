"""
LangGraph-based Alert Triage Workflow

按照 LangGraph 官方推荐架构实现:
- state.py: 状态定义
- nodes/: 各节点实现
- graph.py: 图构建和编排
"""

import time
from typing import Optional
from functools import partial

from langgraph.graph import StateGraph, END
from langchain_qwq import ChatQwen

from app.core.config import get_settings
from app.pkg.logger import logger
from app.triage.state import (
    TriageState,
    BaseAlertInfo,
    ClassificationOutput,
    AttackMappingOutput,
    ExtractedEntitiesOutput,
    TiMatchingOutput,
    AnalysisOutput,
)
from app.triage.nodes.classify import classify_node
from app.triage.nodes.attack_mapping import attack_mapping_node
from app.triage.nodes.entity_extraction import entity_extraction_node
from app.triage.nodes.ti_matching import ti_matching_node
from app.triage.nodes.analysis import analysis_node
from app.pkg.virustotal.client import VirusTotalClient
from app.schemas.triage import (
    ClassificationResult,
    AttackMappingResult,
    ExtractedEntities,
    TiMatchItem,
    TiMatchingResult,
    InvestigationStep,
    AnalysisResult,
)


class TriageGraph:
    """
    基于 LangGraph 的 Triage 工作流

    工作流: classify → attack_mapping → entity_extraction → ti_matching → analysis → END
    """

    def __init__(
        self,
        llm: ChatQwen,
        vt_client: VirusTotalClient,
    ):
        self.llm = llm
        self.vt_client = vt_client

        # 构建状态图
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        workflow = StateGraph(TriageState)

        # 添加预处理节点解析 base_alert_info
        workflow.add_node("parse_input", self._parse_input_node)

        # 使用 partial 绑定依赖到节点函数
        workflow.add_node("classify", partial(classify_node, llm=self.llm))
        workflow.add_node("attack_mapping", partial(attack_mapping_node, llm=self.llm))
        workflow.add_node(
            "entity_extraction", partial(entity_extraction_node, llm=self.llm)
        )
        workflow.add_node(
            "ti_matching", partial(ti_matching_node, vt_client=self.vt_client)
        )
        workflow.add_node("analysis", partial(analysis_node, llm=self.llm))
        workflow.add_node("finalize", self._finalize_node)

        # 定义边（顺序工作流）
        workflow.set_entry_point("parse_input")
        workflow.add_edge("parse_input", "classify")
        workflow.add_edge("classify", "attack_mapping")
        workflow.add_edge("attack_mapping", "entity_extraction")
        workflow.add_edge("entity_extraction", "ti_matching")
        workflow.add_edge("ti_matching", "analysis")
        workflow.add_edge("analysis", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def _parse_input_node(self, state: TriageState) -> dict:
        """预处理节点 - 解析 base_alert_info"""
        try:
            alert_data = state["alert_data"]
            base_info_raw = alert_data.get("base_alert_info", {})

            # 处理 host_ip 可能是字符串 "[]" 的情况
            host_ip = base_info_raw.get("host_ip")
            if isinstance(host_ip, str):
                host_ip = None if host_ip in ("[]", "") else host_ip

            base_info = BaseAlertInfo(
                uuid=base_info_raw.get("uuid", ""),
                name=base_info_raw.get("name", ""),
                severity=base_info_raw.get("severity", 0),
                src_ip=base_info_raw.get("src_ip", []),
                dst_ip=base_info_raw.get("dst_ip", []),
                host_ip=host_ip,
                attacker_ip=base_info_raw.get("attacker_ip", []),
                victim_ip=base_info_raw.get("victim_ip", []),
                first_time=base_info_raw.get("first_time"),
                last_time=base_info_raw.get("last_time"),
            )
            return {"base_info": base_info}
        except Exception as e:
            return {"errors": [f"Parse input failed: {str(e)}"]}

    async def _finalize_node(self, state: TriageState) -> dict:
        """最终节点 - 计算处理时间"""
        processing_time_ms = int((time.time() - state["start_time"]) * 1000)
        return {"processing_time_ms": processing_time_ms}

    async def process(self, alert_data: dict) -> dict:
        """
        执行完整的 Triage 工作流

        Args:
            alert_data: 告警原始数据

        Returns:
            包含所有分析结果的字典
        """
        # 初始化状态
        initial_state: TriageState = {
            "alert_data": alert_data,
            "base_info": None,
            "start_time": time.time(),
            "classification": None,
            "attack_mapping": None,
            "entities": None,
            "ti_matching": None,
            "verdict": None,
            "analysis": None,
            "processing_time_ms": None,
            "errors": [],
        }

        # 执行工作流
        logger.info(
            f"Starting triage graph execution for alert: {alert_data.get('base_alert_info', {}).get('uuid', 'unknown')}"
        )
        try:
            final_state = await self.graph.ainvoke(initial_state)
            logger.info("Triage graph execution completed")

            # 转换为响应格式
            return self._convert_to_response(final_state)
        except Exception as e:
            logger.error(f"Triage graph execution failed: {e}")
            raise

    def _convert_to_response(self, state: TriageState) -> dict:
        """将状态转换为 API 响应格式"""
        return {
            "base_info": state.get("base_info"),
            "classification": (
                ClassificationResult(
                    source_type=state["classification"].source_type,
                    category=state["classification"].category,
                    reasoning=state["classification"].reasoning,
                )
                if state.get("classification")
                else None
            ),
            "attack_mapping": (
                AttackMappingResult(
                    tactic=state["attack_mapping"].tactic,
                    technique=state["attack_mapping"].technique,
                    reasoning=state["attack_mapping"].reasoning,
                )
                if state.get("attack_mapping")
                else None
            ),
            "entities": (
                ExtractedEntities(
                    ips=state["entities"].ips,
                    domains=state["entities"].domains,
                    urls=state["entities"].urls,
                    hashes=state["entities"].hashes,
                    file_paths=state["entities"].file_paths,
                    process_paths=state["entities"].process_paths,
                    cmdlines=state["entities"].cmdlines,
                    accounts=state["entities"].accounts,
                    emails=state["entities"].emails,
                )
                if state.get("entities")
                else None
            ),
            "ti_matching": (
                TiMatchingResult(
                    total_checked=state["ti_matching"].total_checked,
                    malicious_found=state["ti_matching"].malicious_found,
                    results=[
                        TiMatchItem(
                            entity_type=r.entity_type,
                            entity_value=r.entity_value,
                            malicious=r.malicious,
                            total=r.total,
                        )
                        for r in state["ti_matching"].results
                    ],
                )
                if state.get("ti_matching")
                else None
            ),
            "analysis": (
                AnalysisResult(
                    conclusion=state["analysis"].conclusion,
                    investigation_steps=[
                        InvestigationStep(step=s.step, title=s.title, details=s.details)
                        for s in state["analysis"].investigation_steps
                    ],
                )
                if state.get("analysis")
                else None
            ),
            "processing_time_ms": state.get("processing_time_ms"),
            "errors": state.get("errors", []),
        }


def create_triage_graph() -> TriageGraph:
    """创建 Triage Graph 实例"""
    settings = get_settings()

    llm = ChatQwen(
        model=settings.LLM_MODEL,
        base_url=settings.LLM_API_BASE,
        api_key=settings.LLM_API_KEY,
        temperature=0.7,  # Qwen3 推荐
        top_p=0.8,  # Qwen3 推荐
        enable_thinking=settings.LLM_ENABLE_THINKING,
    )

    vt_client = VirusTotalClient(settings.VIRUSTOTAL_API_KEY)

    return TriageGraph(llm=llm, vt_client=vt_client)
