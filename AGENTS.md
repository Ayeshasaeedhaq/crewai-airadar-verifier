# AGENTS.md — CrewAI AI Radar Verifier

## Project Goal

Build a portfolio-quality CrewAI notebook that verifies claims from AI Radar-style image/PDF briefs.

The workflow should ingest a JPEG, PNG, or PDF brief, extract visible text with OCR, identify discrete factual claims, research each claim online, verify the claims against reliable sources, and output 1–3 supporting URLs per claim.

## Primary Output

Create and maintain:

- `news_brief_verifier.ipynb`
- `requirements.txt`
- `README.md`
- `.env.example`
- `.gitignore`
- `src/ocr.py`
- `src/claim_extraction.py`
- `src/search_provider.py`
- `src/verification.py`
- `src/export.py`

## Required Architecture

Use CrewAI as the primary orchestration framework.

Agents:

1. Intake OCR Agent
2. Claim Extraction Agent
3. Search Strategy Agent
4. Research Agent
5. Verification Agent
6. Source Ranking Agent
7. Report Agent

## Input Document Pattern

The input may be an image-heavy AI Radar brief with:

- header/title/date/company
- editorial verdict
- KPI metric cards
- grouped findings
- status labels
- update narrative
- footer branding

PDFs may have no selectable text. Always support OCR fallback.

## Notebook Requirements

The notebook must be divided into clear markdown sections:

1. Introduction
2. Architecture Overview
3. Environment Setup
4. Imports
5. Configuration
6. File Input
7. OCR Extraction
8. Claim Extraction
9. CrewAI Agent Definitions
10. CrewAI Task Definitions
11. Crew Execution
12. Verification Results
13. Export Results
14. Limitations
15. How This Demonstrates Agentic AI Experience

## Final Output Table

Include:

- Claim ID
- Page Number
- Brief Section
- Extracted Claim
- Claim Type
- Entities
- Date Reference
- Verification Status
- Confidence Score
- Source URL 1
- Source URL 2
- Source URL 3
- Evidence Notes

## Verification Rules

- Do not verify from search snippets alone.
- Retrieve and inspect source page content.
- Prefer primary sources first:
  - company press releases
  - SEC filings
  - annual reports
  - earnings transcripts
  - government pages
  - official blogs
- Use reputable news sources second.
- Do not invent URLs.
- If evidence is weak, mark as `Not Found`.
- If evidence partly supports the claim, mark as `Partially Confirmed`.
- If evidence conflicts, mark as `Contradicted`.

## Coding Standards

- Keep code modular.
- Use environment variables for API keys.
- Do not hardcode secrets.
- Add comments for non-engineer readability.
- Include error handling.
- Include retry/rate-limit handling.
- Keep intermediate outputs visible in the notebook.
- No placeholder-only code.
- No fake results.
- No toy-only implementation.

## Environment Variables

Use:

```text
OPENAI_API_KEY=
SEARCH_API_KEY=
