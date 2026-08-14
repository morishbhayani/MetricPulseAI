import pandas as pd


def dataframe_to_markdown_table(df: pd.DataFrame, max_rows: int = 10) -> str:
    """
    Convert a dataframe to a markdown table.
    """

    if df is None or df.empty:
        return "No data available."

    return df.head(max_rows).to_markdown(index=False)


def generate_markdown_report(
    kpi_name: str,
    trend_df: pd.DataFrame,
    change: dict,
    driver_df: pd.DataFrame | None = None,
    anomaly_df: pd.DataFrame | None = None,
    forecast_df: pd.DataFrame | None = None,
    insight_summary: str | None = None
) -> str:
    """
    Generate a stakeholder-ready markdown report.
    """

    report = f"""# MetricPulse AI Report

## KPI Analyzed

**KPI:** {kpi_name}

## Executive Summary

{insight_summary if insight_summary else "No summary available."}

## Period Change

- **Previous period:** {change.get("previous_period")}
- **Current period:** {change.get("current_period")}
- **Previous value:** {change.get("previous_value")}
- **Current value:** {change.get("current_value")}
- **Absolute change:** {change.get("absolute_change")}
- **Percent change:** {change.get("percent_change")}%

## KPI Trend

{dataframe_to_markdown_table(trend_df)}

## Root-Cause Driver Analysis

{dataframe_to_markdown_table(driver_df)}

## Anomaly Detection

{dataframe_to_markdown_table(anomaly_df)}

## Forecast

{dataframe_to_markdown_table(forecast_df)}

## Notes

This report was generated from uploaded CSV data using pandas, DuckDB, and Streamlit. KPI values, root-cause drivers, anomalies, and forecasts are calculated programmatically.
"""

    return report
