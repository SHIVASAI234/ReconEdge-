from reconciliation_engine import reconcile_csv_texts

BANK = """transaction_id,amount,status
TX001,5000,settled
TX002,8500,settled
TX003,2400,settled
TX005,12000,settled
TX006,1750,settled
"""

INTERNAL = """transaction_id,amount,status
TX001,5000,settled
TX002,8000,settled
TX004,2400,pending
TX005,12000,settled
TX006,1750,pending
"""

def test_demo_reconciliation():
    result = reconcile_csv_texts(BANK, INTERNAL)

    assert result["transactions_reviewed"] == 6
    assert result["match_count"] == 2
    assert result["exception_count"] == 4
    assert result["gross_exception_exposure"] == 5300.0
    assert result["net_discrepancy"] == 500.0

    by_tx = {
        x["transaction_id"]: x["classification"]
        for x in result["exceptions"]
    }

    assert by_tx["TX002"] == "AMOUNT_MISMATCH"
    assert by_tx["TX003"] == "MISSING_INTERNAL"
    assert by_tx["TX004"] == "MISSING_BANK"
    assert by_tx["TX006"] == "STATUS_MISMATCH"
