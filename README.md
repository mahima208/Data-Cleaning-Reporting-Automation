# Data Cleaning & Reporting Automation

Automate data cleaning and reporting workflows using Python. This project helps you preprocess raw data, handle missing values and duplicates, standardize inconsistent values, and generate automated Excel reports with visual summaries.

## Project Structure

```
Data-Cleaning-Reporting-Automation
│
├── data
├── reports
├── images
├── scripts
└── README.md
```

- `data/` - place raw CSV or Excel files here
- `reports/` - generated report workbooks and chart outputs
- `images/` - optional saved visual summaries or exported graphics
- `scripts/` - Python automation scripts

## Features

- Load CSV or Excel data
- Clean missing values, duplicates, and inconsistencies
- Standardize inconsistent text values
- Generate data quality summaries and automated reports
- Create Excel workbooks with cleaned data, summary metrics, and charts
- Generate an HTML dashboard page with charts and data summaries

## Getting Started

### Requirements

- Python 3.9+
- `pandas`
- `openpyxl`
- `matplotlib`
- `seaborn`

Install requirements:

```powershell
python -m pip install -r requirements.txt
```

### Usage

From the project root:

```powershell
python scripts\data_cleaning_reporting.py --input data\your_data.xlsx --output reports
```

To run a sample dataset and generate a demo report:

```powershell
python scripts\data_cleaning_reporting.py --sample --output reports
```

## Expected Outcome

- `reports/cleaned_report.xlsx` with cleaned data, data quality scorecard, and summary metrics
- Chart files in `reports/charts/`
- Better understanding of data preprocessing and reporting efficiency
