"""Free DuckDuckGo search and source-content retrieval utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from ddgs import DDGS
from markdownify import markdownify as md
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class SearchResult:
    title: str
    url: str
    content: str
    score: float | None = None
    raw: dict[str, Any] | None = None


class DuckDuckGoSearchProvider:
    """Search provider that uses free DuckDuckGo web search."""

    def __init__(self, max_results: int = 5, region: str = "us-en") -> None:
        self.max_results = max_results
        self.region = region

    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Run a DuckDuckGo web search and normalize the response."""

        results = []
        with DDGS() as ddgs:
            for index, item in enumerate(
                ddgs.text(
                    query,
                    region=self.region,
                    safesearch="moderate",
                    max_results=max_results or self.max_results,
                )
            ):
                url = item.get("href") or item.get("url")
                if not url:
                    continue
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=url,
                        content=item.get("body", ""),
                        score=1 / (index + 1),
                        raw=item,
                    )
                )
        return results


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
def fetch_source_content(url: str, timeout: int = 20) -> str:
    """Retrieve source page content so verification is not based on search snippets alone."""

    headers = {
        "User-Agent": "AI-Radar-Verifier/1.0 (+https://github.com/Ayeshasaeedhaq/crewai-airadar-verifier)"
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "text/html" in content_type:
        return md(response.text, heading_style="ATX").strip()
    return response.text.strip()
