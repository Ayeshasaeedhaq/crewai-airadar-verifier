# AGENTS.md — CrewAI AI Radar Verifier

## Project Goal

Build a portfolio-quality CrewAI notebook that verifies claims from text-based AI Radar intelligence briefs.

The workflow should ingest a `.txt` or `.md` brief, extract discrete factual claims, research each claim online, verify the claims against reliable sources, and output 1–3 supporting URLs per claim.

The system should be text-first. OCR is not required for the first version.

## Primary Output

Create and maintain:

* `airadar_verifier.ipynb`
* `requirements.txt`
* `README.md`
* `.env.example`
* `.gitignore`
* `sample_briefs/elevance_health_ai_brief.txt`
* `outputs/.gitkeep`
* `src/intake.py`
* `src/claim_extraction.py`
* `src/search_provider.py`
* `src/verification.py`
* `src/export.py`

## Required Architecture

Use CrewAI as the primary orchestration framework.

Agents:

1. Document Intake Agent
2. Claim Extraction Agent
3. Search Strategy Agent
4. Research Agent
5. Verification Agent
6. Source Ranking Agent
7. Report Agent

## Input Document Pattern

The input is a text-based AI Radar brief.

Expected sections may include:

* title
* company name
* date
* editorial verdict
* KPI metric cards
* grouped findings
* status labels
* strategic narrative
* update notes
* source notes if available

Example claim types:

* financial claims
* operational efficiency claims
* workforce claims
* product launch claims
* partnership claims
* legal/regulatory claims
* executive strategy claims
* AI infrastructure claims

## Notebook Requirements

The notebook must be divided into clear markdown sections:

1. Introduction
2. Architecture Overview
3. Environment Setup
4. Imports
5. Configuration
6. Text Brief Input
7. Document Parsing
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

* Claim ID
* Brief Section
* Extracted Claim
* Claim Type
* Entities
* Date Reference
* Verification Status
* Confidence Score
* Source URL 1
* Source URL 2
* Source URL 3
* Evidence Notes

## Verification Rules

* Do not verify from search snippets alone.
* Retrieve and inspect source page content when possible.
* Prefer primary sources first:

  * company press releases
  * SEC filings
  * annual reports
  * earnings transcripts
  * government pages
  * official blogs
* Use reputable news sources second.
* Do not invent URLs.
* If evidence is weak, mark as `Not Found`.
* If evidence partly supports the claim, mark as `Partially Confirmed`.
* If evidence conflicts, mark as `Contradicted`.

## Coding Standards

* Keep code modular.
* Use environment variables for API keys.
* Do not hardcode secrets.
* Add comments for non-engineer readability.
* Include error handling.
* Include retry/rate-limit handling.
* Keep intermediate outputs visible in the notebook.
* No placeholder-only code.
* No fake results.
* No toy-only implementation.

## Environment Variables

Use Claude as the primary LLM.

```text
ANTHROPIC_API_KEY=
SEARCH_API_KEY=
```

Search provider:

Use Tavily first.

## Git Safety

Never commit:

* `.env`
* API keys
* exported CSV/XLSX outputs
* notebook checkpoints
* cache files

## README Requirements

README should explain:

* what the project does
* why CrewAI is used
* how the agent workflow works
* setup instructions
* how to run the notebook
* example output
* limitations
* portfolio positioning

## Portfolio Positioning

The project should demonstrate:

* CrewAI agent orchestration
* text-based intelligence ingestion
* claim extraction
* search strategy generation
* evidence retrieval
* source ranking
* verification logic
* audit-ready reporting

## First Build Instruction for Codex

Read this `AGENTS.md` first.

Then build the full project according to these instructions.

Start by creating the repo structure and files. Then implement the notebook and modules end-to-end.

Use text input first. Do not add OCR in version one.
