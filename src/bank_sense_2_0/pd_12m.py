"""BankSense 2.0 — 12-month PD model (IFRS 9 Stage 1 / Basel-style target).

Why: the original PD target was *lifetime* default ("ever defaulted").
Lifetime default rates by origination year swing from ~13% (2015) to ~22% (2019)
and down to ~8% (2021-2023), largely because the 2017-2020 cohorts were exposed
to the COVID shock. A model trained on 2015-2020 lifetime defaults therefore
over-predicts 2023 defaults. A fixed 12-month default window gives a target that
is comparable across cohorts (~2.2% in normal years), which is also the horizon
banks use for Basel PD and IFRS 9 Stage 1 ECL.

Run:  python -m bank_sense_2_0.pd_12m   (from the src/ folder, or with the package installed)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "loan_portfolio.csv"
OUT = ROOT / "data" / "model_outputs"

NUM = ["credit_score", "ead", "coupon_rate", "leverage", "interest_coverage",
       "debt_to_equity", "maturity_months"]
CAT = ["sector", "loan_type", "collateral", "initial_rating"]
COVID_COHORTS = [2019, 2020]  # 12m window overlaps the 2020 shock


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW, parse_dates=["origination_date", "default_date"])
    days = (df["default_date"] - df["origination_date"]).dt.days
    df["default_12m"] = (df["default_date"].notna() & (days <= 365)).astype(int)
    df["year"] = df["origination_date"].dt.year
    df["ead"] = np.log1p(df["ead"])  # skewed exposure
    return df


def model() -> Pipeline:
    pre = ColumnTransformer([
        ("num", StandardScaler(), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
    ])
    return Pipeline([("pre", pre), ("lr", LogisticRegression(max_iter=2000, C=0.5))])


def summarise(name: str, y, p) -> dict:
    return {"split": name, "loans": len(y), "defaults": int(y.sum()),
            "observed_dr_%": round(100 * y.mean(), 3),
            "mean_pd_%": round(100 * p.mean(), 3),
            "gap_pp": round(100 * (p.mean() - y.mean()), 3),
            "auc": round(roc_auc_score(y, p), 4),
            "brier": round(brier_score_loss(y, p), 5)}


def buckets(y, p) -> pd.DataFrame:
    edges = [0, .01, .02, .03, .05, .10, 1]
    b = pd.cut(p, edges, include_lowest=True)
    t = pd.DataFrame({"y": y, "p": p, "bucket": b}).groupby("bucket", observed=True)
    out = t.agg(loans=("y", "size"), defaults=("y", "sum"),
                mean_pd=("p", "mean"), observed_dr=("y", "mean"))
    out[["mean_pd", "observed_dr"]] = (100 * out[["mean_pd", "observed_dr"]]).round(2)
    return out.reset_index()


def run(exclude_covid: bool) -> tuple[list[dict], pd.DataFrame, pd.DataFrame]:
    df = load()
    train_years = [y for y in range(2015, 2021) if not (exclude_covid and y in COVID_COHORTS)]
    tr, cal, val, te = (df[df.year.isin(train_years)], df[df.year == 2021],
                        df[df.year == 2022], df[df.year == 2023])
    base = model().fit(tr[NUM + CAT], tr["default_12m"])
    calib = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid")
    calib.fit(cal[NUM + CAT], cal["default_12m"])
    rows = []
    for name, d in [("train", tr), ("calib_2021", cal), ("select_2022", val), ("oot_2023", te)]:
        rows.append(summarise(name, d["default_12m"].values,
                              calib.predict_proba(d[NUM + CAT])[:, 1]))
    p23 = calib.predict_proba(te[NUM + CAT])[:, 1]
    scored = te[["loan_id", "origination_date", "default_12m"]].assign(pd_12m=p23)
    return rows, buckets(te["default_12m"].values, p23), scored


if __name__ == "__main__":
    for excl in (False, True):
        rows, bk, scored = run(excl)
        tag = "excl_covid_cohorts" if excl else "all_cohorts"
        print(f"\n=== Training {tag} ===")
        print(pd.DataFrame(rows).to_string(index=False))
        print(bk.to_string(index=False))
    OUT.mkdir(parents=True, exist_ok=True)
    rows, bk, scored = run(True)
    pd.DataFrame(rows).to_csv(OUT / "pd_12m_summary.csv", index=False)
    bk.to_csv(OUT / "pd_12m_calibration_buckets_2023.csv", index=False)
    scored.to_csv(OUT / "pd_12m_2023_scores.csv", index=False)
