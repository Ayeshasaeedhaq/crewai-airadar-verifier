# CrewAI AI Radar Verifier - Draft v1.0

This project is a text-first claim verifier for AI Radar intelligence briefs. It ingests a `.txt` brief, extracts factual claims with Anthropic Claude, searches for supporting evidence with free DuckDuckGo search, asks Claude to verify each claim against inspected source content, and exports an audit-ready table.

Draft version should be visible in the top heading of every notebook or written draft so portfolio reviewers can tell which iteration they are viewing.

Version one intentionally does not implement OCR. The input must already be text.

## Why CrewAI

CrewAI is used to make the workflow legible as a multi-agent verification system rather than a single opaque script. The notebook defines a seven-agent process:

1. Document Intake Agent
2. Claim Extraction Agent
3. Search Strategy Agent
4. Research Agent
5. Verification Agent
6. Source Ranking Agent
7. Report Agent

The reusable Python modules do the operational work, while CrewAI frames the responsibilities, task handoffs, and portfolio narrative.

## Workflow

1. Load a text AI Radar brief from `sample_briefs/`.
2. Parse markdown-style sections and light metadata.
3. Extract discrete factual claims with Claude.
4. Generate search strategies for each claim.
5. Search with free DuckDuckGo search and inspect returned page content where possible.
6. Prefer primary sources such as company releases, SEC filings, annual reports, government pages, and official blogs.
7. Verify each claim as `Confirmed`, `Partially Confirmed`, `Contradicted`, or `Not Found`.
8. Export CSV and XLSX reports to `outputs/`.

## Setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

When you run the notebook, it will prompt for your Anthropic key securely:

```text
Enter Anthropic API key:
```

You may still use a local `.env` file if you prefer, but it is not required. No search API key is needed because DuckDuckGo search is free and keyless.

The notebook uses automatic Claude model fallback. It starts with current Sonnet models, then tries Haiku models if the key does not have access to Sonnet. You can override the first model attempted by setting `ANTHROPIC_MODEL` in `.env`.

## Run the Notebook

Open `airadar_verifier.ipynb` in Jupyter or VS Code and run the cells from top to bottom. The default input is:

```text
sample_briefs/elevance_health_ai_brief.txt
```

The notebook keeps intermediate outputs visible: parsed metadata, extracted claims, CrewAI agent/task definitions, verification results, and export paths.

## Output Table

The final report includes:

- Claim ID
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

Example statuses:

| Claim ID | Extracted Claim | Verification Status | Confidence Score |
|---|---|---:|---:|
| C001 | Elevance Health reported 2024 operating revenue above $175 billion. | Confirmed | 0.92 |
| C002 | The company served more than 45 million medical members during 2024. | Partially Confirmed | 0.74 |

The example above is illustrative of the table shape. Actual verification results are generated live from Claude and DuckDuckGo evidence retrieval; the project does not ship fake verification outputs.

## Limitations

- No OCR or PDF image extraction in version one.
- Verification depends on Anthropic API availability, DuckDuckGo search coverage, source accessibility, and current public web coverage.
- Some websites block automated retrieval; the workflow records weak evidence as `Not Found` rather than inventing support.
- Claude is asked to verify only against inspected evidence excerpts, not search snippets alone.

## Portfolio Positioning

This project demonstrates practical agentic AI experience across CrewAI orchestration, text-based intelligence ingestion, claim extraction, search strategy generation, evidence retrieval, source ranking, conservative verification logic, and audit-ready reporting.
