"""Data-contract checks for the exported BankSense 2.0 model outputs.

Run from the project root:
    uv run python -m unittest discover -s tests -v

These are software/data-contract checks, not regulatory model validation.
"""
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = PROJECT_ROOT / "data" / "model_outputs"


class ModelOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loan = pd.read_csv(OUTPUTS / "banksense_2023_loan_risk_output.csv")
        cls.stress = pd.read_csv(OUTPUTS / "stress_ecl_loan_level.csv")
        cls.summary = pd.read_csv(OUTPUTS / "stress_summary.csv")
        cls.sectors = pd.read_csv(OUTPUTS / "sector_dashboard.csv")
        cls.bands = pd.read_csv(OUTPUTS / "risk_band_dashboard.csv")
        cls.portfolio = pd.read_csv(OUTPUTS / "portfolio_dashboard_summary.csv")

    def test_2023_loan_output_has_unique_loan_ids(self):
        self.assertGreater(len(self.loan), 0)
        self.assertIn("loan_id", self.loan.columns)
        self.assertFalse(self.loan["loan_id"].isna().any())
        self.assertFalse(self.loan["loan_id"].duplicated().any())

    def test_required_loan_fields_are_present_and_complete(self):
        required = {
            "loan_id", "ead", "defaulted", "pd_raw", "pd_calibrated",
            "lgd_predicted", "ecl_predicted", "risk_band",
            "pd_covid_stressed", "lgd_covid_stressed",
            "ecl_covid_stressed", "covid_incremental_ecl",
        }
        self.assertTrue(required.issubset(self.loan.columns))
        self.assertFalse(self.loan[list(required)].isna().any().any())

    def test_pd_and_lgd_outputs_are_probabilities(self):
        for column in ("pd_raw", "pd_calibrated", "lgd_predicted",
                       "pd_covid_stressed", "lgd_covid_stressed"):
            self.assertTrue(self.loan[column].between(0, 1).all(), column)

    def test_expected_loss_arithmetic(self):
        expected_ecl = self.loan["pd_calibrated"] * self.loan["lgd_predicted"] * self.loan["ead"]
        np.testing.assert_allclose(self.loan["ecl_predicted"], expected_ecl, rtol=1e-8, atol=0.01)
        expected_stressed_ecl = self.loan["pd_covid_stressed"] * self.loan["lgd_covid_stressed"] * self.loan["ead"]
        np.testing.assert_allclose(self.loan["ecl_covid_stressed"], expected_stressed_ecl, rtol=1e-8, atol=0.01)
        self.assertTrue((self.loan["ecl_predicted"] >= 0).all())
        self.assertTrue((self.loan["ecl_covid_stressed"] >= 0).all())

    def test_stress_output_has_six_scenarios_and_unique_loan_scenario_pairs(self):
        expected = {"baseline", "mild", "adverse", "gfc_like", "severe", "covid_like"}
        self.assertEqual(set(self.stress["scenario"].unique()), expected)
        self.assertFalse(self.stress.duplicated(["loan_id", "scenario"]).any())
        self.assertFalse(self.stress.isna().any().any())

    def test_stress_ecl_arithmetic_and_baseline_consistency(self):
        expected = self.stress["pd_stressed"] * self.stress["lgd_stressed"] * self.stress["ead"]
        np.testing.assert_allclose(self.stress["ecl_stressed"], expected, rtol=1e-8, atol=0.01)
        baseline = self.summary.loc[self.summary["scenario"] == "baseline"].iloc[0]
        self.assertAlmostEqual(float(baseline["baseline_ecl"]), float(baseline["stressed_ecl"]), delta=0.01)
        self.assertAlmostEqual(float(baseline["ecl_increase_pct"]), 0.0, delta=1e-8)

    def test_dashboard_contracts_are_present(self):
        self.assertTrue({"sector", "loans", "total_ead", "total_ecl"}.issubset(self.sectors.columns))
        self.assertTrue({"risk_band", "loans", "total_ead", "average_pd", "total_ecl"}.issubset(self.bands.columns))
        self.assertTrue({"metric", "value"}.issubset(self.portfolio.columns))


if __name__ == "__main__":
    unittest.main()
