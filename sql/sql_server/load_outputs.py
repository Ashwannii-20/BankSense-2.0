"""Load BankSense model-output CSVs into Microsoft SQL Server.

Connection string may be supplied via BANKSENSE_SQLSERVER_CONNECTION_STRING.
Default uses Windows authentication against localhost and ODBC Driver 18.
Run from project root:
  uv add --dev pyodbc
  $env:BANKSENSE_SQLSERVER_CONNECTION_STRING = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=BankSense;Trusted_Connection=yes;TrustServerCertificate=yes;"
  uv run python sql/sql_server/load_outputs.py --check-only
  uv run python sql/sql_server/load_outputs.py
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "model_outputs"

TABLES: list[dict[str, Any]] = [
    {
        "file": "banksense_2023_loan_risk_output.csv",
        "table": "loan_risk_output",
        "columns": ["loan_id", "origination_date", "sector", "loan_type", "collateral", "initial_rating", "credit_score", "ead", "defaulted", "pd_raw", "pd_calibrated", "lgd_predicted", "ecl_predicted", "risk_band", "pd_covid_stressed", "lgd_covid_stressed", "ecl_covid_stressed", "covid_incremental_ecl"],
        "date_columns": {"origination_date"},
        "int_columns": {"credit_score", "defaulted"},
        "decimal_columns": {"ead", "pd_raw", "pd_calibrated", "lgd_predicted", "ecl_predicted", "pd_covid_stressed", "lgd_covid_stressed", "ecl_covid_stressed", "covid_incremental_ecl"},
    },
    {
        "file": "stress_ecl_loan_level.csv",
        "table": "stress_ecl_loan_level",
        "columns": ["loan_id", "sector", "initial_rating", "collateral", "loan_type", "ead", "pd_base", "lgd_base", "ecl_base", "pd_stress_multiplier", "lgd_stress_multiplier", "pd_stressed", "lgd_stressed", "ecl_stressed", "scenario"],
        "date_columns": set(),
        "int_columns": set(),
        "decimal_columns": {"ead", "pd_base", "lgd_base", "ecl_base", "pd_stress_multiplier", "lgd_stress_multiplier", "pd_stressed", "lgd_stressed", "ecl_stressed"},
    },
    {
        "file": "stress_summary.csv",
        "table": "stress_summary",
        "columns": ["scenario", "total_ead", "baseline_ecl", "stressed_ecl", "average_pd", "average_lgd", "ecl_increase", "ecl_increase_pct", "ecl_rate"],
        "date_columns": set(),
        "int_columns": set(),
        "decimal_columns": {"total_ead", "baseline_ecl", "stressed_ecl", "average_pd", "average_lgd", "ecl_increase", "ecl_increase_pct", "ecl_rate"},
    },
    {
        "file": "sector_dashboard.csv",
        "table": "sector_dashboard",
        "columns": ["sector", "loans", "total_ead", "average_pd", "average_lgd", "total_ecl", "covid_ecl", "ecl_share_pct", "covid_incremental_ecl", "covid_incremental_ecl_per_1m_ead"],
        "date_columns": set(),
        "int_columns": {"loans"},
        "decimal_columns": {"total_ead", "average_pd", "average_lgd", "total_ecl", "covid_ecl", "ecl_share_pct", "covid_incremental_ecl", "covid_incremental_ecl_per_1m_ead"},
    },
    {
        "file": "risk_band_dashboard.csv",
        "table": "risk_band_dashboard",
        "columns": ["risk_band", "loans", "total_ead", "average_pd", "average_lgd", "total_ecl", "covid_ecl", "ecl_share_pct", "covid_incremental_ecl"],
        "date_columns": set(),
        "int_columns": {"loans"},
        "decimal_columns": {"total_ead", "average_pd", "average_lgd", "total_ecl", "covid_ecl", "ecl_share_pct", "covid_incremental_ecl"},
    },
    {
        "file": "portfolio_dashboard_summary.csv",
        "table": "portfolio_dashboard_summary",
        "columns": ["metric", "value"],
        "date_columns": set(),
        "int_columns": set(),
        "decimal_columns": {"value"},
    },
]


def convert_value(column: str, value: str, spec: dict[str, Any]) -> Any:
    if value is None or value.strip() == "":
        return None
    if column in spec["date_columns"]:
        return datetime.strptime(value, "%Y-%m-%d").date()
    if column in spec["int_columns"]:
        return int(value)
    if column in spec["decimal_columns"]:
        try:
            return Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid numeric value for {column}: {value!r}") from exc
    return value


def read_rows(spec: dict[str, Any]) -> list[tuple[Any, ...]]:
    path = OUTPUT_DIR / spec["file"]
    if not path.exists():
        raise FileNotFoundError(f"Required CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != spec["columns"]:
            raise ValueError(
                f"Unexpected columns in {path.name}.\n"
                f"Expected: {spec['columns']}\nFound: {reader.fieldnames}"
            )
        rows = [tuple(convert_value(col, row.get(col, ""), spec) for col in spec["columns"]) for row in reader]
    if not rows:
        raise ValueError(f"CSV contains no data rows: {path}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="validate CSV headers and values without connecting to SQL Server")
    args = parser.parse_args()

    payloads: list[tuple[dict[str, Any], list[tuple[Any, ...]]]] = []
    try:
        for spec in TABLES:
            rows = read_rows(spec)
            payloads.append((spec, rows))
            print(f"OK  {spec['file']}: {len(rows):,} rows; columns match")
    except (OSError, ValueError) as exc:
        print(f"CSV validation failed: {exc}", file=sys.stderr)
        return 2

    if args.check_only:
        print("CSV checks passed. No database connection was made.")
        return 0

    connection_string = os.environ.get(
        "BANKSENSE_SQLSERVER_CONNECTION_STRING",
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=BankSense;Trusted_Connection=yes;TrustServerCertificate=yes;",
    )
    try:
        import pyodbc  # type: ignore[import-not-found]
    except ImportError:
        print("Missing pyodbc. Install with: uv add --dev pyodbc", file=sys.stderr)
        return 3

    conn = None
    try:
        conn = pyodbc.connect(connection_string, autocommit=False)
        cursor = conn.cursor()
        for spec, rows in payloads:
            table = spec["table"]
            columns = spec["columns"]
            quoted_columns = ", ".join(f"[{col}]" for col in columns)
            placeholders = ", ".join("?" for _ in columns)
            cursor.execute(f"DELETE FROM [banksense].[{table}]")
            insert_sql = f"INSERT INTO [banksense].[{table}] ({quoted_columns}) VALUES ({placeholders})"
            cursor.fast_executemany = False
            cursor.executemany(insert_sql, rows)
            print(f"Loaded {len(rows):,} rows into banksense.{table}")
        conn.commit()
        print("All CSV outputs loaded successfully; transaction committed.")
        return 0
    except Exception as exc:  # keep DB/driver-specific error visible to user
        if conn is not None:
            conn.rollback()
        print(f"SQL Server load failed; transaction rolled back.\n{exc}", file=sys.stderr)
        return 4
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
