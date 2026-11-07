# BankSense 2.0 — PostgreSQL Analytics Layer

This folder adds a PostgreSQL analytics layer over exported model outputs. It does **not** replace the notebook modelling pipeline or make the dashboard database-backed; the current Streamlit dashboard continues to read the CSV outputs.

## Files

- `01_create_schema.sql` — output tables, checks, primary keys and indexes.
- `02_load_outputs.psql` — CSV loading with PostgreSQL's `\copy` command.
- `03_analytics_queries.sql` — portfolio snapshot, risk bands, sector concentration, scenario comparison and review queue.
- `04_data_quality_checks.sql` — checks for duplicate IDs, probability bounds, ECL arithmetic and scenario coverage.

## Run on Windows

1. In pgAdmin, create a database named `banksense`.
2. Open PowerShell in the `Bank_sense_2.0` project root—the directory containing `data`, `notebooks`, and `pyproject.toml`.
3. Create the schema:

   ```powershell
   psql -U postgres -d banksense -f sql/postgresql/01_create_schema.sql
   ```

4. Load the CSV outputs:

   ```powershell
   psql -U postgres -d banksense -f sql/postgresql/02_load_outputs.psql
   ```

5. Run the analytics queries:

   ```powershell
   psql -U postgres -d banksense -f sql/postgresql/03_analytics_queries.sql
   ```

6. Run data-quality checks:

   ```powershell
   psql -U postgres -d banksense -f sql/postgresql/04_data_quality_checks.sql
   ```

If `psql` is not recognized, add PostgreSQL's `bin` directory to PATH or use SQL Shell (psql). The load file contains psql-specific `\copy` commands; don't paste those commands into pgAdmin's ordinary SQL Query Tool. You can instead use pgAdmin's Import/Export Data feature for each table.

## Scope

The dataset is synthetic/public portfolio data—not IDBI Bank customer data. The review queue ranks modeled incremental loss and must not be treated as an automated credit decision. This is a portfolio demonstration, not a complete IFRS 9 implementation or production risk system.
