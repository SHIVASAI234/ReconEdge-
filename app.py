from __future__ import annotations

import os
from io import StringIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_reasoner import reason_with_ai
from daytona_runner import run_reconciliation_in_daytona
from evidence_builder import build_evidence_package
from risk_engine import score_all
from verifier import verify_ai_response


load_dotenv()


SAMPLE_BANK = """transaction_id,amount,status
TX001,5000,settled
TX002,8500,settled
TX003,2400,settled
TX005,12000,settled
TX006,1750,settled
"""

SAMPLE_INTERNAL = """transaction_id,amount,status
TX001,5000,settled
TX002,8000,settled
TX004,2400,pending
TX005,12000,settled
TX006,1750,pending
"""


def df_from_text(text: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(text))


st.set_page_config(
    page_title="ReconEdge",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ ReconEdge")
st.caption("Detect. Quantify. Investigate. Resolve.")

st.markdown(
    """
**ReconEdge** is an intelligent financial reconciliation and exception-resolution
platform. Daytona determines the facts inside an isolated sandbox; an optional AI
reasoning layer interprets those facts into ranked root-cause hypotheses and next checks.
"""
)

with st.sidebar:
    st.header("Execution")

    daytona_key = st.text_input(
        "Daytona API key",
        type="password",
        value="",
        placeholder="Paste full Daytona key",
    )
    if daytona_key:
        os.environ["DAYTONA_API_KEY"] = daytona_key.strip()

    currency = st.text_input(
        "Currency",
        value=os.getenv("RECON_CURRENCY", "EUR"),
    )
    tolerance = st.number_input(
        "Amount tolerance",
        min_value=0.0,
        value=float(os.getenv("RECON_TOLERANCE", "0.01")),
        step=0.01,
    )
    materiality = st.number_input(
        "Materiality threshold",
        min_value=1.0,
        value=float(os.getenv("RECON_MATERIALITY_THRESHOLD", "1000")),
        step=100.0,
    )

    st.divider()
    st.header("AI reasoning (optional)")
    use_ai = st.toggle("Enable AI reasoning", value=False)

    if use_ai:
        ai_url = st.text_input(
            "AI API URL",
            value=os.getenv("AI_API_URL", ""),
        )
        ai_key = st.text_input(
            "AI API key",
            type="password",
            value="",
        )
        ai_model = st.text_input(
            "AI model",
            value=os.getenv("AI_MODEL", ""),
        )

        if ai_url:
            os.environ["AI_API_URL"] = ai_url.strip()
        if ai_key:
            os.environ["AI_API_KEY"] = ai_key.strip()
        if ai_model:
            os.environ["AI_MODEL"] = ai_model.strip()

use_demo = st.toggle("Use synthetic demo data", value=True)

bank_text = SAMPLE_BANK if use_demo else None
internal_text = SAMPLE_INTERNAL if use_demo else None

if not use_demo:
    left, right = st.columns(2)
    with left:
        bank_file = st.file_uploader("Bank / Custodian CSV", type=["csv"])
    with right:
        internal_file = st.file_uploader("Internal Ledger CSV", type=["csv"])

    if bank_file:
        bank_text = bank_file.getvalue().decode("utf-8")
    if internal_file:
        internal_text = internal_file.getvalue().decode("utf-8")

if bank_text and internal_text:
    left, right = st.columns(2)

    with left:
        st.subheader("Bank / Custodian")
        st.dataframe(
            df_from_text(bank_text),
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("Internal Ledger")
        st.dataframe(
            df_from_text(internal_text),
            use_container_width=True,
            hide_index=True,
        )

if st.button("🚀 Run ReconEdge Investigation", type="primary", use_container_width=True):
    if not os.getenv("DAYTONA_API_KEY"):
        st.error("Provide a Daytona API key in the sidebar.")
        st.stop()

    if not bank_text or not internal_text:
        st.error("Provide both datasets.")
        st.stop()

    with st.status("Running controlled investigation...", expanded=True) as status:
        st.write("Creating Daytona sandbox and executing deterministic reconciliation...")
        try:
            reconciliation = run_reconciliation_in_daytona(
                bank_text,
                internal_text,
                tolerance=tolerance,
            )
        except Exception as exc:
            status.update(label="Daytona execution failed", state="error")
            st.error(str(exc))
            st.stop()

        sandbox_meta = reconciliation.pop("sandbox")

        st.write("Building structured evidence...")
        evidence = build_evidence_package(
            reconciliation,
            currency=currency,
        )

        st.write("Scoring exception risk and materiality...")
        risks = score_all(
            evidence.exceptions,
            materiality_threshold=materiality,
        )

        ai_response = None
        verification = None

        if use_ai:
            st.write("Sending one batched evidence package to the AI reasoner...")
            try:
                ai_response = reason_with_ai(evidence, risks)
                verification = verify_ai_response(evidence, ai_response)
            except Exception as exc:
                st.warning(f"AI reasoning unavailable: {exc}")

        status.update(label="Investigation complete", state="complete")

    st.subheader("Execution trace")
    a, b, c = st.columns(3)
    a.metric("Sandbox ID", sandbox_meta["sandbox_id"] or "n/a")
    b.metric("Runtime", f'{sandbox_meta["runtime_seconds"]:.2f}s')
    c.metric("Cleanup", "Deleted ✅" if sandbox_meta["deleted"] else "Check cleanup")

    st.subheader("Financial reconciliation")
    s = evidence.summary
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Reviewed", s.transactions_reviewed)
    m2.metric("Matches", s.match_count)
    m3.metric("Exceptions", s.exception_count)
    m4.metric("Gross exposure", f"{currency} {s.gross_exception_exposure:,.2f}")

    n1, n2, n3 = st.columns(3)
    n1.metric("Match rate", f"{s.match_rate:.2f}%")
    n2.metric("Exception rate", f"{s.exception_rate:.2f}%")
    n3.metric("Net discrepancy", f"{currency} {s.net_discrepancy:+,.2f}")

    risk_by_tx = {r.transaction_id: r for r in risks}
    ai_by_tx = (
        {x.transaction_id: x for x in ai_response.exceptions}
        if ai_response
        else {}
    )

    st.subheader("Exception investigation")

    for exception in evidence.exceptions:
        risk = risk_by_tx[exception.transaction_id]

        with st.expander(
            f"⚠️ {exception.transaction_id} — "
            f"{exception.classification} — {risk.band} ({risk.score:.2f})",
            expanded=True,
        ):
            left, right = st.columns(2)

            with left:
                st.markdown("**Deterministic evidence**")
                for fact in exception.evidence:
                    st.write("•", fact)

                st.write(
                    f"Signed difference: {currency} "
                    f"{exception.signed_difference:+,.2f}"
                )
                st.write(
                    f"Absolute difference: {currency} "
                    f"{exception.absolute_difference:,.2f}"
                )
                st.write(f"Variance: {exception.variance_pct:.2f}%")

                st.markdown("**Risk components**")
                st.json(risk.components)

            with right:
                ai_item = ai_by_tx.get(exception.transaction_id)

                if ai_item:
                    st.markdown("**AI investigation**")
                    st.write(ai_item.summary)

                    for h in ai_item.hypotheses:
                        st.write(
                            f"**#{h.rank} {h.cause}** "
                            f"— confidence {h.confidence:.0%}"
                        )
                        for ev in h.supporting_evidence:
                            st.caption(f"• {ev}")

                    st.markdown("**Recommended checks**")
                    for check in ai_item.recommended_checks:
                        st.write("→", check)

                    st.markdown("**Escalation guidance**")
                    st.write(ai_item.escalation)
                else:
                    st.info(
                        "AI reasoning not enabled. Deterministic evidence and "
                        "risk scoring are still available."
                    )

    if verification:
        st.subheader("AI verification")
        if verification.valid:
            st.success("AI response passed structural verification.")
        else:
            st.error("AI response failed verification.")
            for issue in verification.issues:
                st.write("•", issue)

    st.caption(
        f"Investigation ID: {evidence.investigation_id} | "
        "Daytona = execution facts | AI = bounded interpretation"
    )
