import pandas as pd

from src.tool_executor import execute_tool


def run_tool_calling_investigation(
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None,
    previous_period: str | None = None,
    current_period: str | None = None
) -> dict:
    """
    Run a full KPI investigation using the tool executor.

    This is still not an LLM agent.
    It is a controlled tool-calling workflow that proves our tools can be called
    through one shared executor.
    """

    context = {"df": df}
    tool_trace = []

    def call_tool(tool_name: str, args: dict):
        result = execute_tool(tool_name, args, context)

        tool_trace.append({
            "tool_name": tool_name,
            "args": args,
            "result_type": type(result).__name__
        })

        return result

    profile = call_tool("profile_dataset", {})

    trend_df = call_tool(
        "calculate_kpi_trend",
        {
            "date_col": date_col,
            "kpi_name": kpi_name,
            "revenue_col": revenue_col,
            "order_col": order_col
        }
    )

    periods = trend_df["period"].tolist()

    if len(periods) >= 2:
        if previous_period is None:
            previous_period = periods[-2]

        if current_period is None:
            current_period = periods[-1]

        comparison_result = call_tool(
            "compare_periods",
            {
                "previous_period": previous_period,
                "current_period": current_period
            }
        )
    else:
        comparison_result = {}

    if segment_col is not None and previous_period is not None and current_period is not None:
        root_cause_result = call_tool(
            "analyze_root_cause",
            {
                "date_col": date_col,
                "kpi_name": kpi_name,
                "segment_col": segment_col,
                "previous_period": previous_period,
                "current_period": current_period,
                "revenue_col": revenue_col,
                "order_col": order_col
            }
        )
    else:
        root_cause_result = pd.DataFrame()

    anomaly_result = call_tool(
        "detect_anomalies",
        {
            "z_threshold": 1.5
        }
    )

    forecast_result = call_tool(
        "forecast_kpi",
        {
            "periods_to_forecast": 3
        }
    )

    summary = call_tool(
        "generate_insight_summary",
        {
            "kpi_name": kpi_name,
            "segment_col": segment_col
        }
    )

    return {
        "profile": profile,
        "trend_df": trend_df,
        "comparison_result": comparison_result,
        "root_cause_result": root_cause_result,
        "anomaly_result": anomaly_result,
        "forecast_result": forecast_result,
        "summary": summary,
        "tool_trace": pd.DataFrame(tool_trace)
    }
