# ReconEdge — Code Start

This package contains the first working architecture for ReconEdge.

## Run locally / in Codespaces

```bash
python3 -m pip install -r requirements.txt
pytest -q
streamlit run app.py --server.address 0.0.0.0
```

## MVP pipeline

```text
User
 ↓
Daytona sandbox
 ↓
Deterministic reconciliation
 ↓
Evidence builder
 ↓
Risk engine
 ↓
Optional AI reasoner
 ↓
Verifier
 ↓
Streamlit investigation report
```

The demo data is embedded in `app.py`, so no separate data folder is required.
