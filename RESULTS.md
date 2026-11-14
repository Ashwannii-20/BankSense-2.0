# BankSense 2.0 - Results Map

Author: Ashwani Tripathi

This page links the main claims in the README to the files in this repository, so every number can be traced.

| README claim | Where to check it |
|---|---|
| Data audit, cleaning, leakage review, PD/LGD modelling | notebooks/01_data_audit.ipynb, 02_data_cleaning.ipynb, 03_leakage_analysis.ipynb |
| 12-month PD rebuild and calibration | src/bank_sense_2_0/pd_12m.py; data/model_outputs/pd_12m_summary.csv, pd_12m_calibration_buckets_2023.csv, pd_12m_2023_scores.csv |
| Loan-level PD, LGD, ECL (2023 test set) | data/model_outputs/banksense_2023_loan_risk_output.csv |
| Six macro stress scenarios | data/model_outputs/stress_summary.csv, stress_ecl_loan_level.csv |
| Sector analysis | data/model_outputs/sector_dashboard.csv |
| Risk bands | data/model_outputs/risk_band_dashboard.csv |
| Portfolio KPIs | data/model_outputs/portfolio_dashboard_summary.csv |
| Dashboard | dashboard/app.py and the live demo linked in the README |
| Data-contract tests | tests/test_model_outputs.py |
| SQL Server and PostgreSQL scripts | sql/sql_server/, sql/postgresql/ |
| Dashboard screenshots | docs/screenshots/ |

## Scope
- This is an independent portfolio project on a public Kaggle dataset, not an IDBI Bank project.
- Stress multipliers are illustrative, not regulatory calibration.
- ECL here is a simplified PD x LGD x EAD demonstration, not full IFRS 9.
- PD and LGD modelling, calibration, ECL and stress testing run in notebooks/03_leakage_analysis.ipynb; the 12-month PD rebuild is in src/bank_sense_2_0/pd_12m.py.
