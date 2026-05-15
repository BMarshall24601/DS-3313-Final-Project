"""
cleaner.py — Stage 4: Cleaning & Standardization
Applies the cleaning rules from settings.yaml.
Flags rows needing human review
"""
 
import pandas as pd


def clean(df: pd.DataFrame, config: dict):
    df = df.copy()
    clean_cfg = config.get("cleaning", {})
    col_map = config.get("columns", {})
    summary = {
        "duplicates_removed": 0,
        "dates_parsed": {},
        "uppercase_normalized": [],
        "rows_flagged_for_review": 0
    }

    # --- Step 1: Remove duplicate rows by unique ID ---
    uid_col = col_map.get("unique_id", "")
    strategy = clean_cfg.get("on_duplicate", "keep_first")
    if uid_col and uid_col in df.columns and strategy in ("keep_first", "keep_last"):
        before = len(df)
        keep = "first" if strategy == "keep_first" else "last"
        df = df.drop_duplicates(subset=[uid_col], keep=keep)
        removed = before - len(df)
        summary["duplicates_removed"] = removed
        print(f"  [cleaner] Removed {removed} duplicate rows (kept {keep}).")

    # --- Step 2: Normalize text columns to uppercase ---
    for col in clean_cfg.get("normalize_uppercase", []):
        if col in df.columns:
            df[col] = df[col].str.strip().str.upper()
            summary["uppercase_normalized"].append(col)
            print(f"  [cleaner] Normalized '{col}' to uppercase.")

    # --- Step 3: Clean zip-like columns (remove .0 suffix) ---
    for rule in config.get("validation", {}).get("regex_checks", []):
        col = rule.get("column")
        if col and col in df.columns:
            df[col] = df[col].str.strip()
            # Fix "10001.0" → "10001"
            df[col] = df[col].apply(
                lambda v: str(int(float(v))) if pd.notna(v) and v != "" and v.replace(".", "").isdigit() else v
            )
            print(f"  [cleaner] Cleaned formatting in '{col}'.")

    # --- Step 4: Parse date columns ---
    date_fmt = config.get("validation", {}).get("date_format", "")
    for dcol in clean_cfg.get("date_columns", []):
        if dcol not in df.columns or not date_fmt:
            continue
        parsed = pd.to_datetime(df[dcol], format=date_fmt, errors="coerce")
        failed = parsed.isna() & df[dcol].notna()
        df[dcol] = parsed
        summary["dates_parsed"][dcol] = {
            "successfully_parsed": int(parsed.notna().sum()),
            "failed_to_parse": int(failed.sum())
        }
        print(f"  [cleaner] Parsed '{dcol}': {failed.sum()} failed (set to NaT).")

    # --- Step 5: Handle missing values per column strategy ---
    missing_strategy = clean_cfg.get("missing_value_strategy", {})
    flag_col = "validation_flags" if "validation_flags" in df.columns else None

    for col, strategy in missing_strategy.items():
        if col not in df.columns:
            continue
        missing_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
        count = missing_mask.sum()
        if count == 0:
            continue
        if strategy == "flag" and flag_col:
            df.loc[missing_mask, flag_col] += f"review_missing_{col};"
            summary["rows_flagged_for_review"] += int(count)
            print(f"  [cleaner] Flagged {count} rows for missing '{col}'.")
        elif strategy == "leave":
            print(f"  [cleaner] '{col}' has {count} blanks — left as-is (expected).")

    # --- Step 6: Strip whitespace from all string columns ---
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df, summary