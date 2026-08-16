from typing import Literal

from pydantic import BaseModel, Field

PIIType = Literal["EMAIL", "PHONE", "NRIC", "CREDIT_CARD"]


class InvestigationRequest(BaseModel):
    log: str = Field(
        ...,
        min_length=1,
        description="Application log to investigate for privacy risks.",
    )


class PIIFinding(BaseModel):
    type: PIIType
    value: str
    start: int
    end: int

class InvestigationReport(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    pii_detected: list[PIIType]
    policy_violations: list[str]
    policy_sources: list[str]
    explanation: str
    recommended_action: str
    redacted_log: str | None = None

class InvestigationResponse(InvestigationReport):
    investigation_id: str