"""Claim extraction with Claude, plus deterministic fallback parsing."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential


CLAIM_TYPES = [
    "financial",
    "operational_efficiency",
    "workforce",
    "product_launch",
    "partnership",
    "legal_regulatory",
    "executive_strategy",
    "ai_infrastructure",
    "other",
]


@dataclass
class ExtractedClaim:
    claim_id: str
    brief_section: str
    claim: str
    claim_type: str
    entities: list[str]
    date_reference: str | None = None
    search_queries: list[str] | None = None


def _extract_json_array(text: str) -> list[dict[str, Any]]:
    """Parse a JSON array even when the model includes surrounding prose."""

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, list):
        raise ValueError("Expected a JSON array of claims.")
    return parsed


def _normalize_claims(items: list[dict[str, Any]], max_claims: int) -> list[ExtractedClaim]:
    claims = []
    for index, item in enumerate(items[:max_claims], start=1):
        claim_text = str(item.get("claim") or item.get("extracted_claim") or "").strip()
        if not claim_text:
            continue
        claim_type = str(item.get("claim_type") or "other").strip().lower()
        if claim_type not in CLAIM_TYPES:
            claim_type = "other"
        entities = item.get("entities") or []
        if isinstance(entities, str):
            entities = [entity.strip() for entity in entities.split(",") if entity.strip()]
        queries = item.get("search_queries") or []
        if isinstance(queries, str):
            queries = [queries]
        claims.append(
            ExtractedClaim(
                claim_id=item.get("claim_id") or f"C{index:03d}",
                brief_section=str(item.get("brief_section") or item.get("section") or "Unknown").strip(),
                claim=claim_text,
                claim_type=claim_type,
                entities=[str(entity).strip() for entity in entities if str(entity).strip()],
                date_reference=item.get("date_reference") or None,
                search_queries=[str(query).strip() for query in queries if str(query).strip()] or None,
            )
        )
    return claims


def fallback_extract_claims(sections: dict[str, str], max_claims: int = 8) -> list[ExtractedClaim]:
    """Deterministic fallback that extracts factual-looking bullets and sentences."""

    claims: list[ExtractedClaim] = []
    fact_pattern = re.compile(
        r"(\$?\d[\d,]*(?:\.\d+)?\s?(?:billion|million|%|percent)?|reported|announced|launched|partnered|served|invested|faces|positioned)",
        re.IGNORECASE,
    )
    for section, body in sections.items():
        candidates = []
        for line in body.splitlines():
            stripped = line.strip(" -*\t")
            if stripped:
                candidates.extend(re.split(r"(?<=[.!?])\s+", stripped))
        for candidate in candidates:
            text = candidate.strip()
            if len(text) < 30 or not fact_pattern.search(text):
                continue
            claim_id = f"C{len(claims) + 1:03d}"
            claims.append(
                ExtractedClaim(
                    claim_id=claim_id,
                    brief_section=section,
                    claim=text,
                    claim_type="other",
                    entities=[],
                    date_reference=None,
                    search_queries=[text],
                )
            )
            if len(claims) >= max_claims:
                return claims
    return claims


class ClaudeClaimExtractor:
    """Extract discrete factual claims from a text brief using Anthropic Claude."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Set ANTHROPIC_API_KEY before running Claude claim extraction.")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.client = Anthropic(api_key=self.api_key)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=12), stop=stop_after_attempt(3))
    def extract(self, raw_text: str, sections: dict[str, str], max_claims: int = 8) -> list[ExtractedClaim]:
        """Return structured factual claims and search-ready query suggestions."""

        prompt = f"""
You are extracting verifiable factual claims from a text-based AI Radar brief.

Return only a JSON array. Each item must include:
claim_id, brief_section, claim, claim_type, entities, date_reference, search_queries.

Allowed claim_type values: {", ".join(CLAIM_TYPES)}.

Rules:
- Extract discrete claims that can be checked against public sources.
- Do not include opinions unless they contain a factual assertion.
- Prefer financial, membership, product, partnership, regulatory, executive, and AI infrastructure claims.
- Provide 2 or 3 search_queries that include the company/entity and likely primary-source terms.
- Do not invent facts not present in the brief.
- Limit to {max_claims} highest-value claims.

Known section names: {list(sections.keys())}

Brief:
{raw_text}
"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        return _normalize_claims(_extract_json_array(text), max_claims=max_claims)


def claims_as_dicts(claims: list[ExtractedClaim]) -> list[dict[str, Any]]:
    """Serialize claim objects for notebook display or CrewAI task context."""

    return [asdict(claim) for claim in claims]
