import pandas as pd

from src.tool_executor import execute_tool


def use_safe_column(df: pd.DataFrame, value, fallback):
    """
    Use the LLM-provided column only if it exists in the dataframe.
    Otherwise use the app-selected fallback column.
    """

    if value in df.columns:
        return value

    return fallback


def fill_default_args(
    tool_name: str,
    args: dict,
    context: dict,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> dict:
    """
    Add safe default arguments when the LLM leaves out obvious app settings
    or returns stale/wrong column names.
    """

    filled_args = dict(args)
    df = context.get("df")

    if tool_name == "calculate_kpi_trend":
        filled_args["date_col"] = use_safe_column(df, filled_args.get("date_col"), date_col)
        filled_args["kpi_name"] = filled_args.get("kpi_name", kpi_name)
        filled_args["revenue_col"] = use_safe_column(df, filled_args.get("revenue_col"), revenue_col)
        filled_args["order_col"] = use_safe_column(df, filled_args.get("order_col"), order_col)

    if tool_name == "compare_periods":
        trend_df = context.get("trend_df")

        if trend_df is not None and not trend_df.empty:
            periods = trend_df["period"].tolist()

            if len(periods) >= 2:
                filled_args.setdefault("previous_period", periods[-2])
                filled_args.setdefault("current_period", periods[-1])

    if tool_name == "analyze_root_cause":
        trend_df = context.get("trend_df")

        filled_args["date_col"] = use_safe_column(df, filled_args.get("date_col"), date_col)
        filled_args["kpi_name"] = filled_args.get("kpi_name", kpi_name)
        filled_args["segment_col"] = use_safe_column(df, filled_args.get("segment_col"), segment_col)
        filled_args["revenue_col"] = use_safe_column(df, filled_args.get("revenue_col"), revenue_col)
        filled_args["order_col"] = use_safe_column(df, filled_args.get("order_col"), order_col)

        if trend_df is not None and not trend_df.empty:
            periods = trend_df["period"].tolist()

            if len(periods) >= 2:
                filled_args.setdefault("previous_period", periods[-2])
                filled_args.setdefault("current_period", periods[-1])

    if tool_name == "detect_anomalies":
        filled_args.setdefault("z_threshold", 1.5)

    if tool_name == "forecast_kpi":
        filled_args.setdefault("periods_to_forecast", 3)

    if tool_name == "run_sql_query":
        filled_args.setdefault(
            "query",
            "SELECT * FROM sales_data LIMIT 10;"
        )

    if tool_name == "generate_insight_summary":
        filled_args["kpi_name"] = filled_args.get("kpi_name", kpi_name)
        filled_args["segment_col"] = use_safe_column(df, filled_args.get("segment_col"), segment_col)

    return filled_args


def run_llm_tool_plan(
    tool_plan: list[dict],
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> dict:
    """
    Execute a validated LLM-generated tool plan.
    """

    context = {"df": df}
    results = {}
    tool_trace = []

    for step in tool_plan:
        tool_name = step["tool_name"]
        raw_args = step.get("args", {})
        reason = step.get("reason", "")

        args = fill_default_args(
            tool_name=tool_name,
            args=raw_args,
            context=context,
            date_col=date_col,
            kpi_name=kpi_name,
            revenue_col=revenue_col,
            order_col=order_col,
            segment_col=segment_col
        )

        result = execute_tool(tool_name, args, context)

        results[tool_name] = result

        tool_trace.append({
            "tool_name": tool_name,
            "args": args,
            "reason": reason,
            "result_type": type(result).__name__
        })

    return {
        "results": results,
        "tool_trace": pd.DataFrame(tool_trace),
        "context": context
    }
