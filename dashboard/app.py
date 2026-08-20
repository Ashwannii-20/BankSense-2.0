from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="BankSense 2.0",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "model_outputs"
)


# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_data():
    """Load all saved BankSense model outputs."""

    files = {
        "portfolio": (
            MODEL_OUTPUT_DIR
            / "portfolio_dashboard_summary.csv"
        ),
        "risk_bands": (
            MODEL_OUTPUT_DIR
            / "risk_band_dashboard.csv"
        ),
        "sectors": (
            MODEL_OUTPUT_DIR
            / "sector_dashboard.csv"
        ),
        "loans": (
            MODEL_OUTPUT_DIR
            / "banksense_2023_loan_risk_output.csv"
        ),
        "stress_loans": (
            MODEL_OUTPUT_DIR
            / "stress_ecl_loan_level.csv"
        ),
        "stress_summary": (
            MODEL_OUTPUT_DIR
            / "stress_summary.csv"
        ),
    }

    missing_files = [
        str(path)
        for path in files.values()
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "The following required model-output files are missing:\n"
            + "\n".join(missing_files)
        )

    portfolio = pd.read_csv(
        files["portfolio"]
    )

    risk_bands = pd.read_csv(
        files["risk_bands"]
    )

    sectors = pd.read_csv(
        files["sectors"]
    )

    loans = pd.read_csv(
        files["loans"]
    )

    stress_loans = pd.read_csv(
        files["stress_loans"]
    )

    stress_summary = pd.read_csv(
        files["stress_summary"],
        index_col=0,
    )

    return (
        portfolio,
        risk_bands,
        sectors,
        loans,
        stress_loans,
        stress_summary,
    )


# ============================================================================
# LOAD DATA
# ============================================================================

try:
    (
        portfolio,
        risk_bands,
        sectors,
        loans,
        stress_loans,
        stress_summary,
    ) = load_data()

except Exception as exc:
    st.error(
        "BankSense dashboard data could not be loaded."
    )
    st.exception(exc)
    st.stop()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def metric_value(
    metric_name: str,
    default: float = 0.0,
) -> float:
    """Return a portfolio metric by name."""

    row = portfolio.loc[
        portfolio["metric"].eq(metric_name),
        "value",
    ]

    if row.empty:
        return default

    return float(row.iloc[0])


def gbp_billions(value: float) -> str:
    return f"£{value / 1e9:.2f}B"


def gbp_millions(value: float) -> str:
    return f"£{value / 1e6:.1f}M"


def gbp_thousands(value: float) -> str:
    return f"£{value / 1e3:.1f}K"


def percentage(value: float) -> str:
    return f"{value:.2%}"


def percentage_1dp(value: float) -> str:
    return f"{value:.1f}%"


# ============================================================================
# CORE PORTFOLIO METRICS
# ============================================================================

total_ead = metric_value("total_ead")

observed_default_rate = metric_value(
    "observed_default_rate"
)

mean_predicted_pd = metric_value(
    "mean_predicted_pd"
)

mean_predicted_lgd = metric_value(
    "mean_predicted_lgd"
)

total_predicted_ecl = metric_value(
    "total_predicted_ecl"
)

predicted_ecl_rate = metric_value(
    "predicted_ecl_rate"
)

covid_stressed_ecl = metric_value(
    "covid_stressed_ecl"
)

covid_incremental_ecl = metric_value(
    "covid_incremental_ecl"
)

covid_ecl_increase_pct = metric_value(
    "covid_ecl_increase_pct"
)


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:

    st.markdown(
        "## 🏦 BankSense 2.0"
    )

    st.caption(
        "Credit Risk Analytics"
    )

    st.markdown("---")

    dashboard_view = st.radio(
        "Dashboard view",
        [
            "Executive Overview",
            "Risk Segmentation",
            "Sector Risk",
            "Stress Testing",
            "Loan-Level Risk",
        ],
    )

    st.markdown("---")

    st.markdown(
        "### Model framework"
    )

    st.write(
        "PD: Logistic Regression + Platt calibration"
    )

    st.write(
        "LGD: Gradient Boosting"
    )

    st.write(
        "ECL: PD × LGD × EAD"
    )

    st.write(
        "Test population: 2023 out-of-time"
    )


