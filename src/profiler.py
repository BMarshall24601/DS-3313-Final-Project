"""
profiler.py — Stage 2: Data Profiling
Generates a summary of the raw data before any cleaning.
This tells us what we're working with: shape, missing values, duplicates.
"""

import pandas as pd


def profile(df: pd.DataFrame) -> dict:
    """
    Build a profile summary of the DataFrame.
    Returns a dictionary that gets saved to the final report.
    """
    print(f"  [profiler] Profiling {len(df):,} rows...")

    profile_data = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "missing_values": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "field_summaries": {}
    }

    for col in df.columns:
        missing = df[col].isna().sum() + (df[col] == "").sum()
        pct = round((missing / len(df)) * 100, 2)
        profile_data["missing_values"][col] = {
            "count": int(missing),
            "percent": pct
        }

    for col in df.columns:
        unique_count = df[col].nunique()
        profile_data["field_summaries"][col] = {
            "unique_values": int(unique_count)
        }

    print(f"  [profiler] Found {profile_data['duplicate_rows']} duplicate rows.")
    return profile_data