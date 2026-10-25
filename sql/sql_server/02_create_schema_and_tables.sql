/* Run after 01_create_database.sql. This script is safe to rerun. */
USE [BankSense];
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'banksense')
    EXEC(N'CREATE SCHEMA [banksense]');
GO

IF OBJECT_ID(N'banksense.loan_risk_output', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[loan_risk_output] (
        loan_id                  VARCHAR(32)   NOT NULL PRIMARY KEY,
        origination_date         DATE          NULL,
        sector                   VARCHAR(100)  NOT NULL,
        loan_type                VARCHAR(50)   NULL,
        collateral               VARCHAR(50)   NULL,
        initial_rating           VARCHAR(25)   NULL,
        credit_score             INT           NULL,
        ead                      DECIMAL(24,6) NOT NULL CHECK (ead >= 0),
        defaulted                TINYINT       NOT NULL CHECK (defaulted IN (0,1)),
        pd_raw                   DECIMAL(12,10) NOT NULL CHECK (pd_raw BETWEEN 0 AND 1),
        pd_calibrated            DECIMAL(12,10) NOT NULL CHECK (pd_calibrated BETWEEN 0 AND 1),
        lgd_predicted            DECIMAL(12,10) NOT NULL CHECK (lgd_predicted BETWEEN 0 AND 1),
        ecl_predicted            DECIMAL(24,6) NOT NULL CHECK (ecl_predicted >= 0),
        risk_band                VARCHAR(20)   NOT NULL CHECK (risk_band IN ('Very Low','Low','Medium','High','Very High')),
        pd_covid_stressed        DECIMAL(12,10) NOT NULL CHECK (pd_covid_stressed BETWEEN 0 AND 1),
        lgd_covid_stressed       DECIMAL(12,10) NOT NULL CHECK (lgd_covid_stressed BETWEEN 0 AND 1),
        ecl_covid_stressed       DECIMAL(24,6) NOT NULL CHECK (ecl_covid_stressed >= 0),
        covid_incremental_ecl    DECIMAL(24,6) NOT NULL
    );
END;
GO

IF OBJECT_ID(N'banksense.stress_ecl_loan_level', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[stress_ecl_loan_level] (
        loan_id                  VARCHAR(32)    NOT NULL,
        sector                   VARCHAR(100)   NOT NULL,
        initial_rating           VARCHAR(25)    NULL,
        collateral               VARCHAR(50)    NULL,
        loan_type                VARCHAR(50)    NULL,
        ead                      DECIMAL(24,6)  NOT NULL CHECK (ead >= 0),
        pd_base                  DECIMAL(12,10) NOT NULL CHECK (pd_base BETWEEN 0 AND 1),
        lgd_base                 DECIMAL(12,10) NOT NULL CHECK (lgd_base BETWEEN 0 AND 1),
        ecl_base                 DECIMAL(24,6)  NOT NULL CHECK (ecl_base >= 0),
        pd_stress_multiplier     DECIMAL(16,8)  NOT NULL CHECK (pd_stress_multiplier >= 0),
        lgd_stress_multiplier    DECIMAL(16,8)  NOT NULL CHECK (lgd_stress_multiplier >= 0),
        pd_stressed              DECIMAL(12,10) NOT NULL CHECK (pd_stressed BETWEEN 0 AND 1),
        lgd_stressed             DECIMAL(12,10) NOT NULL CHECK (lgd_stressed BETWEEN 0 AND 1),
        ecl_stressed             DECIMAL(24,6)  NOT NULL CHECK (ecl_stressed >= 0),
        scenario                 VARCHAR(50)    NOT NULL,
        CONSTRAINT PK_stress_ecl_loan_level PRIMARY KEY (loan_id, scenario)
    );
END;
GO

IF OBJECT_ID(N'banksense.stress_summary', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[stress_summary] (
        scenario          VARCHAR(50)    NOT NULL PRIMARY KEY,
        total_ead         DECIMAL(24,6)  NOT NULL,
        baseline_ecl      DECIMAL(24,6)  NOT NULL,
        stressed_ecl      DECIMAL(24,6)  NOT NULL,
        average_pd        DECIMAL(12,10) NOT NULL,
        average_lgd       DECIMAL(12,10) NOT NULL,
        ecl_increase      DECIMAL(24,6)  NOT NULL,
        ecl_increase_pct  DECIMAL(12,6)  NOT NULL,
        ecl_rate          DECIMAL(12,10) NOT NULL
    );
END;
GO

IF OBJECT_ID(N'banksense.sector_dashboard', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[sector_dashboard] (
        sector                               VARCHAR(100)   NOT NULL PRIMARY KEY,
        loans                                INT            NOT NULL,
        total_ead                            DECIMAL(24,6)  NOT NULL,
        average_pd                           DECIMAL(12,10) NOT NULL,
        average_lgd                          DECIMAL(12,10) NOT NULL,
        total_ecl                            DECIMAL(24,6)  NOT NULL,
        covid_ecl                            DECIMAL(24,6)  NOT NULL,
        ecl_share_pct                        DECIMAL(12,6)  NOT NULL,
        covid_incremental_ecl                DECIMAL(24,6)  NOT NULL,
        covid_incremental_ecl_per_1m_ead     DECIMAL(24,6)  NOT NULL
    );
END;
GO

IF OBJECT_ID(N'banksense.risk_band_dashboard', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[risk_band_dashboard] (
        risk_band             VARCHAR(20)    NOT NULL PRIMARY KEY CHECK (risk_band IN ('Very Low','Low','Medium','High','Very High')),
        loans                 INT            NOT NULL,
        total_ead             DECIMAL(24,6)  NOT NULL,
        average_pd            DECIMAL(12,10) NOT NULL,
        average_lgd           DECIMAL(12,10) NOT NULL,
        total_ecl             DECIMAL(24,6)  NOT NULL,
        covid_ecl             DECIMAL(24,6)  NOT NULL,
        ecl_share_pct         DECIMAL(12,6)  NOT NULL,
        covid_incremental_ecl DECIMAL(24,6)  NOT NULL
    );
END;
GO

IF OBJECT_ID(N'banksense.portfolio_dashboard_summary', N'U') IS NULL
BEGIN
    CREATE TABLE [banksense].[portfolio_dashboard_summary] (
        metric VARCHAR(100)  NOT NULL PRIMARY KEY,
        value  DECIMAL(24,6) NOT NULL
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_loan_risk_sector' AND object_id = OBJECT_ID(N'banksense.loan_risk_output'))
    CREATE INDEX IX_loan_risk_sector ON [banksense].[loan_risk_output](sector);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_loan_risk_band' AND object_id = OBJECT_ID(N'banksense.loan_risk_output'))
    CREATE INDEX IX_loan_risk_band ON [banksense].[loan_risk_output](risk_band);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_loan_risk_ecl' AND object_id = OBJECT_ID(N'banksense.loan_risk_output'))
    CREATE INDEX IX_loan_risk_ecl ON [banksense].[loan_risk_output](ecl_predicted DESC);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_stress_scenario' AND object_id = OBJECT_ID(N'banksense.stress_ecl_loan_level'))
    CREATE INDEX IX_stress_scenario ON [banksense].[stress_ecl_loan_level](scenario);
GO
