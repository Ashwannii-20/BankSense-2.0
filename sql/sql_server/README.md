# BankSense 2.0 — Microsoft SQL Server integration

These scripts use **T-SQL**, not PostgreSQL syntax. You do not need `psql` for this workflow.

## Prerequisites

- A local or accessible Microsoft SQL Server instance.
- SQL Server Management Studio (SSMS) or another SQL Server query editor.
- Microsoft ODBC Driver 18 for SQL Server for the Python loader (or change the driver name in the connection string to the installed ODBC driver).
- The project's model-output CSVs under `data/model_outputs/`.

## 1. Create the database and tables

1. Open SSMS and connect to the SQL Server instance you normally use.
2. Open and execute `sql/sql_server/01_create_database.sql`.
3. Open and execute `sql/sql_server/02_create_schema_and_tables.sql`.

The database is named `BankSense`; the tables are in the `banksense` schema. Both scripts are designed to be safely rerun.

## 2. Configure the Python loader

From the project root in VS Code terminal, install the optional loader dependency:

```powershell
uv add --dev pyodbc
```

The loader defaults to Windows Authentication on `localhost` with ODBC Driver 18. Set the connection string to match the exact server name shown in SSMS. For example, if SSMS uses `localhost\SQLEXPRESS`:

```powershell
$env:BANKSENSE_SQLSERVER_CONNECTION_STRING = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=BankSense;Trusted_Connection=yes;TrustServerCertificate=yes;"
```

For a default instance, replace the `SERVER` value with `localhost` or the name shown in SSMS. If using SQL authentication, use the appropriate `UID` and `PWD` fields locally; do not save passwords in Git or source files.

First validate the CSVs without a database connection:

```powershell
uv run python sql/sql_server/load_outputs.py --check-only
```

Then load them:

```powershell
uv run python sql/sql_server/load_outputs.py
```

**Important:** the loader deletes and reloads rows in the six `banksense` output tables, inside one database transaction. Use it only for this portfolio database, not for any production or shared database.

## 3. Run analysis and quality checks

In SSMS, open and execute:

- `sql/sql_server/03_analytics_queries.sql` — portfolio snapshot, risk bands, sector contribution, stress scenarios and review queue.
- `sql/sql_server/04_data_quality_checks.sql` — row counts, range checks, ECL arithmetic checks and scenario inventory.

The checks for bad rows are designed to return **zero rows** when the relevant controls pass. Scenario inventory should list six stress scenarios.

## What this demonstrates

- SQL Server schema design, primary keys, check constraints and indexes.
- Data loading from Python output CSVs into relational tables.
- Aggregations, CASE ordering, CTEs, window functions and data-quality reconciliation.

The data remains synthetic, and these analytics are for portfolio demonstration—not production credit decisions.
