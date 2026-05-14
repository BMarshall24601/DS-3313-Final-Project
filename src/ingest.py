import pandas as pd
import os


def load_csv(filepath: str) -> pd.DataFrame:
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
    return df