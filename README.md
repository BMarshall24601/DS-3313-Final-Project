Project Purpose

This project creates a reusable pipeline that ingests raw CSV data, cleans and standardizes it, and produces curated outputs in the form of CSV files. This extends manual curation into a reusable and automated system.

The project ingests a raw CSV file, profiles the data, validates the data, cleans the data, produces a curated CSV file and a file of rows for review and produces a report log.

Dataset Types

This pipeline is designed for CSV or TSV files 

Installing Dependencies

1. Clone the repository
git clone https://github.com/YOUR_USERNAME/data-curation-project.git
cd data-curation-project

2. Create a virtual environment
python -m venv venv
source venv/bin/activate (for Mac/Linux)
venv\Scripts\activate (for Windows)

3. Install dependencies
pip install -r requirements.txt

How to Run the Workflow

Place CSV or TSV files in data/raw/ folder

Follow instructions in settings.yaml to add a new entry. No other files will need to be modified.

Run the pipeline with python src/main.py dataset_a (change the letter at the end as necessary)

Check curated data (under data/curated), flagged(under data/curated) data, and the report (under reports)

Assumptions

Input files are CSVs or TSVs with headers
One column is a unique row identifier

Limitations

Cannot handle Excel files
If the source format changes, update settings.yaml
Flags uncertainties for human review
May not handle very large datasets 

Data is sourced from
- https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9/about_data
- https://data.cityofchicago.org/Service-Requests/311-Service-Requests/v6vf-nfxy/about_data
- https://www.kaggle.com/datasets/lucasgreenwell/big5personalitydataset

Originally, the analyses were performed with data from January 1st to March 31st for the first two datasets and with full data for the final dataset.
It yielded more interesting results than the small datasets.