import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() in {".csv"}:
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xls", ".xlsx"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file type. Use CSV or Excel.")

    print(f"Loaded data from {path} ({df.shape[0]} rows, {df.shape[1]} columns)")
    return df


def generate_sample_data() -> pd.DataFrame:
    data = {
        "Region": ["North", "south", "East", "East", "West", "north", "South", None, "West", "East"],
        "Sales": [4200, 3300, None, 4100, 3900, 4200, 3300, 3600, 3900, 4100],
        "Date": ["2025-01-12", "2025-01-15", "2025-02-05", "2025-02-05", "2025-03-01", "2025-03-02", "2025-03-05", "2025-03-08", None, "2025-03-10"],
        "Category": ["Office", "office", "Furniture", "Furniture", "Office", "Office", "office", "Furniture", "Office", None],
        "Quantity": [10, 12, 5, 5, 9, 10, 12, 8, 9, 7],
    }
    df = pd.DataFrame(data)
    print("Created sample dataset for demonstration.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    original_shape = df.shape
    df = df.copy()

    df = df.drop_duplicates(ignore_index=True)
    print(f"Dropped duplicates, {original_shape[0] - df.shape[0]} rows removed")

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": None, "none": None, "": None})

    df = df.rename(columns=lambda name: name.strip())

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            print(f"Filled missing numeric values in '{col}' with median={median_value}")
        elif pd.api.types.is_datetime64_any_dtype(df[col]) or col.lower().startswith("date"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].isna().any():
                df[col] = df[col].ffill().bfill()
                print(f"Parsed and filled missing dates in '{col}'")
        else:
            if df[col].isna().any():
                mode_value = df[col].mode(dropna=True)
                replacement = mode_value.iloc[0] if not mode_value.empty else "Unknown"
                df[col] = df[col].fillna(replacement)
                print(f"Filled missing categorical values in '{col}' with '{replacement}'")

    standardization_map = {
        "Region": {"north": "North", "south": "South", "east": "East", "west": "West"},
        "Category": {"office": "Office", "furniture": "Furniture"},
    }
    for col, mapping in standardization_map.items():
        if col in df.columns:
            df[col] = df[col].replace(mapping)
            print(f"Standardized values in '{col}'")

    return df


def build_data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isna().sum()
    data_types = df.dtypes
    unique_counts = df.nunique(dropna=True)

    report = pd.DataFrame(
        {
            "dtype": data_types.astype(str),
            "missing_values": missing,
            "unique_values": unique_counts,
        }
    )
    report.index.name = "column"
    return report


def generate_charts(df: pd.DataFrame, charts_dir: Path) -> None:
    charts_dir.mkdir(parents=True, exist_ok=True)

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    if numeric_columns:
        plt.figure(figsize=(10, 5))
        df[numeric_columns].hist(bins=10, layout=(1, len(numeric_columns)), edgecolor="black")
        plt.tight_layout()
        hist_path = charts_dir / "numeric_histograms.png"
        plt.savefig(hist_path)
        plt.close()
        print(f"Saved numeric histograms to {hist_path}")

    if "Region" in df.columns and "Sales" in df.columns:
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="Region", y="Sales", estimator=sum, errorbar=None)
        plt.title("Total Sales by Region")
        plt.tight_layout()
        chart_path = charts_dir / "sales_by_region.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"Saved sales-by-region chart to {chart_path}")


def save_report(cleaned_df: pd.DataFrame, scorecard: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "cleaned_report.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        cleaned_df.to_excel(writer, sheet_name="CleanedData", index=False)
        scorecard.to_excel(writer, sheet_name="DataQuality")

        summary = pd.DataFrame(
            {
                "metric": [
                    "total_rows",
                    "total_columns",
                    "duplicate_rows",
                    "missing_values_total",
                ],
                "value": [
                    cleaned_df.shape[0],
                    cleaned_df.shape[1],
                    cleaned_df.duplicated().sum(),
                    cleaned_df.isna().sum().sum(),
                ],
            }
        )
        summary.to_excel(writer, sheet_name="Summary", index=False)

    print(f"Saved report workbook to {report_path}")
    return report_path


def save_charts(df: pd.DataFrame, output_dir: Path) -> None:
    charts_dir = output_dir / "charts"
    generate_charts(df, charts_dir)


def run_pipeline(input_path: Path | None, output_dir: Path, generate_sample: bool = False) -> None:
    if generate_sample or input_path is None:
        df = generate_sample_data()
    else:
        df = load_data(input_path)

    cleaned = clean_data(df)
    quality_report = build_data_quality_report(cleaned)
    report_path = save_report(cleaned, quality_report, output_dir)
    save_charts(cleaned, output_dir)

    print("Automation complete.")
    print(f"Report available at: {report_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Data cleaning and reporting automation")
    parser.add_argument("--input", type=Path, help="Path to input CSV or Excel file", default=None)
    parser.add_argument("--output", type=Path, help="Output directory for reports", default=Path("reports"))
    parser.add_argument("--sample", action="store_true", help="Generate a sample dataset and run automation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_pipeline(args.input, args.output, generate_sample=args.sample)


if __name__ == "__main__":
    main()
