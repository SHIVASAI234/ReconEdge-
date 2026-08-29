from __future__ import annotations

from uuid import uuid4

from models import EvidencePackage, ExceptionRecord, ReconciliationSummary


def build_evidence_package(
    reconciliation_result: dict,
    currency: str = "EUR",
    investigation_id: str | None = None,
) -> EvidencePackage:
    investigation_id = investigation_id or f"INV-{uuid4().hex[:10].upper()}"

    summary = ReconciliationSummary(
        transactions_reviewed=reconciliation_result["transactions_reviewed"],
        match_count=reconciliation_result["match_count"],
        exception_count=reconciliation_result["exception_count"],
        match_rate=reconciliation_result["match_rate"],
        exception_rate=reconciliation_result["exception_rate"],
        gross_exception_exposure=reconciliation_result["gross_exception_exposure"],
        net_discrepancy=reconciliation_result["net_discrepancy"],
    )

    exceptions = [
        ExceptionRecord(**item)
        for item in reconciliation_result["exceptions"]
    ]

    return EvidencePackage(
        investigation_id=investigation_id,
        currency=currency,
        summary=summary,
        exceptions=exceptions,
    )
