from __future__ import annotations

import base64
import inspect
import json
import time

from daytona import Daytona

from reconciliation_engine import reconcile_csv_texts


def run_reconciliation_in_daytona(
    bank_csv_text: str,
    internal_csv_text: str,
    tolerance: float = 0.01,
) -> dict:
    """
    Executes the exact local reconciliation function inside one disposable
    Daytona sandbox, then returns structured JSON.
    """
    daytona = Daytona()
    sandbox = None
    sandbox_id = None
    deleted = False
    started = time.perf_counter()
    result = None

    function_source = inspect.getsource(reconcile_csv_texts)

    bank_b64 = base64.b64encode(bank_csv_text.encode("utf-8")).decode("ascii")
    internal_b64 = base64.b64encode(
        internal_csv_text.encode("utf-8")
    ).decode("ascii")

    sandbox_code = f"""
import base64
import json

{function_source}

bank_csv_text = base64.b64decode({bank_b64!r}).decode("utf-8")
internal_csv_text = base64.b64decode({internal_b64!r}).decode("utf-8")

result = reconcile_csv_texts(
    bank_csv_text,
    internal_csv_text,
    tolerance={float(tolerance)!r},
)

print(json.dumps(result))
"""

    try:
        sandbox = daytona.create()
        sandbox_id = sandbox.id

        response = sandbox.process.code_run(
            sandbox_code,
            timeout=60,
        )

        output = getattr(response, "result", "")
        exit_code = getattr(response, "exit_code", 0)

        if exit_code not in (0, None):
            raise RuntimeError(
                f"Daytona execution failed with exit code {exit_code}: {output}"
            )

        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if not lines:
            raise RuntimeError("Daytona sandbox returned no output.")

        result = json.loads(lines[-1])

    finally:
        if sandbox is not None:
            try:
                sandbox.delete()
                deleted = True
            except Exception:
                deleted = False

    if result is None:
        raise RuntimeError("No reconciliation result was produced.")

    result["sandbox"] = {
        "sandbox_id": sandbox_id,
        "runtime_seconds": round(time.perf_counter() - started, 3),
        "deleted": deleted,
    }
    return result
