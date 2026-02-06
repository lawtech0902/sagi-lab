"""
Triage Workflow State Definition

按照 LangGraph 推荐架构定义状态
"""

from typing import TypedDict, Optional, List, Literal, Annotated
from operator import add
from pydantic import BaseModel, Field


# ============ Input Models (告警输入格式) ============


class BaseAlertInfo(BaseModel):
    """基础告警信息 - 直接从输入中提取，无需 LLM"""

    uuid: str = Field(description="告警唯一标识")
    name: str = Field(description="告警名称")
    severity: int = Field(description="严重程度 1-5")
    src_ip: List[str] = Field(default_factory=list, description="源IP列表")
    dst_ip: List[str] = Field(default_factory=list, description="目的IP列表")
    host_ip: Optional[str] = Field(default=None, description="主机IP")
    attacker_ip: List[str] = Field(default_factory=list, description="攻击者IP列表")
    victim_ip: List[str] = Field(default_factory=list, description="受害者IP列表")
    first_time: Optional[str] = Field(default=None, description="首次发生时间")
    last_time: Optional[str] = Field(default=None, description="最后发生时间")


# ============ Output Models (用于 LLM 结构化输出) ============


class ClassificationOutput(BaseModel):
    """分类结果"""

    source_type: Literal["Endpoint", "Network"] = Field(
        description="告警来源类型: Endpoint(终端类) 或 Network(网络类)"
    )
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
    ] = Field(description="告警类别")
    reasoning: str = Field(default="", description="分类推理过程")


class AttackMappingOutput(BaseModel):
    """ATT&CK 映射结果"""

    tactic: str = Field(description="MITRE ATT&CK Tactic ID")
    technique: str = Field(description="MITRE ATT&CK Technique ID")
    reasoning: str = Field(default="", description="映射推理过程")


class ExtractedEntitiesOutput(BaseModel):
    """提取的实体"""

    ips: List[str] = Field(default_factory=list, description="IP 地址列表")
    domains: List[str] = Field(default_factory=list, description="域名列表")
    urls: List[str] = Field(default_factory=list, description="URL 列表")
    hashes: List[str] = Field(
        default_factory=list, description="哈希列表 (MD5/SHA1/SHA256)"
    )
    file_paths: List[str] = Field(default_factory=list, description="文件路径列表")
    process_paths: List[str] = Field(default_factory=list, description="进程路径列表")
    cmdlines: List[str] = Field(default_factory=list, description="命令行列表")
    accounts: List[str] = Field(default_factory=list, description="账户名列表")
    emails: List[str] = Field(default_factory=list, description="邮箱地址列表")


class TiMatchItem(BaseModel):
    """单个 TI 匹配结果"""

    entity_type: str
    entity_value: str
    malicious: int = 0
    total: int = 0


class TiMatchingOutput(BaseModel):
    """TI 匹配结果"""

    total_checked: int = 0
    malicious_found: int = 0
    results: List[TiMatchItem] = Field(default_factory=list)


class InvestigationStep(BaseModel):
    """调查步骤"""

    step: int = Field(description="步骤编号")
    title: str = Field(description="步骤标题")
    details: str = Field(description="步骤详情")


class AnalysisOutput(BaseModel):
    """分析结果"""

    conclusion: Literal["malicious", "benign"] = Field(
        description="总体结论: malicious(恶意), benign(良性)"
    )
    investigation_steps: List[InvestigationStep] = Field(
        default_factory=list, description="调查步骤详情"
    )


# ============ LangGraph State ============


class TriageState(TypedDict):
    """
    Triage 工作流状态

    遵循 LangGraph 推荐:
    - 使用 TypedDict 获得最佳性能
    - 使用 Annotated 定义 reducer
    - 存储原始数据，在节点中格式化
    """

    # 输入
    alert_data: dict  # 完整的告警 JSON
    base_info: Optional[BaseAlertInfo]  # 解析后的基础信息
    start_time: float

    # 中间结果 (每个节点的输出)
    classification: Optional[ClassificationOutput]
    attack_mapping: Optional[AttackMappingOutput]
    entities: Optional[ExtractedEntitiesOutput]
    ti_matching: Optional[TiMatchingOutput]
    verdict: Optional[str]  # TI 匹配后的提前判定

    # 最终结果
    analysis: Optional[AnalysisOutput]
    processing_time_ms: Optional[int]

    # 错误收集 (使用 add reducer 累积错误)
    errors: Annotated[List[str], add]
