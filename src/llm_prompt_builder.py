from src.tool_registry import ANALYTICS_TOOLS


def build_tool_catalog_text() -> str:
    """
    Convert tool registry into readable text for the LLM.
    """

    lines = []

    for tool in ANALYTICS_TOOLS:
        lines.append(f"Tool name: {tool['tool_name']}")
        lines.append(f"Description: {tool['description']}")
        lines.append(f"Inputs: {tool['inputs']}")
        lines.append(f"Output: {tool['output']}")
        lines.append("")

    return "\n".join(lines)


def build_llm_planner_prompt(
    question: str,
    available_columns: list[str],
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> str:
    """
    Build the prompt that will be sent to an LLM planner.

    The LLM should only choose tools.
    It should not calculate numbers directly.
    """

    tool_catalog = build_tool_catalog_text()

    prompt = f"""
You are the planning brain for MetricPulse AI.

Your job:
Choose which analytics tools should be called to answer the user's question.

Important rules:
- Do not calculate KPI values yourself.
- Do not invent numbers.
- Do not write Python code.
- Only choose from the available tools.
- Return valid JSON only.
- The JSON must contain a list called "tool_plan".
- Each step must include "tool_name", "args", and "reason".

User question:
{question}

Dataset columns:
{available_columns}

Current selected settings:
- date_col: {date_col}
- kpi_name: {kpi_name}
- revenue_col: {revenue_col}
- order_col: {order_col}
- segment_col: {segment_col}

Available tools:
{tool_catalog}

Return JSON in this exact format:

{{
  "tool_plan": [
    {{
      "tool_name": "profile_dataset",
      "args": {{}},
      "reason": "Understand the dataset structure before analysis."
    }},
    {{
      "tool_name": "calculate_kpi_trend",
      "args": {{
        "date_col": "{date_col}",
        "kpi_name": "{kpi_name}",
        "revenue_col": "{revenue_col}",
        "order_col": "{order_col}"
      }},
      "reason": "Calculate the KPI trend needed to answer the question."
    }}
  ]
}}
"""

    return prompt.strip()
