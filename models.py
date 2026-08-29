from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


ExceptionType = Literal[
    "MATCH",
    "AMOUNT_MISMATCH",
    "MISSING_INTERNAL",
    "MISSING_BANK",
    "STATUS_MISMATCH",
]


class ExceptionRecord(BaseModel):
    transaction_id: str
    classification: ExceptionType
    bank_amount: float | None = None
    internal_amount: float | None = None
    signed_difference: float = 0.0
    absolute_difference: float = 0.0
    variance_pct: float = 0.0
    bank_status: str | None = None
    internal_status: str | None = None
    evidence: list[str] = Field(default_factory=list)


class ReconciliationSummary(BaseModel):
    transactions_reviewed: int
    match_count: int
    exception_count: int
    match_rate: float
    exception_rate: float
    gross_exception_exposure: float
    net_discrepancy: float


class EvidencePackage(BaseModel):
    investigation_id: str
    currency: str
    summary: ReconciliationSummary
    exceptions: list[ExceptionRecord]


class RiskAssessment(BaseModel):
    transaction_id: str
    score: float
    band: Literal["LOW", "MEDIUM", "HIGH"]
    components: dict[str, float]


class AIHypothesis(BaseModel):
    rank: int
    cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: list[str] = Field(default_factory=list)


class AIExceptionAnalysis(BaseModel):
    transaction_id: str
    summary: str
    hypotheses: list[AIHypothesis]
    recommended_checks: list[str]
    escalation: str


class AIInvestigationResponse(BaseModel):
    investigation_id: str
    exceptions: list[AIExceptionAnalysis]


class VerificationResult(BaseModel):
    valid: bool
    issues: list[str] = Field(default_factory=list)
