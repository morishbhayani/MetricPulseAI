import json

from src.tool_registry import ANALYTICS_TOOLS


def build_llm_planner_prompt(
    question: str,
    column_names: list[str],
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> str:
    """
    Build the prompt that will be sent to an LLM planner.

    The LLM should not calculate numbers.
    The LLM should only choose tools and arguments.
    """

    tool_registry_json = json.dumps(ANALYTICS_TOOLS, indent=2)

    available_context = {
        "question": question,
        "available_columns": column_names,
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
6. Return valid JSON only.
7. The JSON must contain a list called "tool_calls".
8. Each tool call must include "tool_name" and "args".

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
    }}
  ]
}}
"""

    return prompt.strip()
