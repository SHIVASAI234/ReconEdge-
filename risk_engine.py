from __future__ import annotations

from models import ExceptionRecord, RiskAssessment


TYPE_SEVERITY = {
    "AMOUNT_MISMATCH": 0.75,
    "MISSING_INTERNAL": 0.90,
    "MISSING_BANK": 0.85,
    "STATUS_MISMATCH": 0.55,
}


def _cap(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_exception(
    exception: ExceptionRecord,
    materiality_threshold: float = 1000.0,
    ageing_score: float = 0.0,
) -> RiskAssessment:
    threshold = max(float(materiality_threshold), 0.01)

    monetary = _cap(exception.absolute_difference / threshold)
    variance = _cap(exception.variance_pct / 10.0)
    type_score = TYPE_SEVERITY.get(exception.classification, 0.50)
    ageing = _cap(ageing_score)

    score = round(
        0.40 * monetary
        + 0.20 * variance
        + 0.30 * type_score
        + 0.10 * ageing,
        4,
    )

    if score >= 0.70:
        band = "HIGH"
    elif score >= 0.40:
        band = "MEDIUM"
    else:
        band = "LOW"

    return RiskAssessment(
        transaction_id=exception.transaction_id,
        score=score,
        band=band,
        components={
            "monetary_materiality": round(monetary, 4),
            "variance_severity": round(variance, 4),
            "exception_type_severity": round(type_score, 4),
            "ageing": round(ageing, 4),
        },
    )


def score_all(
    exceptions: list[ExceptionRecord],
    materiality_threshold: float = 1000.0,
) -> list[RiskAssessment]:
    return [
        score_exception(
            exception,
            materiality_threshold=materiality_threshold,
        )
        for exception in exceptions
    ]
