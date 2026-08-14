import pandas as pd

from src.profiler import profile_dataframe
from src.kpi_engine import build_monthly_kpi_trend, calculate_period_change
from src.anomaly_detector import detect_kpi_anomalies
from src.forecaster import forecast_kpi_trend


def run_agentic_investigation(
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None
) -> dict:
    """
    Run an agent-style KPI investigation.

    This is not an LLM agent yet. It is a structured multi-step workflow:
    1. Data Quality Agent
    2. KPI Agent
    3. Change Detection Agent
    4. Anomaly Agent
    5. Forecast Agent
    """

    profile = profile_dataframe(df)

    trend_df = build_monthly_kpi_trend(
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col
    )

    change = calculate_period_change(trend_df)

    anomaly_df = detect_kpi_anomalies(
        trend_df,
        value_col="kpi_value",
        z_threshold=1.5
    )

    forecast_df = forecast_kpi_trend(
        trend_df,
        periods_to_forecast=3
    )

    data_quality_notes = []

    if profile["duplicate_rows"] > 0:
        data_quality_notes.append(f"Detected {profile['duplicate_rows']} duplicate rows.")

    missing_total = sum(profile["missing_values"].values())

    if missing_total > 0:
        data_quality_notes.append(f"Detected {missing_total} missing values across the dataset.")

    if not data_quality_notes:
        data_quality_notes.append("No major data quality issues detected from basic profiling.")

    agent_steps = [
        {
            "agent": "Data Quality Agent",
            "task": "Checked missing values, duplicates, and column types.",
            "output": " ".join(data_quality_notes)
        },
        {
            "agent": "KPI Agent",
            "task": f"Calculated monthly {kpi_name}.",
            "output": f"Generated {len(trend_df)} monthly KPI records."
        },
        {
            "agent": "Change Detection Agent",
            "task": "Compared current period against previous period.",
            "output": (
                f"{kpi_name} changed by {change.get('absolute_change')} "
                f"({change.get('percent_change')}%)."
            )
        },
        {
            "agent": "Anomaly Agent",
            "task": "Checked for unusual KPI values using z-score detection.",
            "output": (
                f"Detected {int(anomaly_df['is_anomaly'].sum())} anomalies."
                if not anomaly_df.empty
                else "No anomaly check was performed."
            )
        },
        {
            "agent": "Forecast Agent",
            "task": "Generated a baseline KPI forecast.",
            "output": (
                f"Forecasted {len(forecast_df)} future periods."
                if not forecast_df.empty
                else "Not enough data to forecast."
            )
        }
    ]

    return {
        "profile": profile,
        "trend_df": trend_df,
        "change": change,
        "anomaly_df": anomaly_df,
        "forecast_df": forecast_df,
        "agent_steps": agent_steps
    }
