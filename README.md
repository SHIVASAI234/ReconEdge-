[README (1).md](https://github.com/user-attachments/files/31598085/README.1.md)
ReconEdge is an intelligent financial reconciliation and exception-resolution platform designed to move financial operations beyond simple break detection and toward evidence-driven investigation.

The name ReconEdge combines two ideas:

Recon comes from reconciliation — the process of comparing financial records across systems, ledgers, custodians, banks, and operational platforms to ensure that transactions, balances, and statuses agree.

Edge represents the intelligence layer that goes beyond traditional reconciliation. Instead of only identifying that two records are different, ReconEdge aims to provide the additional context needed to understand why the break occurred, how material it is, what evidence supports it, and what action should follow next.

The core idea behind ReconEdge emerged from a common weakness in financial operations workflows:

Traditional reconciliation systems are often good at finding mismatches, but they still leave analysts with the harder task of investigating those mismatches manually.

A typical reconciliation engine may tell an operations analyst:
**Intelligent reconciliation for modern financial operations.**

> **Detect. Quantify. Investigate. Resolve.**

ReconEdge is a controlled financial investigation system that combines:

- deterministic reconciliation calculations,
- isolated Daytona sandbox execution,
- structured evidence generation,
- AI-powered root-cause reasoning,
- materiality and risk scoring,
- confidence-based decision gates,
- and human oversight for material financial decisions.

The objective is not merely to detect that two records do not match.

ReconEdge is designed to answer:

1. **What broke?**
2. **Where did it break?**
3. **How much is affected?**
4. **What evidence supports the exception?**
5. **What are the most plausible root causes?**
6. **How material is the break?**
7. **What should an analyst investigate next?**
8. **When should the issue be escalated?**

---

# 1. Problem Statement

Financial institutions process large volumes of transactions across systems that do not always update at the same time or interpret financial events identically.

A single event may flow through:

```text
Trading / Source System
        ↓
Internal Ledger
        ↓
Operations Platform
        ↓
Bank / Custodian
        ↓
Settlement Infrastructure
```

These systems can diverge because of:

- timing differences,
- delayed interfaces,
- failed bookings,
- fees,
- partial settlements,
- amendments,
- rejected or cancelled transactions,
- stale lifecycle statuses,
- duplicated records,
- missing records,
- or incorrect monetary values.

Traditional reconciliation systems are often effective at answering:

```text
Do these records match?
```

But operational teams still need to answer:

```text
Why do they not match?
How large is the difference?
Which side is likely wrong?
What evidence supports the exception?
Is it material?
What should be checked next?
Does it need escalation?
```

That investigation is where a significant amount of manual effort remains.

---

## 1.1 The Operational Gap

A conventional workflow often looks like:

```text
Data
 ↓
Compare
 ↓
Break detected
 ↓
Human investigation
 ↓
Root cause
 ↓
Action
```

The system stops at:

```text
BREAK DETECTED
```

while the expensive part remains:

```text
WHY?
WHAT EVIDENCE?
HOW SERIOUS?
WHAT NEXT?
```

ReconEdge focuses on this gap.

> **ReconEdge is not just a matching engine. It is an investigation layer that sits between reconciliation detection and human resolution.**

---

## 1.2 Example: Amount Mismatch

```text
Bank / Custodian
TX002 → €8,500 → Settled

Internal Ledger
TX002 → €8,000 → Settled
```

The obvious fact is:

```text
Difference = €500
```

But the operational questions are deeper:

- Was a fee applied externally?
- Was the internal booking incorrect?
- Was the transaction amended?
- Was there a partial settlement?
- Is the difference material?
- Does the transaction require escalation?
- What supporting records should be checked?

ReconEdge separates these two responsibilities:

```text
Deterministic code → determines the facts
AI reasoning       → interprets the facts
```

---

# 2. Product Thesis

ReconEdge transforms:

```text
"These records do not match."
```

into:

```text
WHAT happened?
        ↓
AMOUNT_MISMATCH

WHERE?
        ↓
TX002

HOW MUCH?
        ↓
€500

HOW MATERIAL?
        ↓
5.88% variance

WHAT IS THE EVIDENCE?
        ↓
Bank €8,500
Internal €8,000

WHY MIGHT IT HAVE HAPPENED?
        ↓
Ranked root-cause hypotheses

WHAT SHOULD HAPPEN NEXT?
        ↓
Evidence-backed investigation steps
```

The product workflow is:

```text
DETECT
   ↓
QUANTIFY
   ↓
CLASSIFY
   ↓
BUILD EVIDENCE
   ↓
ASSESS RISK
   ↓
REASON
   ↓
VERIFY
   ↓
RECOMMEND
```

---

# 3. End-to-End Architecture

```text
User / API Request
        ↓
Intake + Context Builder
        ↓
Schema & Data Quality Validator
        ↓
Investigation Planner
        ↓
Policy / Guardrail Gate
        ↓
Daytona Sandbox Orchestrator
        ↓
Deterministic Reconciliation Engine
        ↓
Evidence Builder
        ↓
Materiality & Risk Engine
        ↓
AI Root-Cause Reasoner
        ↓
Evidence Verifier / Critic
        ↓
Confidence Gate
   ↙        ↓        ↘
Retry   Human Review   Continue
        ↓
Recommended Action Engine
        ↓
Investigation Report
        ↓
Audit + Data Lineage
        ↓
Feedback / Learning Loop
```

---

# 4. Calculation & Reconciliation Engine

The calculation layer is deterministic and executes inside a Daytona sandbox.

The AI model does **not** decide whether two amounts are equal and does **not** replace arithmetic logic.

This is intentional:

> **Financial facts should be computed deterministically before they are interpreted probabilistically.**

---

## 4.1 Transaction Universe

Let:

- \(B\) = set of transaction IDs in the bank/custodian dataset
- \(I\) = set of transaction IDs in the internal ledger

The complete transaction universe is:

\[
U = B \cup I
\]

Every transaction in \(U\) is evaluated exactly once.

For each transaction \(t\):

```text
bank_exists(t)
internal_exists(t)
bank_amount(t)
internal_amount(t)
bank_status(t)
internal_status(t)
```

---

## 4.2 Presence Checks

Define:

\[
P_B(t) =
\begin{cases}
1 & \text{if transaction exists externally}\\
0 & \text{otherwise}
\end{cases}
\]

\[
P_I(t) =
\begin{cases}
1 & \text{if transaction exists internally}\\
0 & \text{otherwise}
\end{cases}
\]

Classification:

```text
P_B = 1 and P_I = 1 → continue comparison
P_B = 1 and P_I = 0 → MISSING_INTERNAL
P_B = 0 and P_I = 1 → MISSING_BANK
```

Missing records are treated as explicit financial exceptions.

---

## 4.3 Signed Amount Difference

When both records exist:

\[
\Delta_t = A_B(t) - A_I(t)
\]

Where:

- \(A_B(t)\) = bank/custodian amount
- \(A_I(t)\) = internal amount
- \(\Delta_t\) = signed discrepancy

Example:

```text
Bank amount:     €8,500
Internal amount: €8,000
```

\[
\Delta = 8500 - 8000 = +500
\]

Interpretation:

```text
Positive → external value exceeds internal value
Negative → internal value exceeds external value
```

---

## 4.4 Absolute Exception Exposure

The absolute discrepancy is:

\[
E_t = |\Delta_t|
\]

This measures magnitude while ignoring direction.

For a missing transaction, the absent side can be represented as zero **for exception-exposure calculation only**.

Example:

```text
Bank TX003:     €2,400
Internal TX003: absent
```

\[
\Delta = 2400 - 0 = 2400
\]

\[
E = |2400| = 2400
\]

This does **not** imply a confirmed €2,400 financial loss.

It means €2,400 of transaction value is associated with that reconciliation exception.

---

## 4.5 Gross Exception Exposure

Across all transactions:

\[
GrossExposure = \sum_{t \in U} |\Delta_t|
\]

For the synthetic demo dataset:

```text
TX001:      0
TX002:    500
TX003:  2,400
TX004:  2,400
TX005:      0
TX006:      0
----------------
Gross:  €5,300
```

\[
GrossExposure = 500 + 2400 + 2400 = 5300
\]

This metric answers:

> How much transaction value is associated with monetary reconciliation exceptions?

---

## 4.6 Net Discrepancy

Gross exposure loses direction.

ReconEdge therefore also supports:

\[
NetDiscrepancy = \sum_{t \in U} \Delta_t
\]

For the sample dataset:

```text
TX002:  +€500
TX003: +€2,400
TX004: -€2,400
```

\[
NetDiscrepancy = 500
\]

So:

```text
Gross exception exposure = €5,300
Net discrepancy          = +€500
```

These measure different things:

- **Gross exposure** = total exception magnitude
- **Net discrepancy** = directional imbalance

---

## 4.7 Percentage Variance

For transactions present in both systems:

\[
VariancePct_t =
\frac{|A_B(t)-A_I(t)|}
{\max(|A_B(t)|, |A_I(t)|)}
\times 100
\]

For:

```text
€8,500 vs €8,000
```

\[
VariancePct =
\frac{500}{8500}\times100
\approx 5.88\%
\]

This provides relative materiality.

---

## 4.8 Status Comparison

Amounts may match while the lifecycle status differs.

Define:

\[
S_t =
\begin{cases}
0 & \text{if statuses match}\\
1 & \text{if statuses differ}
\end{cases}
\]

Example:

```text
Bank:     settled
Internal: pending
```

Produces:

```text
STATUS_MISMATCH
```

with zero monetary discrepancy but non-zero operational significance.

---

## 4.9 Exception Classification Logic

The MVP applies a deterministic hierarchy:

```text
IF external record missing:
    MISSING_BANK

ELSE IF internal record missing:
    MISSING_INTERNAL

ELSE IF amounts differ:
    AMOUNT_MISMATCH

ELSE IF statuses differ:
    STATUS_MISMATCH

ELSE:
    MATCH
```

---

## 4.10 Match Rate

\[
MatchRate =
\frac{MatchedTransactions}
{TransactionsReviewed}
\times100
\]

For the sample:

\[
MatchRate = \frac{2}{6}\times100 = 33.33\%
\]

---

## 4.11 Exception Rate

\[
ExceptionRate =
\frac{ExceptionTransactions}
{TransactionsReviewed}
\times100
\]

For the sample:

\[
ExceptionRate = \frac{4}{6}\times100 = 66.67\%
\]

The sample intentionally contains a high exception rate so multiple exception types can be demonstrated.

---

# 5. Agent Flow — Deep Orchestration Architecture

ReconEdge should not behave like a single prompt that receives files and generates an answer.

It is designed as a **stateful financial investigation workflow**.

Core principle:

> **Facts are computed. Hypotheses are reasoned. Decisions are gated. Evidence is preserved.**

---

## 5.1 Stage 1 — Intake & Context Builder

The first component converts the request into a standard investigation object.

Possible inputs:

```text
bank/custodian file
internal ledger file
account
currency
business date
reconciliation type
tolerance
materiality threshold
analyst notes
historical exception context
```

Example:

```json
{
  "investigation_id": "INV-2026-08-29-00017",
  "reconciliation_type": "transaction",
  "business_date": "2026-08-29",
  "currency": "EUR",
  "tolerance": 0.01,
  "materiality_threshold": 1000,
  "status": "RECEIVED"
}
```

---

## 5.2 Stage 2 — Schema & Data Quality Validator

Before Daytona or AI is used, ReconEdge validates:

```text
required columns
transaction IDs
numeric amount fields
duplicate IDs
known statuses
currency formats
date formats
empty datasets
unexpected delimiters
invalid decimals
negative values
```

Example:

```json
{
  "schema_valid": true,
  "bank_rows": 5,
  "internal_rows": 5,
  "duplicate_ids": [],
  "invalid_amount_rows": [],
  "warnings": []
}
```

If validation fails, the workflow stops early.

---

## 5.3 Stage 3 — AI Investigation Planner

The planner does not calculate financial values.

Its role is to decide:

> Which analytical checks should run?

Example output:

```json
{
  "checks": [
    "presence_check",
    "amount_check",
    "status_check"
  ],
  "execution_order": [
    "presence_check",
    "amount_check",
    "status_check"
  ],
  "requires_sandbox": true
}
```

Future planner capabilities may include:

```text
duplicate detection
date-window matching
FX normalisation
many-to-one matching
position comparison
price comparison
cash balance comparison
historical-pattern analysis
```

For the hackathon MVP, this planner can remain fixed.

---

## 5.4 Stage 4 — Policy & Guardrail Gate

Before execution, ReconEdge checks:

```text
dataset size
file types
execution timeout
sandbox limit
network requirements
unsupported operations
sensitive-data restrictions
generated-code permissions
```

Example:

```json
{
  "approved": true,
  "sandbox_limit": 1,
  "timeout_seconds": 60,
  "network_access": false,
  "reason": "Standard transaction reconciliation"
}
```

---

## 5.5 Stage 5 — Daytona Sandbox Orchestrator

The Daytona layer manages:

```text
CREATE
  ↓
CONFIGURE
  ↓
LOAD INPUT
  ↓
EXECUTE
  ↓
CAPTURE OUTPUT
  ↓
VERIFY EXIT STATUS
  ↓
DELETE
```

For the MVP:

```text
1 investigation = 1 Daytona sandbox
```

Example lifecycle record:

```json
{
  "sandbox_id": "sbx_...",
  "runtime_ms": 842,
  "exit_code": 0,
  "cleanup_status": "DELETED"
}
```

Cleanup should always run in a `finally` block.

---

## 5.6 Stage 6 — Deterministic Reconciliation Engine

The engine performs:

```text
transaction-universe construction
presence checks
amount comparison
signed difference
absolute difference
percentage variance
status comparison
exception classification
gross exposure
net discrepancy
match rate
exception rate
```

Example:

```json
{
  "transaction_id": "TX002",
  "classification": "AMOUNT_MISMATCH",
  "bank_amount": 8500,
  "internal_amount": 8000,
  "signed_difference": 500,
  "absolute_difference": 500,
  "variance_pct": 5.88,
  "bank_status": "settled",
  "internal_status": "settled"
}
```

The AI must not overwrite these fields.

---

## 5.7 Stage 7 — Evidence Builder

The evidence builder converts calculations into a compact investigation object.

Example:

```json
{
  "exception_id": "EXC-TX002",
  "observed_facts": [
    "Transaction exists in both systems",
    "Bank amount = 8500 EUR",
    "Internal amount = 8000 EUR",
    "Difference = +500 EUR",
    "Variance = 5.88%",
    "Both statuses = settled"
  ],
  "classification": "AMOUNT_MISMATCH",
  "data_sources": [
    "bank.csv",
    "internal.csv"
  ]
}
```

The AI reasons over this evidence rather than raw spreadsheets.

---

## 5.8 Stage 8 — Materiality & Risk Scoring

ReconEdge prioritises exceptions rather than treating every break equally.

A simple scoring model:

\[
RiskScore =
w_1 M +
w_2 V +
w_3 T +
w_4 A
\]

Where:

- \(M\) = monetary materiality
- \(V\) = percentage variance severity
- \(T\) = exception-type severity
- \(A\) = ageing or urgency

Example:

```text
Monetary materiality      0.70
Variance severity         0.55
Exception-type severity   0.80
Ageing                    0.20
```

Weights:

```text
0.40
0.20
0.30
0.10
```

Then:

\[
RiskScore =
0.40(0.70)
+
0.20(0.55)
+
0.30(0.80)
+
0.10(0.20)
\]

\[
RiskScore = 0.65
\]

Possible bands:

```text
0.00–0.39  LOW
0.40–0.69  MEDIUM
0.70–1.00  HIGH
```

---

## 5.9 Stage 9 — AI Root-Cause Reasoner

The reasoner receives:

```text
deterministic facts
exception classification
risk score
business context
optional historical context
```

Its output should contain ranked hypotheses.

Example:

```json
{
  "exception_id": "EXC-TX002",
  "summary": "The external value exceeds the internal ledger value by EUR 500.",
  "hypotheses": [
    {
      "rank": 1,
      "cause": "Fee or adjustment not reflected internally",
      "confidence": 0.62,
      "supporting_evidence": [
        "Both records exist",
        "Statuses match",
        "Difference is monetary only"
      ]
    },
    {
      "rank": 2,
      "cause": "Incorrect internal booking amount",
      "confidence": 0.25
    },
    {
      "rank": 3,
      "cause": "Amendment or partial settlement",
      "confidence": 0.13
    }
  ]
}
```

Confidence is a model-generated reasoning indicator, not a statistical probability.

---

## 5.10 Stage 10 — Evidence Verifier / Critic

The reasoner's output should not automatically become the final answer.

The verifier checks:

```text
Did AI invent an amount?
Did it contradict deterministic evidence?
Did it claim certainty without proof?
Did it recommend unsupported actions?
Did it confuse hypothesis with fact?
```

Example:

```json
{
  "valid": true,
  "unsupported_claims": [],
  "contradictions": [],
  "requires_retry": false
}
```

If invalid:

```text
AI Reasoner
    ↓
Verifier rejects unsupported claim
    ↓
Reasoner retries with stricter constraints
```

---

## 5.11 Stage 11 — Confidence Gate

Example logic:

```text
Confidence ≥ 0.75
→ recommendation can proceed

0.45 ≤ Confidence < 0.75
→ recommendation + analyst review

Confidence < 0.45
→ collect more evidence / re-plan
```

This prevents weak AI reasoning from appearing as a final conclusion.

---

## 5.12 Stage 12 — Human-in-the-Loop Review

Human review may be required when:

```text
break value exceeds threshold
AI confidence is low
evidence conflicts
exception type is unknown
multiple causes are plausible
the same break repeatedly fails
materiality threshold is exceeded
```

Possible analyst actions:

```text
APPROVE hypothesis
REJECT hypothesis
REQUEST MORE DATA
ESCALATE
MARK RESOLVED
```

---

## 5.13 Stage 13 — Recommended Action Engine

Example:

```json
{
  "recommended_actions": [
    {
      "priority": 1,
      "action": "Review transaction confirmation",
      "purpose": "Confirm expected contractual amount"
    },
    {
      "priority": 2,
      "action": "Review fee and adjustment fields",
      "purpose": "Determine whether EUR 500 is a valid adjustment"
    },
    {
      "priority": 3,
      "action": "Validate internal ledger posting",
      "purpose": "Determine whether the internal record requires correction"
    }
  ]
}
```

The MVP recommends actions but does not alter financial records.

---

## 5.14 Stage 14 — Investigation Report Generator

Example report:

```text
INVESTIGATION ID
INV-2026-08-29-00017

TRANSACTION
TX002

EXCEPTION
AMOUNT_MISMATCH

RISK
MEDIUM — 0.65

FACTS
Bank: €8,500
Internal: €8,000
Difference: +€500
Variance: 5.88%

LIKELY CAUSE
Fee or adjustment not reflected internally

CONFIDENCE
62%

NEXT ACTION
Review confirmation and fee/adjustment fields

SANDBOX
Executed successfully
Sandbox deleted

STATUS
ANALYST REVIEW REQUIRED
```

---

## 5.15 Stage 15 — Audit & Data Lineage

Every investigation can capture:

```text
investigation ID
input hashes
schema validation result
planner output
sandbox ID
execution time
calculation output
AI model
prompt version
AI response
verifier result
risk score
human decision
final status
```

---

## 5.16 Stage 16 — Feedback & Learning Loop

Once an analyst confirms the real cause:

```json
{
  "exception_type": "AMOUNT_MISMATCH",
  "ai_top_hypothesis": "Fee or adjustment",
  "confirmed_root_cause": "Custody fee",
  "ai_prediction_correct": true
}
```

This can later improve:

```text
prompt quality
hypothesis ranking
exception heuristics
confidence calibration
recurring-break detection
model evaluation
```

---

# 6. Stateful Investigation Model

ReconEdge should maintain one state object across the workflow.

```json
{
  "investigation_id": "INV-2026-08-29-00017",
  "stage": "AI_REASONING",
  "input_validation": {},
  "plan": {},
  "sandbox": {},
  "calculations": {},
  "exceptions": [],
  "risk_scores": {},
  "reasoning": {},
  "verification": {},
  "human_review": {},
  "final_report": {}
}
```

Each stage should update only its own section.

---

# 7. Daytona Integration

Daytona is the isolated execution layer for analytical work.

It is not just hosting the UI.

```text
ReconEdge UI
     ↓
Investigation Controller
     ↓
CREATE Daytona sandbox
     ↓
Inject input + reconciliation job
     ↓
Execute deterministic calculations
     ↓
Return structured JSON
     ↓
DELETE sandbox
```

---

## 7.1 Why Daytona?

Financial investigation workflows benefit from:

- isolated execution,
- disposable compute,
- reproducible runs,
- controlled lifecycle,
- separation of UI and execution,
- future support for generated code,
- future support for parallel investigations.

For the MVP:

> **One investigation = one Daytona sandbox.**

---

## 7.2 Sandbox Execution Contract

Input:

```json
{
  "bank_csv": "...",
  "internal_csv": "..."
}
```

Output:

```json
{
  "transactions_reviewed": 6,
  "match_count": 2,
  "exception_count": 4,
  "gross_exception_exposure": 5300.0,
  "net_discrepancy": 500.0,
  "exceptions": [
    {
      "transaction_id": "TX002",
      "type": "AMOUNT_MISMATCH",
      "bank_amount": 8500.0,
      "internal_amount": 8000.0,
      "signed_difference": 500.0,
      "absolute_difference": 500.0,
      "variance_pct": 5.88,
      "bank_status": "settled",
      "internal_status": "settled"
    }
  ]
}
```

---

# 8. AI API Integration

ReconEdge uses an evidence-first architecture.

```text
RAW DATA
   ↓
DAYTONA
   ↓
DETERMINISTIC CALCULATIONS
   ↓
STRUCTURED EVIDENCE
   ↓
AI API
   ↓
ROOT-CAUSE HYPOTHESES
   ↓
RECOMMENDED ACTIONS
```

The AI does not independently recalculate financial facts.

---

## 8.1 AI Responsibilities

### Daytona / deterministic code determines:

- presence or absence of records
- amount equality
- signed difference
- absolute exposure
- percentage variance
- status mismatch
- gross exception exposure
- net discrepancy
- structured evidence

### AI API determines:

- plausible root-cause hypotheses
- hypothesis ranking
- reasoning explanation
- investigation sequence
- recommended next checks
- escalation guidance

---

## 8.2 AI Input Contract

Example:

```json
{
  "transaction_id": "TX002",
  "exception_type": "AMOUNT_MISMATCH",
  "bank_amount": 8500,
  "internal_amount": 8000,
  "signed_difference": 500,
  "absolute_difference": 500,
  "variance_pct": 5.88,
  "bank_status": "settled",
  "internal_status": "settled",
  "risk_score": 0.65
}
```

---

## 8.3 AI Output Contract

```json
{
  "transaction_id": "TX002",
  "summary": "External and internal records differ by EUR 500.",
  "root_causes": [
    {
      "hypothesis": "Fee or adjustment not reflected internally",
      "confidence": 0.62
    },
    {
      "hypothesis": "Incorrect internal booking amount",
      "confidence": 0.25
    },
    {
      "hypothesis": "Partial settlement or amendment",
      "confidence": 0.13
    }
  ],
  "recommended_checks": [
    "Compare transaction confirmation",
    "Review fee and adjustment fields",
    "Check amendment history",
    "Validate internal posting"
  ],
  "escalation": "Escalate if source confirmation supports EUR 8,500 and no valid adjustment explains the difference."
}
```

---

## 8.4 AI Guardrails

The AI should be instructed to:

- use only supplied evidence,
- never invent transaction values,
- never modify supplied calculations,
- distinguish facts from hypotheses,
- return ranked hypotheses,
- state when evidence is insufficient,
- recommend investigation steps rather than executing financial actions,
- return structured JSON only.

Example system instruction:

```text
You are a financial operations investigation assistant.

You receive deterministic reconciliation evidence produced by code.

Never alter or recalculate supplied numeric facts.

Separate observed evidence from hypotheses.

For each exception:
1. summarise the observed break,
2. rank plausible operational root causes,
3. explain what evidence supports each hypothesis,
4. recommend the next checks,
5. state whether escalation may be required.

Do not claim a root cause is confirmed unless the evidence proves it.

Return valid JSON only.
```

---

# 9. AI API Usage Strategy

For the MVP:

```text
1 Daytona sandbox
+
1 batched AI API request
+
1 investigation report
```

Avoid:

```text
1 AI call per transaction
```

Instead, bundle exceptions into one request.

Example:

```json
{
  "investigation_id": "run-001",
  "summary": {
    "transactions_reviewed": 6,
    "exceptions": 4,
    "gross_exception_exposure": 5300,
    "net_discrepancy": 500
  },
  "exception_evidence": [
    "...",
    "...",
    "...",
    "..."
  ]
}
```

Benefits:

- lower API usage,
- lower latency,
- consistent reasoning,
- easier JSON parsing,
- simpler architecture.

---

# 10. Failure & Retry Strategy

```text
Schema error
→ stop before sandbox

Sandbox creation failure
→ retry once
→ fail gracefully

Sandbox timeout
→ delete sandbox
→ return technical failure

Malformed AI JSON
→ retry with stricter format instruction

Unsupported AI claim
→ verifier rejects
→ re-run reasoner

Low confidence
→ human review

Repeated failure
→ stop
```

Every loop should have:

```text
max retries
timeout
explicit stopping condition
```

---

# 11. Demo Dataset

## Bank / Custodian

```csv
transaction_id,amount,status
TX001,5000,settled
TX002,8500,settled
TX003,2400,settled
TX005,12000,settled
TX006,1750,settled
```

## Internal Ledger

```csv
transaction_id,amount,status
TX001,5000,settled
TX002,8000,settled
TX004,2400,pending
TX005,12000,settled
TX006,1750,pending
```

---

## 11.1 Expected Results

| Transaction | Classification |
|---|---|
| TX001 | MATCH |
| TX002 | AMOUNT_MISMATCH |
| TX003 | MISSING_INTERNAL |
| TX004 | MISSING_BANK |
| TX005 | MATCH |
| TX006 | STATUS_MISMATCH |

Expected metrics:

```text
Transactions reviewed:      6
Matches:                    2
Exceptions:                 4
Match rate:             33.33%
Exception rate:         66.67%
Gross exception exposure: €5,300
Net discrepancy:          +€500
```

---

# 12. Product UI

The ReconEdge UI should display:

```text
Investigation ID
Daytona sandbox ID
Sandbox runtime
Cleanup status

Transactions reviewed
Matches
Exceptions
Match rate
Exception rate
Gross exposure
Net discrepancy

Exception type
Risk score
Bank amount
Internal amount
Signed difference
Absolute difference
Variance %
Bank status
Internal status

Observed evidence
Root-cause hypotheses
AI confidence
Recommended checks
Escalation guidance
Final investigation status
```

---

# 13. Repository Structure

Target MVP structure:

```text
reconedge/
│
├── app.py
├── daytona_runner.py
├── reconciliation_engine.py
├── evidence_builder.py
├── risk_engine.py
├── ai_reasoner.py
├── verifier.py
├── models.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Possible later structure:

```text
reconedge/
│
├── app/
│   └── streamlit_app.py
│
├── agents/
│   ├── planner.py
│   ├── reasoner.py
│   └── verifier.py
│
├── engine/
│   ├── reconciliation.py
│   ├── evidence.py
│   └── risk.py
│
├── sandbox/
│   └── daytona_client.py
│
├── schemas/
│   └── investigation.py
│
├── tests/
│   ├── test_reconciliation.py
│   ├── test_risk.py
│   └── test_reasoner.py
│
└── README.md
```

---

# 14. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Language | Python |
| Data Processing | Pandas / Python |
| Sandboxed Compute | Daytona |
| AI Reasoning | AI API / LLM |
| Structured Output | JSON |
| Version Control | GitHub |

---

# 15. Installation

## 15.1 Clone

```bash
git clone https://github.com/YOUR_USERNAME/reconedge.git
cd reconedge
```

## 15.2 Install

```bash
python3 -m pip install -r requirements.txt
```

## 15.3 Daytona API Key

Either use a secure environment variable:

```bash
export DAYTONA_API_KEY="YOUR_DAYTONA_API_KEY"
```

or enter it into a password field in the Streamlit UI.

Never commit a real API key.

---

## 15.4 AI API Key

Use the relevant provider-specific environment variable, for example:

```bash
export AI_API_KEY="YOUR_AI_API_KEY"
```

The exact provider can remain configurable.

---

## 15.5 Run

```bash
streamlit run app.py --server.address 0.0.0.0
```

If using GitHub Codespaces, open the forwarded Streamlit port.

---

# 16. Security Principles

ReconEdge should follow these principles:

## Isolation

Analytical execution runs inside a disposable Daytona sandbox.

## Minimal Persistence

The MVP should avoid intentionally persisting uploaded financial datasets.

## Cleanup

Sandbox deletion should occur after every investigation.

## Secrets

API keys must not be committed.

## Evidence Before AI

AI receives structured evidence instead of being trusted to perform reconciliation arithmetic.

## Human Oversight

Material financial decisions remain subject to analyst review.

## Synthetic Data

Hackathon demonstrations should use synthetic data rather than confidential employer or client information.

---

# 17. Auditability

A production investigation record should preserve:

```text
investigation ID
input hashes
input metadata
validation result
planner output
sandbox ID
runtime
calculation results
risk score
AI provider/model
prompt version
AI response
verifier result
human review
final status
timestamps
```

This enables:

```text
reproducibility
audit trail
model evaluation
control testing
incident review
governance
```

---

# 18. Hackathon MVP Scope

The full architecture is intentionally broader than what needs to be implemented immediately.

## Target Architecture

```text
Context Builder
      ↓
Validator
      ↓
AI Planner
      ↓
Policy Gate
      ↓
Daytona
      ↓
Calculation Engine
      ↓
Evidence Builder
      ↓
Risk Scorer
      ↓
AI Reasoner
      ↓
AI Verifier
      ↓
Confidence Gate
      ↓
Human Review
      ↓
Action Engine
      ↓
Report
      ↓
Audit + Feedback
```

## MVP Slice

```text
User
 ↓
Validator
 ↓
Fixed Planner
 ↓
ONE Daytona Sandbox
 ↓
Calculation Engine
 ↓
Evidence Builder
 ↓
Simple Risk Score
 ↓
ONE AI Reasoning Call
 ↓
Basic Verification
 ↓
Investigation Report
```

The MVP proves the core product loop without unnecessary infrastructure.

---

# 19. Demo Flow

A concise demo sequence:

```text
1. Select synthetic data
2. Show bank/custodian file
3. Show internal ledger
4. Start investigation
5. Create Daytona sandbox
6. Perform deterministic reconciliation
7. Return structured evidence
8. Calculate risk/materiality
9. Send exception package to AI
10. Show ranked root causes
11. Show recommended next action
12. Show sandbox deletion
13. Show final investigation report
```

The key presentation line:

> **Daytona determines the facts. AI interprets the facts. ReconEdge turns both into an operational investigation.**

---

# 20. Real-World Use Cases

Potential use cases include:

- trade reconciliation
- cash reconciliation
- position reconciliation
- settlement exception management
- transaction lifecycle monitoring
- NAV control investigation
- payment reconciliation
- custody operations
- middle-office exception management
- treasury operations

---

# 21. Future Calculation Capabilities

Future versions can add:

- tolerance-based matching
- configurable materiality thresholds
- date-window matching
- currency normalisation
- FX-adjusted comparisons
- duplicate detection
- fuzzy identifiers
- one-to-many matching
- many-to-one matching
- cash-balance reconciliation
- position-quantity reconciliation
- price reconciliation
- exception ageing
- recurring-break detection
- account-level aggregation
- counterparty-level aggregation
- historical root-cause patterns
- anomaly scoring
- exception concentration analysis

---

# 22. Future Agent Capabilities

Future agentic workflows may include:

```text
AI dynamically chooses checks
        ↓
Generates investigation code
        ↓
Daytona executes generated code safely
        ↓
Agent analyses evidence
        ↓
Agent requests additional evidence
        ↓
Verifier challenges conclusions
        ↓
Human approves resolution
```

Additional possibilities:

- multi-agent investigation
- historical exception retrieval
- policy-aware escalation
- generated audit reports
- automated evidence collection
- recurring-break detection
- dynamic root-cause playbooks
- confidence calibration
- model evaluation

---

# 23. Product Vision

ReconEdge can evolve into a broader:

> **Financial Operations Intelligence Layer**

Potential modules:

```text
ReconEdge
│
├── Cash Reconciliation
├── Position Reconciliation
├── Trade Reconciliation
├── Settlement Monitoring
├── NAV Controls
├── Corporate Actions
├── Exception Management
├── Risk Prioritisation
├── Audit Evidence
└── AI Investigation Agent
```

Longer-term architecture:

```text
Custodian
Bank
Ledger
OMS
Accounting Platform
Settlement System
        ↓
     ReconEdge
        ↓
Evidence Engine
        ↓
Risk Engine
        ↓
AI Investigation Agent
        ↓
Exception Prioritisation
        ↓
Human Review
        ↓
Resolution + Audit Trail
```

---

# 24. Core Product Principle

ReconEdge can be summarised as:

```text
AI decides what to investigate.
        ↓
Daytona provides isolated compute.
        ↓
Code determines what is mathematically true.
        ↓
Evidence is structured.
        ↓
Risk is quantified.
        ↓
AI explains what the facts may mean.
        ↓
A verifier checks the reasoning.
        ↓
A confidence gate controls autonomy.
        ↓
A human remains responsible for material financial decisions.
```

ReconEdge is not an AI chatbot for reconciliation.

It is a:

> **Controlled financial investigation system with sandboxed execution, deterministic evidence, bounded AI reasoning, risk-aware prioritisation, and auditable decision gates.**

---

# 25. Disclaimer

ReconEdge is currently a prototype intended for educational and demonstration purposes.

It does not provide:

- investment advice,
- accounting advice,
- legal advice,
- regulatory advice,
- or automated authority to alter financial records.

Do not use confidential employer, client, or production financial data in a hackathon environment.

---

# ReconEdge

### **Detect. Quantify. Investigate. Resolve.**

**Deterministic financial evidence. Sandboxed execution. AI-powered investigation.**