# ============================================================================
# HEADER
# ============================================================================

st.title(
    "🏦 BankSense 2.0"
)

st.markdown(
    "**Credit Risk & Expected Loss Intelligence**"
)

st.caption(
    "Out-of-time 2023 portfolio | "
    "PD + LGD + EAD + Macro Stress Testing"
)

st.markdown("---")


# ============================================================================
# EXECUTIVE OVERVIEW
# ============================================================================

if dashboard_view == "Executive Overview":

    st.header(
        "Portfolio Overview"
    )

    # ------------------------------------------------------------------------
    # KPI row 1
    # ------------------------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total EAD",
        gbp_billions(total_ead),
    )

    col2.metric(
        "Predicted ECL",
        gbp_billions(total_predicted_ecl),
    )

    col3.metric(
        "ECL Rate",
        percentage(predicted_ecl_rate),
    )

    col4.metric(
        "Mean Predicted PD",
        percentage(mean_predicted_pd),
    )

    # ------------------------------------------------------------------------
    # KPI row 2
    # ------------------------------------------------------------------------

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Mean Predicted LGD",
        percentage(mean_predicted_lgd),
    )

    col6.metric(
        "Observed Default Rate",
        percentage(observed_default_rate),
    )

    col7.metric(
        "COVID-like ECL",
        gbp_billions(covid_stressed_ecl),
    )

    col8.metric(
        "COVID-like Increase",
        percentage_1dp(covid_ecl_increase_pct),
    )

    st.markdown("---")

    # ------------------------------------------------------------------------
    # Key observations
    # ------------------------------------------------------------------------

    st.subheader(
        "Key Risk Observation"
    )

    observation_col1, observation_col2 = st.columns(2)

    with observation_col1:

        st.info(
            f"Observed 2023 default rate: "
            f"**{percentage(observed_default_rate)}**\n\n"
            f"Mean calibrated PD: "
            f"**{percentage(mean_predicted_pd)}**"
        )

    with observation_col2:

        st.warning(
            f"COVID-like stress increases modeled ECL by "
            f"**{percentage_1dp(covid_ecl_increase_pct)}**, "
            f"from "
            f"{gbp_billions(total_predicted_ecl)} "
            f"to "
            f"{gbp_billions(covid_stressed_ecl)}."
        )

    st.markdown("---")

    # ------------------------------------------------------------------------
    # ECL by risk band
    # ------------------------------------------------------------------------

    st.subheader(
        "ECL by Risk Band"
    )

    band_order = [
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High",
    ]

    band_plot = risk_bands.copy()

    band_plot["risk_band"] = pd.Categorical(
        band_plot["risk_band"],
        categories=band_order,
        ordered=True,
    )

    band_plot = band_plot.sort_values(
        "risk_band"
    )

    band_chart = band_plot.set_index(
        "risk_band"
    )[["total_ecl"]].copy()

    band_chart["total_ecl"] = (
        band_chart["total_ecl"]
        / 1e6
    )

    st.bar_chart(
        band_chart,
        y_label="ECL (£ millions)",
    )


# ============================================================================
# RISK SEGMENTATION
# ============================================================================

