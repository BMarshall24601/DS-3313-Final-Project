import pandas as pd
import os


def load_csv(filepath: str, config: dict = None) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Input file not found: '{filepath}'\n"
            f"Please place your raw CSV in the correct data/raw/ folder."
        )

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        first_line = f.readline()

    if first_line.count("\t") > first_line.count(","):
        sep = "\t"
        print(f"  [ingest] Detected tab-separated file.")
    else:
        sep = ","
        print(f"  [ingest] Detected comma-separated file.")

    print(f"  [ingest] Loading: {filepath}")
    df = pd.read_csv(filepath, sep=sep, low_memory=False, dtype=str)
    print(f"  [ingest] Loaded {len(df):,} rows, {len(df.columns)} columns.")

    # Fix columns that load as "10011.0" instead of "10011"
    # Apply to any column that has regex checks configured
    if config:
        for rule in config.get("validation", {}).get("regex_checks", []):
            col = rule.get("column")
            if col and col in df.columns:
                df[col] = df[col].apply(
                    lambda v: str(int(float(v))) if pd.notna(v) and v != "" and v.replace(".", "", 1).isdigit() else v
                )
                print(f"  [ingest] Pre-cleaned formatting in '{col}'.")

    return df