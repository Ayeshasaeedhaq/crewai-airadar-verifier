"""Text-first intake helpers for AI Radar briefs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_EXTENSIONS = {".txt"}


@dataclass
class BriefDocument:
    """Parsed representation of a text-based AI Radar brief."""

    path: Path
    title: str
    company: str | None
    date: str | None
    sections: dict[str, str]
    raw_text: str


def read_text_brief(path: str | Path) -> str:
    """Read a plain-text brief from disk.

    OCR and binary document parsing are intentionally out of scope for v1.
    """

    brief_path = Path(path)
    if not brief_path.exists():
        raise FileNotFoundError(f"Brief not found: {brief_path}")
    if brief_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported brief type '{brief_path.suffix}'. Use one of: {supported}")
    text = brief_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Brief is empty: {brief_path}")
    return text


def parse_sections(raw_text: str) -> dict[str, str]:
    """Split markdown-ish text into named sections while preserving body text."""

    sections: dict[str, list[str]] = {"Overview": []}
    current = "Overview"
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                current = heading
                sections.setdefault(current, [])
                continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items() if "\n".join(lines).strip()}


def _first_matching_value(lines: Iterable[str], label: str) -> str | None:
    prefix = f"{label.lower()}:"
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith(prefix):
            return stripped.split(":", 1)[1].strip() or None
    return None


def load_brief(path: str | Path) -> BriefDocument:
    """Load a text brief and extract light metadata for the workflow."""

    brief_path = Path(path)
    raw_text = read_text_brief(brief_path)
    sections = parse_sections(raw_text)
    lines = raw_text.splitlines()
    first_heading = next((line.lstrip("#").strip() for line in lines if line.strip().startswith("#")), brief_path.stem)
    company = _first_matching_value(lines, "Company")
    date = _first_matching_value(lines, "Date")
    return BriefDocument(path=brief_path, title=first_heading, company=company, date=date, sections=sections, raw_text=raw_text)
