from models import ExceptionRecord
from risk_engine import score_exception

def test_material_amount_mismatch_is_scored():
    exception = ExceptionRecord(
        transaction_id="TX002",
        classification="AMOUNT_MISMATCH",
        bank_amount=8500,
        internal_amount=8000,
        signed_difference=500,
        absolute_difference=500,
        variance_pct=5.88,
        bank_status="settled",
        internal_status="settled",
        evidence=[],
    )

    risk = score_exception(
        exception,
        materiality_threshold=1000,
    )

    assert 0.0 <= risk.score <= 1.0
    assert risk.band in {"LOW", "MEDIUM", "HIGH"}
