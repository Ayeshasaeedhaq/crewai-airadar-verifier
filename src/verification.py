"""Claim verification workflow using Claude and DuckDuckGo-retrieved evidence."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict
from typing import Any
from urllib.parse import urlparse

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from .claim_extraction import ExtractedClaim
from .search_provider import DuckDuckGoSearchProvider, SearchResult, fetch_source_content


PRIMARY_SOURCE_HINTS = (
    "investors.",
    "ir.",
    "sec.gov",
    "annualreports.com",
    "elevancehealth.com",
    "cms.gov",
    "hhs.gov",
    "justice.gov",
    "fda.gov",
    "ftc.gov",
)


def source_priority(url: str) -> int:
    """Rank likely primary sources ahead of secondary coverage."""

    host = urlparse(url).netloc.lower()
    if any(hint in host or hint in url.lower() for hint in PRIMARY_SOURCE_HINTS):
        return 0
    if any(domain in host for domain in ("reuters.com", "apnews.com", "wsj.com", "statnews.com", "fiercehealthcare.com")):
        return 1
    return 2


def rank_sources(results: list[SearchResult]) -> list[SearchResult]:
    """Sort search results by primary-source likelihood and search-rank score."""

    return sorted(results, key=lambda result: (source_priority(result.url), -(result.score or 0)))


def build_search_queries(claim: ExtractedClaim, company: str | None = None) -> list[str]:
    """Create search queries when the extractor did not supply enough."""

    base_entities = " ".join(claim.entities[:3]) or company or ""
    supplied = claim.search_queries or []
    generated = [
        f"{base_entities} {claim.claim} official",
        f"{base_entities} {claim.claim} annual report OR 10-K OR press release",
        f"{base_entities} {claim.claim} SEC filing",
    ]
    deduped = []
    for query in [*supplied, *generated]:
        cleaned = re.sub(r"\s+", " ", query).strip()
        if cleaned and cleaned.lower() not in {item.lower() for item in deduped}:
            deduped.append(cleaned)
    return deduped[:4]


class ClaudeVerifier:
    """Use Claude to assess a claim against inspected source content."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Set ANTHROPIC_API_KEY before running Claude verification.")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.client = Anthropic(api_key=self.api_key)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=12), stop=stop_after_attempt(3))
    def verify(self, claim: ExtractedClaim, evidence_bundle: list[dict[str, str]]) -> dict[str, Any]:
        """Return a conservative verification decision for one claim."""

        prompt = f"""
You are an evidence auditor. Verify the claim using only the inspected source excerpts below.

Allowed verification_status values:
- Confirmed
- Partially Confirmed
- Contradicted
- Not Found

Rules:
- Do not rely on search snippets alone.
- Prefer primary sources.
- Use Not Found if the sources are weak or irrelevant.
- Use Partially Confirmed when only part of the claim is supported.
- Use Contradicted when reliable evidence conflicts with the claim.
- Confidence score must be a number from 0 to 1.
- Return only a JSON object with verification_status, confidence_score, evidence_notes, source_urls.

Claim:
{asdict(claim)}

Inspected source excerpts:
{json.dumps(evidence_bundle, indent=2)[:18000]}
"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1400,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "\n".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        return _parse_verification_json(text)


def _parse_verification_json(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    if parsed.get("verification_status") not in {"Confirmed", "Partially Confirmed", "Contradicted", "Not Found"}:
        parsed["verification_status"] = "Not Found"
    parsed["confidence_score"] = max(0, min(1, float(parsed.get("confidence_score", 0))))
    parsed.setdefault("evidence_notes", "")
    parsed.setdefault("source_urls", [])
    return parsed


def collect_evidence_for_claim(
    claim: ExtractedClaim,
    search_provider: DuckDuckGoSearchProvider,
    company: str | None = None,
    max_sources: int = 3,
) -> list[dict[str, str]]:
    """Search and inspect source content for a claim."""

    seen_urls: set[str] = set()
    search_results: list[SearchResult] = []
    for query in build_search_queries(claim, company=company):
        for result in search_provider.search(query):
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                search_results.append(result)

    evidence = []
    for result in rank_sources(search_results)[: max_sources * 2]:
        source_text = result.content
        if not source_text:
            try:
                source_text = fetch_source_content(result.url)
            except Exception as exc:  # noqa: BLE001 - keep notebook workflow resilient.
                source_text = f"Unable to retrieve page content: {exc}"
        evidence.append(
            {
                "title": result.title,
                "url": result.url,
                "source_priority": str(source_priority(result.url)),
                "excerpt": source_text[:5000],
            }
        )
        if len(evidence) >= max_sources:
            break
    return evidence


def verify_claims(
    claims: list[ExtractedClaim],
    search_provider: DuckDuckGoSearchProvider,
    verifier: ClaudeVerifier,
    company: str | None = None,
) -> list[dict[str, Any]]:
    """Run evidence collection and verification for each claim."""

    verified = []
    for claim in claims:
        evidence = collect_evidence_for_claim(claim, search_provider, company=company)
        if not evidence:
            decision = {
                "verification_status": "Not Found",
                "confidence_score": 0,
                "evidence_notes": "No searchable evidence was retrieved for this claim.",
                "source_urls": [],
            }
        else:
            decision = verifier.verify(claim, evidence)
        selected_urls = decision.get("source_urls") or [item["url"] for item in evidence]
        sources = [{"url": url} for url in selected_urls[:3]]
        verified.append(
            {
                "claim_id": claim.claim_id,
                "brief_section": claim.brief_section,
                "claim": claim.claim,
                "claim_type": claim.claim_type,
                "entities": claim.entities,
                "date_reference": claim.date_reference,
                "verification_status": decision["verification_status"],
                "confidence_score": decision["confidence_score"],
                "sources": sources,
                "evidence_notes": decision["evidence_notes"],
            }
        )
    return verified