elif dashboard_view == "Risk Segmentation":

    st.header(
        "Risk Segmentation"
    )

    band_order = [
        "Very Low",
        "Low",
        "Medium",
        "High",
        "Very High",
    ]

    band_view = risk_bands.copy()

    band_view["risk_band"] = pd.Categorical(
        band_view["risk_band"],
        categories=band_order,
        ordered=True,
    )

    band_view = band_view.sort_values(
        "risk_band"
    )

    # ------------------------------------------------------------------------
    # Formatted table
    # ------------------------------------------------------------------------

    display_band = band_view.copy()

    display_band["Total EAD"] = (
        display_band["total_ead"]
        .map(gbp_billions)
    )

    display_band["Average PD"] = (
        display_band["average_pd"]
        .map(percentage)
    )

    display_band["Average LGD"] = (
        display_band["average_lgd"]
        .map(percentage)
    )

    display_band["Total ECL"] = (
        display_band["total_ecl"]
        .map(gbp_millions)
    )

    display_band["ECL Share"] = (
        display_band["ecl_share_pct"]
        .map(percentage_1dp)
    )

    st.dataframe(
        display_band[
            [
                "risk_band",
                "loans",
                "Total EAD",
                "Average PD",
                "Average LGD",
                "Total ECL",
                "ECL Share",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------------------
    # ECL chart
    # ------------------------------------------------------------------------

    st.subheader(
        "Expected Loss by Risk Band"
    )

    ecl_chart = band_view.set_index(
        "risk_band"
    )[["total_ecl"]].copy()

    ecl_chart["total_ecl"] /= 1e6

    st.bar_chart(
        ecl_chart,
        y_label="ECL (£ millions)",
    )

    # ------------------------------------------------------------------------
    # PD chart
    # ------------------------------------------------------------------------

    st.subheader(
        "Predicted PD by Risk Band"
    )

    pd_chart = band_view.set_index(
        "risk_band"
    )[["average_pd"]].copy()

    pd_chart["average_pd"] *= 100

    st.line_chart(
        pd_chart,
        y_label="Predicted PD (%)",
    )


# ============================================================================
# SECTOR RISK
# ============================================================================

elif dashboard_view == "Sector Risk":

    st.header(
        "Sector Risk"
    )

    sector_view = sectors.sort_values(
        "total_ecl",
        ascending=False,
    ).copy()

    # ------------------------------------------------------------------------
    # Formatted sector table
    # ------------------------------------------------------------------------

    display_sector = sector_view.copy()

    display_sector["EAD"] = (
        display_sector["total_ead"]
        .map(gbp_billions)
    )

    display_sector["Average PD"] = (
        display_sector["average_pd"]
        .map(percentage)
    )

    display_sector["Average LGD"] = (
        display_sector["average_lgd"]
        .map(percentage)
    )

    display_sector["ECL"] = (
        display_sector["total_ecl"]
        .map(gbp_millions)
    )

    display_sector["ECL Share"] = (
        display_sector["ecl_share_pct"]
        .map(percentage_1dp)
    )

    display_sector[
        "COVID Incremental ECL"
    ] = (
        display_sector["covid_incremental_ecl"]
        .map(gbp_millions)
    )

    st.dataframe(
        display_sector[
            [
                "sector",
                "loans",
                "EAD",
                "Average PD",
                "Average LGD",
                "ECL",
                "ECL Share",
                "COVID Incremental ECL",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------------------
    # Total ECL by sector
    # ------------------------------------------------------------------------

    st.subheader(
        "Total ECL by Sector"
    )

    sector_chart = sector_view.set_index(
        "sector"
    )[["total_ecl"]].copy()

    sector_chart["total_ecl"] /= 1e6

    st.bar_chart(
        sector_chart,
        y_label="ECL (£ millions)",
    )

    # ------------------------------------------------------------------------
    # COVID-like incremental ECL
    # ------------------------------------------------------------------------

    st.subheader(
        "COVID-like Incremental ECL"
    )

    covid_chart = sector_view.set_index(
        "sector"
    )[["covid_incremental_ecl"]].copy()

    covid_chart["covid_incremental_ecl"] /= 1e6

    st.bar_chart(
        covid_chart,
        y_label="Incremental ECL (£ millions)",
    )


# ============================================================================
# STRESS TESTING
# ============================================================================

elif dashboard_view == "Stress Testing":

    st.header(
        "Macro Stress Testing"
    )

    st.write(
        "Select a scenario to evaluate portfolio-level "
        "and sector-level expected loss."
    )

    # ------------------------------------------------------------------------
    # Scenario selector
    # ------------------------------------------------------------------------

    scenario_choice = st.selectbox(
        "Select stress scenario",
        [
            "Baseline",
            "Mild",
            "Adverse",
            "GFC-like",
            "Severe",
            "COVID-like",
        ],
    )

    scenario_map = {
        "Baseline": "baseline",
        "Mild": "mild",
        "Adverse": "adverse",
        "GFC-like": "gfc_like",
        "Severe": "severe",
        "COVID-like": "covid_like",
    }

    selected_scenario = (
        scenario_map[scenario_choice]
    )

    # ------------------------------------------------------------------------
    # Get selected scenario summary
    # ------------------------------------------------------------------------

    if selected_scenario not in stress_summary.index:

        st.error(
            f"Scenario '{selected_scenario}' "
            "was not found in stress_summary.csv."
        )

        st.stop()

    selected_summary = stress_summary.loc[
        selected_scenario
    ]

    baseline_ecl = float(
        selected_summary["baseline_ecl"]
    )

    stressed_ecl = float(
        selected_summary["stressed_ecl"]
    )

    ecl_increase = float(
        selected_summary["ecl_increase"]
    )

    ecl_increase_pct = float(
        selected_summary["ecl_increase_pct"]
    )

    average_pd = float(
        selected_summary["average_pd"]
    )

    average_lgd = float(
        selected_summary["average_lgd"]
    )

    ecl_rate = float(
        selected_summary["ecl_rate"]
    )

    # ------------------------------------------------------------------------
    # Scenario KPI row 1
    # ------------------------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Stressed ECL",
        gbp_billions(stressed_ecl),
    )

    c2.metric(
        "Incremental ECL",
        gbp_millions(ecl_increase),
    )

    c3.metric(
        "ECL Increase",
        percentage_1dp(ecl_increase_pct),
    )

    c4.metric(
        "Stressed ECL Rate",
        percentage(ecl_rate),
    )

    # ------------------------------------------------------------------------
    # Scenario KPI row 2
    # ------------------------------------------------------------------------

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Average Stressed PD",
        percentage(average_pd),
    )

    c6.metric(
        "Average Stressed LGD",
        percentage(average_lgd),
    )

    c7.metric(
        "Baseline ECL",
        gbp_billions(baseline_ecl),
    )

    c8.metric(
        "Selected Scenario",
        scenario_choice,
    )

    st.markdown("---")

    # ------------------------------------------------------------------------
    # Selected scenario loan records
    # ------------------------------------------------------------------------

    selected_loans = stress_loans.loc[
        stress_loans["scenario"].eq(
            selected_scenario
        )
    ].copy()

    if selected_loans.empty:

        st.error(
            f"No loan-level records were found for "
            f"{scenario_choice}."
        )

        st.stop()

    # ------------------------------------------------------------------------
    # Sector analysis
    # ------------------------------------------------------------------------

    sector_stress = (
        selected_loans
        .groupby("sector")
        .agg(
            loans=("loan_id", "count"),
            total_ead=("ead", "sum"),
            average_pd=("pd_stressed", "mean"),
            average_lgd=("lgd_stressed", "mean"),
            total_ecl=("ecl_stressed", "sum"),
        )
        .sort_values(
            "total_ecl",
            ascending=False,
        )
    )

    sector_stress["ecl_share_pct"] = (
        sector_stress["total_ecl"]
        / sector_stress["total_ecl"].sum()
        * 100
    )

    st.subheader(
        f"{scenario_choice} — Sector Stress Impact"
    )

    sector_display = (
        sector_stress
        .reset_index()
        .copy()
    )

    sector_display["EAD"] = (
        sector_display["total_ead"]
        .map(gbp_billions)
    )

    sector_display["Average PD"] = (
        sector_display["average_pd"]
        .map(percentage)
    )

    sector_display["Average LGD"] = (
        sector_display["average_lgd"]
        .map(percentage)
    )

    sector_display["Stressed ECL"] = (
        sector_display["total_ecl"]
        .map(gbp_millions)
    )

    sector_display["ECL Share"] = (
        sector_display["ecl_share_pct"]
        .map(percentage_1dp)
    )

    st.dataframe(
        sector_display[
            [
                "sector",
                "loans",
                "EAD",
                "Average PD",
                "Average LGD",
                "Stressed ECL",
                "ECL Share",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ------------------------------------------------------------------------
    # Sector chart
    # ------------------------------------------------------------------------

    st.subheader(
        f"{scenario_choice} — ECL by Sector"
    )

    sector_chart = (
        sector_stress[
            ["total_ecl"]
        ]
        .copy()
    )

    sector_chart["total_ecl"] /= 1e6

    st.bar_chart(
        sector_chart,
        y_label="Stressed ECL (£ millions)",
    )

    # ------------------------------------------------------------------------
    # Highest stressed exposures
    # ------------------------------------------------------------------------

    st.subheader(
        f"{scenario_choice} — Highest Stressed ECL Exposures"
    )

    top_stressed = (
        selected_loans
        .sort_values(
            "ecl_stressed",
            ascending=False,
        )
        .head(20)
        .copy()
    )

    top_stressed["EAD"] = (
        top_stressed["ead"]
        .map(gbp_millions)
    )

    top_stressed["Stressed PD"] = (
        top_stressed["pd_stressed"]
        .map(percentage)
    )

    top_stressed["Stressed LGD"] = (
        top_stressed["lgd_stressed"]
        .map(percentage)
    )

    top_stressed["Stressed ECL"] = (
        top_stressed["ecl_stressed"]
        .map(gbp_millions)
    )

    st.dataframe(
        top_stressed[
            [
                "loan_id",
                "sector",
                "initial_rating",
                "collateral",
                "EAD",
                "Stressed PD",
                "Stressed LGD",
                "Stressed ECL",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================================
# LOAN-LEVEL RISK
# ============================================================================

elif dashboard_view == "Loan-Level Risk":

    st.header(
        "Highest Predicted ECL Exposures"
    )

    # ------------------------------------------------------------------------
    # PD filter
    # ------------------------------------------------------------------------

    min_pd = st.slider(
        "Minimum calibrated PD",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
    )

    filtered_loans = loans.loc[
        loans["pd_calibrated"] >= min_pd
    ].copy()

    filtered_loans = (
        filtered_loans
        .sort_values(
            "ecl_predicted",
            ascending=False,
        )
        .head(50)
    )

    # ------------------------------------------------------------------------
    # Format loan table
    # ------------------------------------------------------------------------

    display_loans = filtered_loans.copy()

    display_loans["EAD"] = (
        display_loans["ead"]
        .map(gbp_millions)
    )

    display_loans["PD"] = (
        display_loans["pd_calibrated"]
        .map(percentage)
    )

    display_loans["LGD"] = (
        display_loans["lgd_predicted"]
        .map(percentage)
    )

    display_loans["ECL"] = (
        display_loans["ecl_predicted"]
        .map(gbp_millions)
    )

    display_loans["COVID ECL"] = (
        display_loans["ecl_covid_stressed"]
        .map(gbp_millions)
    )

    st.dataframe(
        display_loans[
            [
                "loan_id",
                "sector",
                "loan_type",
                "collateral",
                "initial_rating",
                "EAD",
                "PD",
                "LGD",
                "ECL",
                "risk_band",
                "COVID ECL",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")

st.caption(
    "BankSense 2.0 | Out-of-time 2023 credit-risk analytics | "
    "PD: Logistic Regression + Platt calibration | "
    "LGD: Gradient Boosting | "
    "ECL = PD × LGD × EAD"
)