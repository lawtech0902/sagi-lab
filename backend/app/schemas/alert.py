from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID


# Triage Result Schema (nested in Alert)
class TriageResultBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verdict: str
    conclusion: str
    alert_source_type: Optional[str] = None
    alert_category: Optional[str] = None
    tactics: Optional[List[str]] = None
    techniques: Optional[List[str]] = None


class TiMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vt_detected: bool
    vt_positives: Optional[int] = None
    vt_total: Optional[int] = None
    vt_permalink: Optional[str] = None


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_value: str
    is_sensor: bool
    ti_match: Optional[TiMatchResponse] = None


class TriageResultDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_source_type: Optional[str] = None
    alert_category: Optional[str] = None
    tactics: Optional[List[str]] = None
    techniques: Optional[List[str]] = None
    verdict: str
    conclusion: str
    investigation_steps: Optional[Any] = None
    processing_time_ms: Optional[int] = None
    entities: List[EntityResponse] = []
    created_at: datetime


# Alert Schemas
class AlertBase(BaseModel):
    alert_name: str
    alert_level: str
    source_ip: Optional[List[str]] = None
    destination_ip: Optional[List[str]] = None
    host_ip: Optional[str] = None
    first_alert_time: datetime
    last_alert_time: datetime


class AlertCreate(BaseModel):
    alert_data: dict


# IP Validator Mixin
class IpValidatorMixin:
    @field_validator("source_ip", "destination_ip", mode="before", check_fields=False)
    @classmethod
    def validate_ip_list(cls, v):
        if v is None:
            return v
        return [str(ip) for ip in v]

    @field_validator("host_ip", mode="before", check_fields=False)
    @classmethod
    def validate_ip(cls, v):
        if v is None:
            return v
        return str(v)


from pydantic import BaseModel, ConfigDict, field_validator, Field, computed_field

# ... (Previous code remains)


class AlertListItem(BaseModel, IpValidatorMixin):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    # Backend field name matched to ORM, usually handled by from_attributes
    # But for serialization we want 'name' and 'level'
    alert_name: str = Field(serialization_alias="name")
    alert_level: str = Field(serialization_alias="level")

    # Internal fields for validation/ORM mapping, excluded from serialization if computed field exists?
    # Actually, we can just serailize them as is, or use computed fields.
    # Frontend expects sourceIp, destIp.

    source_ip: Optional[List[str]] = Field(default=None, exclude=True)
    destination_ip: Optional[List[str]] = Field(default=None, exclude=True)
    host_ip: Optional[str] = Field(default=None, serialization_alias="hostIp")

    first_alert_time: datetime = Field(serialization_alias="firstAlertTime")
    last_alert_time: datetime = Field(serialization_alias="lastAlertTime")
    upload_time: datetime = Field(serialization_alias="uploadTime")

    triage_result: Optional[TriageResultBrief] = Field(default=None, exclude=True)

    @computed_field(alias="sourceIp")
    def source_ip_str(self) -> str:
        if self.source_ip and len(self.source_ip) > 0:
            return self.source_ip[0]
        return ""

    @computed_field(alias="destIp")
    def dest_ip_str(self) -> str:
        if self.destination_ip and len(self.destination_ip) > 0:
            return self.destination_ip[0]
        return ""

    @computed_field
    def verdict(self) -> str:
        if self.triage_result:
            return self.triage_result.verdict
        return "Unknown"

    @computed_field
    def tactic(self) -> str:
        if (
            self.triage_result
            and self.triage_result.tactics
            and len(self.triage_result.tactics) > 0
        ):
            return self.triage_result.tactics[0]
        return "Unknown"

    @computed_field
    def technique(self) -> str:
        if (
            self.triage_result
            and self.triage_result.techniques
            and len(self.triage_result.techniques) > 0
        ):
            return self.triage_result.techniques[0]
        return "Unknown"


class AlertDetail(BaseModel, IpValidatorMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_name: str
    alert_level: str
    source_ip: Optional[List[str]] = None
    destination_ip: Optional[List[str]] = None
    host_ip: Optional[str] = None
    first_alert_time: datetime
    last_alert_time: datetime
    upload_time: datetime
    raw_data: dict
    triage_result: Optional[TriageResultDetail] = None


# Alias for response
AlertResponse = AlertDetail


class AlertListResponse(BaseModel):
    items: List[AlertListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AlertStats(BaseModel):
    total_critical: int
    by_level: List[dict]  # [{"name": "Critical", "count": 10, "color": "..."}]
