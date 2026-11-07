-- These checks should return zero rows / an expected six-scenario count.

-- 1) Duplicate loan identifiers (expected: no rows).
SELECT loan_id, COUNT(*) AS duplicate_count
FROM banksense.loan_risk_output
GROUP BY loan_id
HAVING COUNT(*) > 1;

-- 2) Invalid probability/loss-ratio values (expected: no rows).
SELECT loan_id, pd_calibrated, lgd_predicted, pd_covid_stressed, lgd_covid_stressed
FROM banksense.loan_risk_output
WHERE pd_calibrated NOT BETWEEN 0 AND 1
   OR lgd_predicted NOT BETWEEN 0 AND 1
   OR pd_covid_stressed NOT BETWEEN 0 AND 1
   OR lgd_covid_stressed NOT BETWEEN 0 AND 1;

-- 3) ECL arithmetic mismatches (expected: no rows; tolerance handles decimal rounding).
SELECT loan_id, ecl_predicted,
       pd_calibrated * lgd_predicted * ead AS recomputed_ecl,
       ecl_covid_stressed,
       pd_covid_stressed * lgd_covid_stressed * ead AS recomputed_covid_ecl
FROM banksense.loan_risk_output
WHERE ABS(ecl_predicted - (pd_calibrated * lgd_predicted * ead)) > 0.01
   OR ABS(ecl_covid_stressed - (pd_covid_stressed * lgd_covid_stressed * ead)) > 0.01;

-- 4) Scenario coverage (expected: six scenarios, including baseline).
SELECT COUNT(DISTINCT scenario) AS scenario_count,
       ARRAY_AGG(DISTINCT scenario ORDER BY scenario) AS scenarios
FROM banksense.stress_summary;

-- 5) Baseline scenario should not change ECL (expected: no rows).
SELECT scenario, baseline_ecl, stressed_ecl, stressed_ecl - baseline_ecl AS difference
FROM banksense.stress_summary
WHERE scenario = 'baseline'
  AND ABS(stressed_ecl - baseline_ecl) > 0.01;
