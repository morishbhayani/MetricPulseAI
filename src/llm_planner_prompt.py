import json

from src.tool_registry import ANALYTICS_TOOLS


def build_llm_planner_prompt(
    question: str,
    column_names: list[str],
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None,
    available_periods: list[str] | None = None
) -> str:
    """
    Build the prompt that will be sent to an LLM planner.

    The LLM should not calculate numbers.
    The LLM should only choose tools and arguments.
    """

    available_periods = available_periods or []

    default_previous_period = available_periods[-2] if len(available_periods) >= 2 else None
    default_current_period = available_periods[-1] if len(available_periods) >= 2 else None

    tool_registry_json = json.dumps(ANALYTICS_TOOLS, indent=2)

    available_context = {
        "question": question,
        "available_columns": column_names,
        "available_periods": available_periods,
        "default_previous_period": default_previous_period,
        "default_current_period": default_current_period,
        "selected_date_col": date_col,
        "selected_kpi_name": kpi_name,
        "selected_revenue_col": revenue_col,
        "selected_order_col": order_col,
        "selected_segment_col": segment_col
    }

    context_json = json.dumps(available_context, indent=2)

    prompt = f"""
You are the planning layer for MetricPulse AI.

Your job is to choose which analytics tools should be called to answer the user's question.

Important rules:
1. Do not calculate KPI values yourself.
2. Do not invent numbers.
3. Do not answer the user directly.
4. Only choose tools from the provided tool registry.
5. Use only the available columns.
6. Use only available_periods for previous_period and current_period.
7. Return valid JSON only.
8. The JSON must contain a list called "tool_calls".
9. Each tool call must include "tool_name" and "args".
10. Always call calculate_kpi_trend before compare_periods, analyze_root_cause, detect_anomalies, forecast_kpi, or generate_insight_summary.
11. For drop, decline, increase, change, or comparison questions, call compare_periods.
12. For why, cause, driver, contribution, region, category, channel, or segment questions, call analyze_root_cause.
13. For anomaly, unusual, spike, dip, or outlier questions, call detect_anomalies.
14. For forecast, predict, future, next month, or next quarter questions, call forecast_kpi.
15. For SQL questions, call run_sql_query with a read-only SELECT query using the table name sales_data.
16. If compare_periods is needed and the user does not specify periods, use default_previous_period and default_current_period.
17. If a business explanation is needed, end with generate_insight_summary.

Available tool registry:
{tool_registry_json}

Available dataset context:
{context_json}

User question:
{question}

Return JSON in exactly this format:

{{
  "tool_calls": [
    {{
      "tool_name": "profile_dataset",
      "args": {{}}
    }},
    {{
      "tool_name": "calculate_kpi_trend",
      "args": {{
        "date_col": "{date_col}",
        "kpi_name": "{kpi_name}",
        "revenue_col": "{revenue_col}",
        "order_col": "{order_col}"
      }}
    }},
    {{
      "tool_name": "compare_periods",
      "args": {{
        "previous_period": "{default_previous_period}",
        "current_period": "{default_current_period}"
      }}
    }}
  ]
}}
"""

    return prompt.strip()
