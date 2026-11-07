-- BankSense 2.0: PostgreSQL schema for exported model outputs.
-- Execute after creating a database named banksense (or change the DB name).

CREATE SCHEMA IF NOT EXISTS banksense;

CREATE TABLE IF NOT EXISTS banksense.loan_risk_output (
    loan_id TEXT PRIMARY KEY,
    origination_date DATE,
    sector TEXT NOT NULL,
    loan_type TEXT,
    collateral TEXT,
    initial_rating TEXT,
    credit_score INTEGER,
    ead NUMERIC(24, 6) NOT NULL CHECK (ead >= 0),
    defaulted SMALLINT NOT NULL CHECK (defaulted IN (0, 1)),
    pd_raw NUMERIC(12, 10) NOT NULL CHECK (pd_raw BETWEEN 0 AND 1),
    pd_calibrated NUMERIC(12, 10) NOT NULL CHECK (pd_calibrated BETWEEN 0 AND 1),
    lgd_predicted NUMERIC(12, 10) NOT NULL CHECK (lgd_predicted BETWEEN 0 AND 1),
    ecl_predicted NUMERIC(24, 6) NOT NULL CHECK (ecl_predicted >= 0),
    risk_band TEXT NOT NULL CHECK (risk_band IN ('Very Low', 'Low', 'Medium', 'High', 'Very High')),
    pd_covid_stressed NUMERIC(12, 10) NOT NULL CHECK (pd_covid_stressed BETWEEN 0 AND 1),
    lgd_covid_stressed NUMERIC(12, 10) NOT NULL CHECK (lgd_covid_stressed BETWEEN 0 AND 1),
    ecl_covid_stressed NUMERIC(24, 6) NOT NULL CHECK (ecl_covid_stressed >= 0),
    covid_incremental_ecl NUMERIC(24, 6) NOT NULL
);

CREATE TABLE IF NOT EXISTS banksense.stress_ecl_loan_level (
    loan_id TEXT NOT NULL,
    sector TEXT NOT NULL,
    initial_rating TEXT,
    collateral TEXT,
    loan_type TEXT,
    ead NUMERIC(24, 6) NOT NULL CHECK (ead >= 0),
    pd_base NUMERIC(12, 10) NOT NULL CHECK (pd_base BETWEEN 0 AND 1),
    lgd_base NUMERIC(12, 10) NOT NULL CHECK (lgd_base BETWEEN 0 AND 1),
    ecl_base NUMERIC(24, 6) NOT NULL CHECK (ecl_base >= 0),
    pd_stress_multiplier NUMERIC(16, 8) NOT NULL CHECK (pd_stress_multiplier >= 0),
    lgd_stress_multiplier NUMERIC(16, 8) NOT NULL CHECK (lgd_stress_multiplier >= 0),
    pd_stressed NUMERIC(12, 10) NOT NULL CHECK (pd_stressed BETWEEN 0 AND 1),
    lgd_stressed NUMERIC(12, 10) NOT NULL CHECK (lgd_stressed BETWEEN 0 AND 1),
    ecl_stressed NUMERIC(24, 6) NOT NULL CHECK (ecl_stressed >= 0),
    scenario TEXT NOT NULL,
    PRIMARY KEY (loan_id, scenario)
);

CREATE TABLE IF NOT EXISTS banksense.stress_summary (
    scenario TEXT PRIMARY KEY,
    total_ead NUMERIC(24, 6) NOT NULL,
    baseline_ecl NUMERIC(24, 6) NOT NULL,
    stressed_ecl NUMERIC(24, 6) NOT NULL,
    average_pd NUMERIC(12, 10) NOT NULL,
    average_lgd NUMERIC(12, 10) NOT NULL,
    ecl_increase NUMERIC(24, 6) NOT NULL,
    ecl_increase_pct NUMERIC(12, 6) NOT NULL,
    ecl_rate NUMERIC(12, 10) NOT NULL
);

CREATE TABLE IF NOT EXISTS banksense.sector_dashboard (
    sector TEXT PRIMARY KEY,
    loans INTEGER NOT NULL,
    total_ead NUMERIC(24, 6) NOT NULL,
    average_pd NUMERIC(12, 10) NOT NULL,
    average_lgd NUMERIC(12, 10) NOT NULL,
    total_ecl NUMERIC(24, 6) NOT NULL,
    covid_ecl NUMERIC(24, 6) NOT NULL,
    ecl_share_pct NUMERIC(12, 6) NOT NULL,
    covid_incremental_ecl NUMERIC(24, 6) NOT NULL,
    covid_incremental_ecl_per_1m_ead NUMERIC(24, 6) NOT NULL
);

CREATE TABLE IF NOT EXISTS banksense.risk_band_dashboard (
    risk_band TEXT PRIMARY KEY CHECK (risk_band IN ('Very Low', 'Low', 'Medium', 'High', 'Very High')),
    loans INTEGER NOT NULL,
    total_ead NUMERIC(24, 6) NOT NULL,
    average_pd NUMERIC(12, 10) NOT NULL,
    average_lgd NUMERIC(12, 10) NOT NULL,
    total_ecl NUMERIC(24, 6) NOT NULL,
    covid_ecl NUMERIC(24, 6) NOT NULL,
    ecl_share_pct NUMERIC(12, 6) NOT NULL,
    covid_incremental_ecl NUMERIC(24, 6) NOT NULL
);

CREATE TABLE IF NOT EXISTS banksense.portfolio_dashboard_summary (
    metric TEXT PRIMARY KEY,
    value NUMERIC(24, 6) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_loan_risk_sector ON banksense.loan_risk_output (sector);
CREATE INDEX IF NOT EXISTS ix_loan_risk_band ON banksense.loan_risk_output (risk_band);
CREATE INDEX IF NOT EXISTS ix_loan_risk_ecl ON banksense.loan_risk_output (ecl_predicted DESC);
CREATE INDEX IF NOT EXISTS ix_stress_scenario ON banksense.stress_ecl_loan_level (scenario);
