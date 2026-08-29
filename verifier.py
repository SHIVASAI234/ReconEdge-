from __future__ import annotations

from models import AIInvestigationResponse, EvidencePackage, VerificationResult


def verify_ai_response(
    evidence: EvidencePackage,
    ai_response: AIInvestigationResponse,
) -> VerificationResult:
    issues = []

    if ai_response.investigation_id != evidence.investigation_id:
        issues.append("AI response investigation_id does not match evidence.")

    evidence_tx_ids = {e.transaction_id for e in evidence.exceptions}
    ai_tx_ids = {e.transaction_id for e in ai_response.exceptions}

    missing = sorted(evidence_tx_ids - ai_tx_ids)
    extra = sorted(ai_tx_ids - evidence_tx_ids)

    if missing:
        issues.append(
            "AI omitted exception transactions: " + ", ".join(missing)
        )

    if extra:
        issues.append(
            "AI introduced unknown transaction IDs: " + ", ".join(extra)
        )

    for item in ai_response.exceptions:
        if not item.hypotheses:
            issues.append(
                f"{item.transaction_id}: no root-cause hypotheses returned."
            )

        for hypothesis in item.hypotheses:
            if hypothesis.confidence < 0 or hypothesis.confidence > 1:
                issues.append(
                    f"{item.transaction_id}: confidence outside 0..1."
                )

        if not item.recommended_checks:
            issues.append(
                f"{item.transaction_id}: no recommended checks returned."
            )

    return VerificationResult(
        valid=not issues,
        issues=issues,
    )
