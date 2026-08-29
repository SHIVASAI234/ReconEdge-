from __future__ import annotations

import json
import os
import requests

from models import AIInvestigationResponse, EvidencePackage, RiskAssessment


SYSTEM_PROMPT = """You are ReconEdge, a financial operations investigation assistant.

You receive deterministic reconciliation evidence produced by code.

Rules:
1. Never alter or recalculate supplied numeric facts.
2. Separate observed facts from hypotheses.
3. Do not claim a root cause is confirmed unless the evidence proves it.
4. Rank plausible operational causes.
5. Recommend evidence-gathering checks, not financial record changes.
6. If evidence is insufficient, say so.
7. Return valid JSON only.

Required JSON shape:
{
  "investigation_id": "...",
  "exceptions": [
    {
      "transaction_id": "...",
      "summary": "...",
      "hypotheses": [
        {
          "rank": 1,
          "cause": "...",
          "confidence": 0.0,
          "supporting_evidence": ["..."]
        }
      ],
      "recommended_checks": ["..."],
      "escalation": "..."
    }
  ]
}
"""


def build_ai_payload(
    evidence: EvidencePackage,
    risks: list[RiskAssessment],
) -> dict:
    risk_by_tx = {r.transaction_id: r.model_dump() for r in risks}

    return {
        "investigation_id": evidence.investigation_id,
        "currency": evidence.currency,
        "summary": evidence.summary.model_dump(),
        "exceptions": [
            {
                **exception.model_dump(),
                "risk": risk_by_tx.get(exception.transaction_id),
            }
            for exception in evidence.exceptions
        ],
    }


def reason_with_ai(
    evidence: EvidencePackage,
    risks: list[RiskAssessment],
) -> AIInvestigationResponse:
    """
    Calls an OpenAI-compatible chat-completions endpoint.
    Configure AI_API_URL, AI_API_KEY, and AI_MODEL.
    """
    api_url = os.getenv("AI_API_URL", "").strip()
    api_key = os.getenv("AI_API_KEY", "").strip()
    model = os.getenv("AI_MODEL", "").strip()

    if not api_url or not api_key or not model:
        raise RuntimeError(
            "AI reasoning is not configured. Set AI_API_URL, AI_API_KEY, and AI_MODEL."
        )

    evidence_payload = build_ai_payload(evidence, risks)

    response = requests.post(
        api_url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(evidence_payload, indent=2),
                },
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Unexpected AI API response shape: {body}"
        ) from exc

    # Some providers may wrap JSON in markdown fences.
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()

    parsed = json.loads(content)
    return AIInvestigationResponse(**parsed)
