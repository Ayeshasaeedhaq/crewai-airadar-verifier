"""Export helpers for AI Radar verification results."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


OUTPUT_COLUMNS = [
    "Claim ID",
    "Brief Section",
    "Extracted Claim",
    "Claim Type",
    "Entities",
    "Date Reference",
    "Verification Status",
    "Confidence Score",
    "Source URL 1",
    "Source URL 2",
    "Source URL 3",
    "Evidence Notes",
]


def results_to_dataframe(results: Iterable[dict]) -> pd.DataFrame:
    """Convert result dictionaries to the required audit-ready output table."""

    rows = []
    for result in results:
        sources = result.get("sources", [])[:3]
        rows.append(
            {
                "Claim ID": result.get("claim_id"),
                "Brief Section": result.get("brief_section"),
                "Extracted Claim": result.get("claim"),
                "Claim Type": result.get("claim_type"),
                "Entities": ", ".join(result.get("entities", [])),
                "Date Reference": result.get("date_reference"),
                "Verification Status": result.get("verification_status"),
                "Confidence Score": result.get("confidence_score"),
                "Source URL 1": sources[0].get("url") if len(sources) > 0 else "",
                "Source URL 2": sources[1].get("url") if len(sources) > 1 else "",
                "Source URL 3": sources[2].get("url") if len(sources) > 2 else "",
                "Evidence Notes": result.get("evidence_notes"),
            }
        )
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def export_results(results: Iterable[dict], output_dir: str | Path = "outputs", basename: str = "airadar_verification") -> dict[str, Path]:
    """Write CSV and XLSX exports. Outputs are gitignored by design."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    dataframe = results_to_dataframe(results)
    csv_path = output_path / f"{basename}.csv"
    xlsx_path = output_path / f"{basename}.xlsx"
    dataframe.to_csv(csv_path, index=False)
    dataframe.to_excel(xlsx_path, index=False)
    return {"csv": csv_path, "xlsx": xlsx_path}
