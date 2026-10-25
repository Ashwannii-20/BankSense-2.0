/* BankSense 2.0 analytics queries for Microsoft SQL Server (T-SQL). */
USE [BankSense];
GO

/* 1. Executive portfolio snapshot. */
SELECT COUNT_BIG(*) AS loan_count,
       SUM(ead) AS total_ead,
       AVG(CAST(defaulted AS DECIMAL(12,10))) AS observed_default_rate,
       AVG(pd_calibrated) AS mean_calibrated_pd,
       AVG(lgd_predicted) AS mean_predicted_lgd,
       SUM(ecl_predicted) AS predicted_ecl,
       SUM(ecl_predicted) / NULLIF(SUM(ead), 0) AS ecl_rate,
       SUM(ecl_covid_stressed) AS covid_stressed_ecl,
       SUM(covid_incremental_ecl) AS covid_incremental_ecl
FROM [banksense].[loan_risk_output];
GO

/* 2. Risk-band validation. Diagnostic only: never retune final-test bands from these outcomes. */
SELECT risk_band,
       COUNT_BIG(*) AS loan_count,
       SUM(ead) AS total_ead,
       AVG(pd_calibrated) AS mean_calibrated_pd,
       AVG(CAST(defaulted AS DECIMAL(12,10))) AS observed_default_rate,
       SUM(ecl_predicted) AS expected_loss,
       SUM(covid_incremental_ecl) AS covid_incremental_ecl
FROM [banksense].[loan_risk_output]
GROUP BY risk_band
ORDER BY CASE risk_band
    WHEN 'Very Low' THEN 1 WHEN 'Low' THEN 2 WHEN 'Medium' THEN 3
    WHEN 'High' THEN 4 WHEN 'Very High' THEN 5 ELSE 6 END;
GO

/* 3. Sector contribution: absolute loss and incremental ECL per GBP 1m EAD. */
;WITH SectorAgg AS (
    SELECT sector,
           COUNT_BIG(*) AS loan_count,
           SUM(ead) AS total_ead,
           AVG(pd_calibrated) AS mean_pd,
           AVG(lgd_predicted) AS mean_lgd,
           SUM(ecl_predicted) AS total_ecl,
           SUM(covid_incremental_ecl) AS covid_incremental_ecl
    FROM [banksense].[loan_risk_output]
    GROUP BY sector
)
SELECT sector, loan_count, total_ead, mean_pd, mean_lgd, total_ecl,
       total_ecl / NULLIF(SUM(total_ecl) OVER (), 0) AS ecl_share,
       covid_incremental_ecl,
       covid_incremental_ecl / NULLIF(total_ead, 0) * 1000000 AS incremental_ecl_per_1m_ead
FROM SectorAgg
ORDER BY covid_incremental_ecl DESC;
GO

/* 4. Stress-scenario comparison. */
SELECT scenario, total_ead, baseline_ecl, stressed_ecl,
       ecl_increase, ecl_increase_pct, average_pd, average_lgd, ecl_rate
FROM [banksense].[stress_summary]
ORDER BY CASE scenario
    WHEN 'baseline' THEN 1 WHEN 'mild' THEN 2 WHEN 'adverse' THEN 3
    WHEN 'gfc_like' THEN 4 WHEN 'severe' THEN 5 WHEN 'covid_like' THEN 6 ELSE 7 END;
GO

/* 5. Analyst review queue: largest modeled COVID-like incremental losses. */
SELECT TOP (25) loan_id, sector, risk_band, ead, pd_calibrated,
       lgd_predicted, ecl_predicted, covid_incremental_ecl
FROM [banksense].[loan_risk_output]
ORDER BY covid_incremental_ecl DESC;
GO

/* 6. Join risk-band dashboard to sector dashboard for a quick portfolio overview. */
SELECT risk_band, loans, total_ead, average_pd, average_lgd, total_ecl,
       covid_ecl, covid_incremental_ecl
FROM [banksense].[risk_band_dashboard]
ORDER BY CASE risk_band
    WHEN 'Very Low' THEN 1 WHEN 'Low' THEN 2 WHEN 'Medium' THEN 3
    WHEN 'High' THEN 4 WHEN 'Very High' THEN 5 ELSE 6 END;
GO
