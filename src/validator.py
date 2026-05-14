"""
validator.py — Stage 3: Validation
Runs validation checks defined entirely in settings.yaml.
No domain-specific logic lives here — all rules are configured externally.
This means the same validator works on any dataset.
"""

import pandas as pd
import re


def run_all_validations(df: pd.DataFrame, config: dict):
    df = df.copy()
    df["validation_flags"] = ""
    results = []

    val_cfg = config.get("validation", {})

    # --- Rule Type 1: Required fields ---
    # Checks that specified columns are not blank or null.
    for field in val_cfg.get("required_fields", []):
        if field not in df.columns:
            results.append({"rule": f"required_field:{field}", "status": "SKIPPED", "detail": "Column not found"})
            continue
        missing_mask = df[field].isna() | (df[field].astype(str).str.strip() == "")
        count = int(missing_mask.sum())
        df.loc[missing_mask, "validation_flags"] += f"missing_{field};"
        results.append({
            "rule": f"required_field:{field}",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'required:{field}' — {count} missing")

    # --- Rule Type 2: Valid categories ---
    # For any column, checks values are within an allowed list.
    # Configured as a list of {column, values} pairs in settings.yaml.
    for rule in val_cfg.get("valid_categories", []):
        col = rule.get("column")
        allowed = [str(v).upper() for v in rule.get("values", [])]
        if not col or col not in df.columns:
            results.append({"rule": f"valid_categories:{col}", "status": "SKIPPED", "detail": "Column not found"})
            continue
        invalid_mask = ~df[col].astype(str).str.upper().isin(allowed) & df[col].notna()
        count = int(invalid_mask.sum())
        df.loc[invalid_mask, "validation_flags"] += f"invalid_category_{col};"
        results.append({
            "rule": f"valid_categories:{col}",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'valid_categories:{col}' — {count} invalid values")

    # --- Rule Type 3: Regex format checks ---
    # For any column, checks values match a regular expression pattern.
    # Configured as a list of {column, pattern} pairs in settings.yaml.
    for rule in val_cfg.get("regex_checks", []):
        col = rule.get("column")
        pattern = rule.get("pattern")
        if not col or not pattern:
            continue
        if col not in df.columns:
            results.append({"rule": f"regex:{col}", "status": "SKIPPED", "detail": "Column not found"})
            continue
        compiled = re.compile(pattern)
        bad_mask = df[col].notna() & ~df[col].astype(str).str.strip().apply(
            lambda v: bool(compiled.match(v))
        )
        count = int(bad_mask.sum())
        df.loc[bad_mask, "validation_flags"] += f"format_error_{col};"
        results.append({
            "rule": f"regex_format:{col}",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'regex:{col}' — {count} format errors")

    # --- Rule Type 4: Numeric range checks ---
    # For any numeric column, checks values fall within [min, max].
    # Configured as a list of {column, min, max} pairs in settings.yaml.
    for rule in val_cfg.get("range_checks", []):
        col = rule.get("column")
        min_val = rule.get("min")
        max_val = rule.get("max")
        if not col or col not in df.columns:
            results.append({"rule": f"range:{col}", "status": "SKIPPED", "detail": "Column not found"})
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        out_of_range = pd.Series(False, index=df.index)
        if min_val is not None:
            out_of_range |= numeric < min_val
        if max_val is not None:
            out_of_range |= numeric > max_val
        out_of_range &= df[col].notna()
        count = int(out_of_range.sum())
        df.loc[out_of_range, "validation_flags"] += f"out_of_range_{col};"
        results.append({
            "rule": f"range_check:{col}",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'range:{col}' — {count} out-of-range values")

    # --- Rule Type 5: Duplicate ID check ---
    # Checks that a specified ID column has no repeated values.
    uid_col = val_cfg.get("unique_id_column")
    if uid_col and uid_col in df.columns:
        dup_mask = df.duplicated(subset=[uid_col], keep=False)
        count = int(dup_mask.sum())
        df.loc[dup_mask, "validation_flags"] += "duplicate_id;"
        results.append({
            "rule": "duplicate_unique_id",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'duplicate_unique_id' — {count} duplicate IDs")

    # --- Rule Type 6: Date format checks ---
    # For any date column, checks values match the configured format string.
    date_fmt = val_cfg.get("date_format")
    for dcol in config.get("cleaning", {}).get("date_columns", []):
        if dcol not in df.columns or not date_fmt:
            continue
        def bad_date(val):
            try:
                pd.to_datetime(val, format=date_fmt)
                return False
            except Exception:
                return True
        bad_mask = df[dcol].notna() & df[dcol].apply(bad_date)
        count = int(bad_mask.sum())
        df.loc[bad_mask, "validation_flags"] += f"malformed_date_{dcol.replace(' ', '_')};"
        results.append({
            "rule": f"date_format:{dcol}",
            "status": "FAIL" if count > 0 else "PASS",
            "flagged_rows": count
        })
        print(f"  [validator] Rule 'date_format:{dcol}' — {count} malformed dates")

    return df, results