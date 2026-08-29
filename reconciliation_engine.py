from __future__ import annotations


def reconcile_csv_texts(
    bank_csv_text: str,
    internal_csv_text: str,
    tolerance: float = 0.01,
) -> dict:
    """
    Deterministic reconciliation engine.

    This function intentionally imports everything it needs internally so the
    exact same function can be shipped into a Daytona sandbox with inspect.getsource().
    """
    import csv
    import io
    from decimal import Decimal, InvalidOperation

    tol = Decimal(str(tolerance))

    def load(text: str, source: str) -> dict:
        reader = csv.DictReader(io.StringIO(text))
        required = {"transaction_id", "amount", "status"}

        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                f"{source} CSV must contain transaction_id, amount, status"
            )

        rows = {}
        duplicates = []

        for row_num, row in enumerate(reader, start=2):
            tx_id = row["transaction_id"].strip()
            if not tx_id:
                raise ValueError(f"{source}: missing transaction_id at row {row_num}")

            if tx_id in rows:
                duplicates.append(tx_id)

            try:
                amount = Decimal(row["amount"].strip())
            except (InvalidOperation, AttributeError):
                raise ValueError(
                    f"{source}: invalid amount for transaction {tx_id}"
                )

            status = row["status"].strip().lower()
            if not status:
                raise ValueError(f"{source}: blank status for transaction {tx_id}")

            rows[tx_id] = {
                "amount": amount,
                "status": status,
            }

        if duplicates:
            raise ValueError(
                f"{source}: duplicate transaction_id values: "
                + ", ".join(sorted(set(duplicates)))
            )

        return rows

    bank = load(bank_csv_text, "Bank/Custodian")
    internal = load(internal_csv_text, "Internal")

    matches = []
    exceptions = []
    universe = sorted(set(bank) | set(internal))

    gross_exposure = Decimal("0")
    net_discrepancy = Decimal("0")

    for tx_id in universe:
        bank_row = bank.get(tx_id)
        internal_row = internal.get(tx_id)

        bank_amount = bank_row["amount"] if bank_row else Decimal("0")
        internal_amount = internal_row["amount"] if internal_row else Decimal("0")
        signed_difference = bank_amount - internal_amount
        absolute_difference = abs(signed_difference)

        net_discrepancy += signed_difference

        if bank_row is None:
            gross_exposure += absolute_difference
            exceptions.append({
                "transaction_id": tx_id,
                "classification": "MISSING_BANK",
                "bank_amount": None,
                "internal_amount": float(internal_row["amount"]),
                "signed_difference": float(signed_difference),
                "absolute_difference": float(absolute_difference),
                "variance_pct": 100.0 if internal_row["amount"] != 0 else 0.0,
                "bank_status": None,
                "internal_status": internal_row["status"],
                "evidence": [
                    "Transaction exists internally but is absent from bank/custodian data.",
                    f"Internal amount = {float(internal_row['amount']):.2f}",
                    f"Internal status = {internal_row['status']}",
                ],
            })
            continue

        if internal_row is None:
            gross_exposure += absolute_difference
            exceptions.append({
                "transaction_id": tx_id,
                "classification": "MISSING_INTERNAL",
                "bank_amount": float(bank_row["amount"]),
                "internal_amount": None,
                "signed_difference": float(signed_difference),
                "absolute_difference": float(absolute_difference),
                "variance_pct": 100.0 if bank_row["amount"] != 0 else 0.0,
                "bank_status": bank_row["status"],
                "internal_status": None,
                "evidence": [
                    "Transaction exists in bank/custodian data but is absent internally.",
                    f"Bank amount = {float(bank_row['amount']):.2f}",
                    f"Bank status = {bank_row['status']}",
                ],
            })
            continue

        denominator = max(abs(bank_row["amount"]), abs(internal_row["amount"]))
        variance_pct = (
            float((absolute_difference / denominator) * Decimal("100"))
            if denominator != 0
            else 0.0
        )

        if absolute_difference > tol:
            gross_exposure += absolute_difference
            exceptions.append({
                "transaction_id": tx_id,
                "classification": "AMOUNT_MISMATCH",
                "bank_amount": float(bank_row["amount"]),
                "internal_amount": float(internal_row["amount"]),
                "signed_difference": float(signed_difference),
                "absolute_difference": float(absolute_difference),
                "variance_pct": round(variance_pct, 4),
                "bank_status": bank_row["status"],
                "internal_status": internal_row["status"],
                "evidence": [
                    "Transaction exists in both systems.",
                    f"Bank amount = {float(bank_row['amount']):.2f}",
                    f"Internal amount = {float(internal_row['amount']):.2f}",
                    f"Signed difference = {float(signed_difference):.2f}",
                    f"Absolute difference = {float(absolute_difference):.2f}",
                    f"Variance = {variance_pct:.2f}%",
                ],
            })
            continue

        if bank_row["status"] != internal_row["status"]:
            exceptions.append({
                "transaction_id": tx_id,
                "classification": "STATUS_MISMATCH",
                "bank_amount": float(bank_row["amount"]),
                "internal_amount": float(internal_row["amount"]),
                "signed_difference": float(signed_difference),
                "absolute_difference": float(absolute_difference),
                "variance_pct": round(variance_pct, 4),
                "bank_status": bank_row["status"],
                "internal_status": internal_row["status"],
                "evidence": [
                    "Amounts are within tolerance but lifecycle statuses differ.",
                    f"Bank status = {bank_row['status']}",
                    f"Internal status = {internal_row['status']}",
                ],
            })
            continue

        matches.append({
            "transaction_id": tx_id,
            "amount": float(bank_row["amount"]),
            "status": bank_row["status"],
        })

    reviewed = len(universe)
    match_count = len(matches)
    exception_count = len(exceptions)

    return {
        "transactions_reviewed": reviewed,
        "match_count": match_count,
        "exception_count": exception_count,
        "match_rate": round((match_count / reviewed * 100) if reviewed else 0.0, 2),
        "exception_rate": round(
            (exception_count / reviewed * 100) if reviewed else 0.0, 2
        ),
        "gross_exception_exposure": round(float(gross_exposure), 2),
        "net_discrepancy": round(float(net_discrepancy), 2),
        "matches": matches,
        "exceptions": exceptions,
    }
