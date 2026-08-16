import pandas as pd

from src.question_planner import plan_tools_for_question
from src.tool_executor import execute_tool


def build_basic_sql_query(
    kpi_name: str,
    revenue_col: str | None,
    order_col: str | None,
    segment_col: str | None
) -> str:
    """
    Build a simple safe SELECT query for demo SQL questions.
    """

    if segment_col is None:
        segment_col = "region"

    if kpi_name == "Revenue" and revenue_col is not None:
        return f"""
SELECT
    {segment_col},
    ROUND(SUM({revenue_col}), 2) AS total_revenue
FROM sales_data
GROUP BY {segment_col}
ORDER BY total_revenue DESC;
"""

    if kpi_name == "Orders" and order_col is not None:
        return f"""
SELECT
    {segment_col},
    COUNT(DISTINCT {order_col}) AS total_orders
FROM sales_data
GROUP BY {segment_col}
ORDER BY total_orders DESC;
"""

    if kpi_name == "Average Order Value" and revenue_col is not None and order_col is not None:
        return f"""
SELECT
    {segment_col},
    ROUND(SUM({revenue_col}) / COUNT(DISTINCT {order_col}), 2) AS average_order_value
FROM sales_data
GROUP BY {segment_col}
ORDER BY average_order_value DESC;
"""

    return f"""
SELECT *
FROM sales_data
LIMIT 10;
"""


def run_question_agent(
    question: str,
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> dict:
    """
    Run tools based on a user question.

    This is still not an LLM agent.
    The planner is rule-based, but the architecture matches a future LLM tool-calling flow.
    """

    plan = plan_tools_for_question(question)
    context = {"df": df}
    tool_trace = []

    previous_period = None
    current_period = None

    def call_tool(tool_name: str, args: dict):
        result = execute_tool(tool_name, args, context)

        tool_trace.append({
            "tool_name": tool_name,
            "args": args,
            "result_type": type(result).__name__
        })

        return result

    results = {}

    for step in plan:
        tool_name = step["tool_name"]

        if tool_name == "profile_dataset":
            results["profile"] = call_tool("profile_dataset", {})

        elif tool_name == "calculate_kpi_trend":
            trend_df = call_tool(
                "calculate_kpi_trend",
                {
                    "date_col": date_col,
                    "kpi_name": kpi_name,
                    "revenue_col": revenue_col,
                    "order_col": order_col
                }
            )

            results["trend_df"] = trend_df

            periods = trend_df["period"].tolist()

            if len(periods) >= 2:
                previous_period = periods[-2]
                current_period = periods[-1]

        elif tool_name == "compare_periods":
            if previous_period is not None and current_period is not None:
                results["comparison_result"] = call_tool(
                    "compare_periods",
                    {
                        "previous_period": previous_period,
                        "current_period": current_period
                    }
                )

        elif tool_name == "analyze_root_cause":
            if segment_col is not None and previous_period is not None and current_period is not None:
                results["root_cause_result"] = call_tool(
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

        elif tool_name == "detect_anomalies":
            results["anomaly_result"] = call_tool(
                "detect_anomalies",
                {
                    "z_threshold": 1.5
                }
            )

        elif tool_name == "forecast_kpi":
            results["forecast_result"] = call_tool(
                "forecast_kpi",
                {
                    "periods_to_forecast": 3
                }
            )

        elif tool_name == "run_sql_query":
            sql_query = build_basic_sql_query(
                kpi_name=kpi_name,
                revenue_col=revenue_col,
                order_col=order_col,
                segment_col=segment_col
            )

            results["sql_result"] = call_tool(
                "run_sql_query",
                {
                    "query": sql_query
                }
            )

        elif tool_name == "generate_insight_summary":
            results["summary"] = call_tool(
                "generate_insight_summary",
                {
                    "kpi_name": kpi_name,
                    "segment_col": segment_col
                }
            )

    results["question"] = question
    results["plan"] = pd.DataFrame(plan)
    results["tool_trace"] = pd.DataFrame(tool_trace)

    return results
