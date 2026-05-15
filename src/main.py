"""
main.py — Automated Data Curation Pipeline
Entry point. Run this file with a dataset key to process a dataset end-to-end.

"""

import sys
import os
import yaml
 
sys.path.insert(0, os.path.dirname(__file__))
 
from ingest import load_csv
from profiler import profile
from validator import run_all_validations
from cleaner import clean
from reporter import save_outputs
 
 
def load_config(config_path="config/settings.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
 
 
def run_pipeline(dataset_key):
    print("=" * 60)
    print(f"  CURATION PIPELINE STARTING: {dataset_key.upper()}")
    print("=" * 60)
 
    full_config = load_config()
    datasets = full_config.get("datasets", {})
 
    if dataset_key not in datasets:
        print(f"ERROR: '{dataset_key}' not found in config/settings.yaml")
        print(f"Available datasets: {list(datasets.keys())}")
        sys.exit(1)
 
    config = datasets[dataset_key]
 
    print(f"\nDataset : {config['name']}")
    print(f"Input   : {config['input_file']}")
    print(f"Output  : {config['output_file']}\n")
 
    print("[Stage 1] Ingesting data...")
    df = load_csv(config["input_file"], config)  # pass config for pre-cleaning
 
    print("\n[Stage 2] Profiling raw data...")
    profile_data = profile(df)
 
    print("\n[Stage 3] Running validation checks...")
    df, validation_results = run_all_validations(df, config)
 
    print("\n[Stage 4] Cleaning and standardizing...")
    df, clean_summary = clean(df, config)
 
    print("\n[Stage 5] Saving outputs and report...")
    save_outputs(
        df_curated=df,
        output_path=config["output_file"],
        report_path=config["report_file"],
        profile=profile_data,
        validation_results=validation_results,
        clean_summary=clean_summary,
        dataset_name=config["name"]
    )
 
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
 
 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <dataset_key>")
        print("Example: python -m src.main dataset_a")
        sys.exit(1)
 
    run_pipeline(sys.argv[1])