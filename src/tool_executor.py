import pandas as pd

from src.profiler import profile_dataframe
from src.kpi_engine import build_monthly_kpi_trend
from src.root_cause import analyze_segment_drivers
from src.anomaly_detector import detect_kpi_anomalies
from src.forecaster import forecast_kpi_trend
from src.sql_engine import run_sql_query
from src.summary_writer import generate_kpi_summary


def compare_period_values(trend_df: pd.DataFrame, previous_period: str, current_period: str) -> dict:
    previous_value = float(
        trend_df.loc[trend_df["period"] == previous_period, "kpi_value"].iloc[0]
    )

    current_value = float(
        trend_df.loc[trend_df["period"] == current_period, "kpi_value"].iloc[0]
    )

    absolute_change = current_value - previous_value

    if previous_value == 0:
        percent_change = None
    else:
        percent_change = (absolute_change / previous_value) * 100

    direction = "increased" if absolute_change > 0 else "decreased" if absolute_change < 0 else "stayed flat"

    return {
        "previous_period": previous_period,
        "current_period": current_period,
        "previous_value": round(previous_value, 2),
        "current_value": round(current_value, 2),
        "absolute_change": round(absolute_change, 2),
        "percent_change": round(percent_change, 2) if percent_change is not None else None,
        "direction": direction
    }


def execute_tool(tool_name: str, args: dict, context: dict):
    """
    Execute one analytics tool.

    context stores shared app data like:
    - df
    - trend_df
    - comparison_result
    - root_cause_result
    - anomaly_result
    - forecast_result
    """

    df = context.get("df")

    if df is None:
        raise ValueError("No dataset found in context.")

    if tool_name == "profile_dataset":
        result = profile_dataframe(df)
        context["profile"] = result
        return result

    if tool_name == "calculate_kpi_trend":
        result = build_monthly_kpi_trend(
            df=df,
            date_col=args["date_col"],
            kpi_name=args["kpi_name"],
            revenue_col=args.get("revenue_col"),
            order_col=args.get("order_col")
        )
        context["trend_df"] = result
        return result

    if tool_name == "compare_periods":
        trend_df = context.get("trend_df")

        if trend_df is None or trend_df.empty:
            raise ValueError("KPI trend must be calculated before comparing periods.")

        result = compare_period_values(
            trend_df=trend_df,
            previous_period=args["previous_period"],
            current_period=args["current_period"]
        )
        context["comparison_result"] = result
        return result

    if tool_name == "analyze_root_cause":
        result = analyze_segment_drivers(
            df=df,
            date_col=args["date_col"],
            segment_col=args["segment_col"],
            kpi_name=args["kpi_name"],
            revenue_col=args.get("revenue_col"),
            order_col=args.get("order_col"),
            previous_period=args["previous_period"],
            current_period=args["current_period"]
        )
        context["root_cause_result"] = result
        return result

    if tool_name == "detect_anomalies":
        trend_df = context.get("trend_df")

        if trend_df is None or trend_df.empty:
            raise ValueError("KPI trend must be calculated before detecting anomalies.")

        result = detect_kpi_anomalies(
            trend_df,
            value_col="kpi_value",
            z_threshold=args.get("z_threshold", 1.5)
        )
        context["anomaly_result"] = result
        return result

    if tool_name == "forecast_kpi":
        trend_df = context.get("trend_df")

        if trend_df is None or trend_df.empty:
            raise ValueError("KPI trend must be calculated before forecasting.")

        result = forecast_kpi_trend(
            trend_df,
            periods_to_forecast=args.get("periods_to_forecast", 3)
        )
        context["forecast_result"] = result
        return result

    if tool_name == "run_sql_query":
        query = args["query"].strip()

        if not query.lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

        result = run_sql_query(df, query)
        context["sql_result"] = result
        return result

    if tool_name == "generate_insight_summary":
        result = generate_kpi_summary(
            change=context.get("comparison_result"),
            driver_df=context.get("root_cause_result"),
            kpi_name=args["kpi_name"],
            segment_col=args.get("segment_col")
        )
        context["business_summary"] = result
        return result

    raise ValueError(f"Unknown tool: {tool_name}")
