# BankSense 2.0 🏦

## Credit Risk, Expected Loss & Macro Stress Testing

BankSense 2.0 is an end-to-end credit-risk analytics project built around a synthetic banking portfolio.

The project covers the full analytical workflow:

**Data Audit → Data Cleaning → Leakage Analysis → PD Modelling → PD Calibration → LGD Modelling → ECL → Macro Stress Testing → Portfolio Risk Dashboard**

The objective is to demonstrate how borrower-level risk models can be combined with exposure information and macroeconomic scenarios to produce portfolio-level credit-risk insights.

---

## 🚀 Project Highlights

### Probability of Default (PD)

A Logistic Regression model was developed using origination-time information and evaluated using a chronological out-of-time test.

**2023 out-of-time results:**

| Metric | Result |
|---|---:|
| ROC-AUC | **0.8889** |
| KS | **0.6402** |
| Raw Brier Score | 0.0705 |
| Platt-Calibrated Brier Score | **0.0584** |

Platt calibration materially improved probability calibration while preserving the model's ranking performance.

---

### Risk Segmentation

Validation-derived PD thresholds were applied to the 2023 out-of-time population.

| Risk Band | Average Predicted PD | Observed Default Rate |
|---|---:|---:|
| Very Low | 4.35% | **0.89%** |
| Low | 7.66% | **3.58%** |
| Medium | 11.00% | **10.44%** |
| High | 15.99% | **12.13%** |
| Very High | 51.17% | **33.33%** |

Observed default rates were monotonic across the risk bands.

The observed default rate increased from **0.89%** in the Very Low band to **33.33%** in the Very High band.

---

### Loss Given Default (LGD)

LGD modelling was performed on defaulted loans only.

The model used:

**HistGradientBoostingRegressor**

**2023 out-of-time performance:**

| Metric | Result |
|---|---:|
| MAE | **0.0802** |
| RMSE | **0.0990** |
| R² | **0.5448** |

The model materially outperformed a simple mean-LGD baseline.

---

### Expected Credit Loss (ECL)

BankSense calculates loan-level expected credit loss as:

```text
ECL = PD × LGD × EAD