-- BankSense 2.0 analytics queries for PostgreSQL.

-- 1) Executive portfolio snapshot.
SELECT COUNT(*) AS loan_count,
       SUM(ead) AS total_ead,
       AVG(defaulted::NUMERIC) AS observed_default_rate,
       AVG(pd_calibrated) AS mean_calibrated_pd,
       AVG(lgd_predicted) AS mean_predicted_lgd,
       SUM(ecl_predicted) AS predicted_ecl,
       SUM(ecl_predicted) / NULLIF(SUM(ead), 0) AS ecl_rate,
       SUM(ecl_covid_stressed) AS covid_stressed_ecl,
       SUM(covid_incremental_ecl) AS covid_incremental_ecl
FROM banksense.loan_risk_output;

-- 2) Risk-band validation: diagnostic only; do not retune bands on final test outcomes.
SELECT risk_band,
       COUNT(*) AS loan_count,
       SUM(ead) AS total_ead,
       AVG(pd_calibrated) AS mean_calibrated_pd,
       AVG(defaulted::NUMERIC) AS observed_default_rate,
       SUM(ecl_predicted) AS expected_loss,
       SUM(covid_incremental_ecl) AS covid_incremental_ecl
FROM banksense.loan_risk_output
GROUP BY risk_band
ORDER BY CASE risk_band
    WHEN 'Very Low' THEN 1 WHEN 'Low' THEN 2 WHEN 'Medium' THEN 3
    WHEN 'High' THEN 4 WHEN 'Very High' THEN 5 ELSE 6 END;

-- 3) Sector risk: absolute contribution and incremental loss per GBP 1m EAD.
SELECT sector,
       COUNT(*) AS loan_count,
       SUM(ead) AS total_ead,
       AVG(pd_calibrated) AS mean_pd,
       AVG(lgd_predicted) AS mean_lgd,
       SUM(ecl_predicted) AS total_ecl,
       SUM(ecl_predicted) / NULLIF(SUM(SUM(ecl_predicted)) OVER (), 0) AS ecl_share,
       SUM(covid_incremental_ecl) AS covid_incremental_ecl,
       SUM(covid_incremental_ecl) / NULLIF(SUM(ead), 0) * 1000000 AS incremental_ecl_per_1m_ead
FROM banksense.loan_risk_output
GROUP BY sector
ORDER BY SUM(covid_incremental_ecl) DESC;

-- 4) Stress-scenario comparison.
SELECT scenario, total_ead, baseline_ecl, stressed_ecl,
       ecl_increase, ecl_increase_pct, average_pd, average_lgd, ecl_rate
FROM banksense.stress_summary
ORDER BY CASE scenario
    WHEN 'baseline' THEN 1 WHEN 'mild' THEN 2 WHEN 'adverse' THEN 3
    WHEN 'gfc_like' THEN 4 WHEN 'severe' THEN 5 WHEN 'covid_like' THEN 6 ELSE 7 END;

-- 5) Prioritized review queue: largest modeled COVID-like incremental losses.
-- This is for analyst review, not an automated credit decision.
SELECT loan_id, sector, risk_band, ead, pd_calibrated, lgd_predicted,
       ecl_predicted, covid_incremental_ecl
FROM banksense.loan_risk_output
ORDER BY covid_incremental_ecl DESC
LIMIT 25;
