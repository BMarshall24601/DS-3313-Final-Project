"""
reporter.py — Stage 5: Reporting & Output
Saves the curated data and writes a JSON report documenting everything that happened.
"""

import json
import os
import pandas as pd
from datetime import datetime


def save_outputs(
    df_curated,
    output_path,
    report_path,
    profile,
    validation_results,
    clean_summary,
    dataset_name
):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    flag_col = "validation_flags"
    if flag_col in df_curated.columns:
        has_flags = df_curated[flag_col].str.strip() != ""
    else:
        has_flags = pd.Series(False, index=df_curated.index)

    df_clean = df_curated[~has_flags].drop(columns=[flag_col], errors="ignore")
    df_flagged = df_curated[has_flags]

    df_clean.to_csv(output_path, index=False)
    print(f"  [reporter] Saved {len(df_clean):,} clean rows → {output_path}")

    if has_flags.any():
        flagged_path = output_path.replace(".csv", "_flagged_for_review.csv")
        df_flagged.to_csv(flagged_path, index=False)
        print(f"  [reporter] Saved {len(df_flagged):,} flagged rows → {flagged_path}")

    report = {
        "dataset": dataset_name,
        "run_timestamp": datetime.now().isoformat(),
        "profile": profile,
        "validation_results": validation_results,
        "cleaning_summary": clean_summary,
        "output_summary": {
            "total_rows_input": profile["row_count"],
            "clean_rows_output": len(df_clean),
            "flagged_rows_output": int(has_flags.sum()),
            "duplicates_removed": clean_summary.get("duplicates_removed", 0)
        }
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"  [reporter] Report saved → {report_path}")