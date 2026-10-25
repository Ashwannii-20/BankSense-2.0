/* Run after loading CSVs. Each query returns records that need attention or a concise summary. */
USE [BankSense];
GO

/* 1. Row counts. */
SELECT 'loan_risk_output' AS table_name, COUNT_BIG(*) AS row_count FROM [banksense].[loan_risk_output]
UNION ALL SELECT 'stress_ecl_loan_level', COUNT_BIG(*) FROM [banksense].[stress_ecl_loan_level]
UNION ALL SELECT 'stress_summary', COUNT_BIG(*) FROM [banksense].[stress_summary]
UNION ALL SELECT 'sector_dashboard', COUNT_BIG(*) FROM [banksense].[sector_dashboard]
UNION ALL SELECT 'risk_band_dashboard', COUNT_BIG(*) FROM [banksense].[risk_band_dashboard]
UNION ALL SELECT 'portfolio_dashboard_summary', COUNT_BIG(*) FROM [banksense].[portfolio_dashboard_summary];
GO

/* 2. Out-of-range scores or negative amounts. Expected result: zero rows. */
SELECT loan_id, pd_raw, pd_calibrated, lgd_predicted, ead, ecl_predicted
FROM [banksense].[loan_risk_output]
WHERE pd_raw NOT BETWEEN 0 AND 1
   OR pd_calibrated NOT BETWEEN 0 AND 1
   OR lgd_predicted NOT BETWEEN 0 AND 1
   OR ead < 0 OR ecl_predicted < 0;
GO

/* 3. ECL arithmetic reconciliation. Tolerance allows CSV/decimal rounding. Expected: zero rows. */
SELECT loan_id, ead, pd_calibrated, lgd_predicted, ecl_predicted,
       CAST(pd_calibrated * lgd_predicted * ead AS DECIMAL(24,6)) AS recalculated_ecl,
       ABS(ecl_predicted - pd_calibrated * lgd_predicted * ead) AS absolute_difference
FROM [banksense].[loan_risk_output]
WHERE ABS(ecl_predicted - pd_calibrated * lgd_predicted * ead) > 0.05;
GO

/* 4. Stress ECL arithmetic reconciliation. Expected: zero rows. */
SELECT loan_id, scenario, ead, pd_stressed, lgd_stressed, ecl_stressed,
       CAST(pd_stressed * lgd_stressed * ead AS DECIMAL(24,6)) AS recalculated_ecl,
       ABS(ecl_stressed - pd_stressed * lgd_stressed * ead) AS absolute_difference
FROM [banksense].[stress_ecl_loan_level]
WHERE ABS(ecl_stressed - pd_stressed * lgd_stressed * ead) > 0.05;
GO

/* 5. Scenario inventory; expected: six scenarios. */
SELECT scenario, COUNT_BIG(*) AS loan_rows,
       SUM(ead) AS total_ead, SUM(ecl_stressed) AS stressed_ecl
FROM [banksense].[stress_ecl_loan_level]
GROUP BY scenario
ORDER BY CASE scenario
    WHEN 'baseline' THEN 1 WHEN 'mild' THEN 2 WHEN 'adverse' THEN 3
    WHEN 'gfc_like' THEN 4 WHEN 'severe' THEN 5 WHEN 'covid_like' THEN 6 ELSE 7 END;
GO
