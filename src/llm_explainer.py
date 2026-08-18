import json
import pandas as pd


def make_json_safe(value):
    """
    Convert pandas objects into JSON-safe Python objects.
    """

    if isinstance(value, pd.DataFrame):
        return {
            "columns": value.columns.tolist(),
            "rows": value.head(10).to_dict(orient="records")
        }

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def build_llm_explainer_prompt(question: str, result: dict) -> str:
    """
    Build a prompt for the LLM to explain verified Python tool outputs.
    """

    evidence = {}

    allowed_result_keys = [
        "tool_trace",
        "calculate_kpi_trend",
        "compare_periods",
        "analyze_root_cause",
        "detect_anomalies",
        "forecast_kpi",
        "run_sql_query",
        "generate_insight_summary"
    ]

    for key in allowed_result_keys:
        if key in result:
            evidence[key] = make_json_safe(result[key])

    evidence_json = json.dumps(evidence, indent=2)

    prompt = f"""
You are the final explanation layer for MetricPulse AI.

The user asked:
{question}

You are given verified outputs from Python analytics tools.

Your job is to write a concise business answer using only the provided evidence.

Rules:
1. Do not invent numbers.
2. Do not invent causes.
3. Start with the direct answer.
4. Use simple business language.
5. Keep the answer around 4-7 sentences.
6. Explain what changed and the likely driver if root-cause evidence is available.
7. Only mention anomalies if anomaly evidence is provided.
8. Only mention forecast if forecast evidence is provided.
9. Do not say forecast, anomaly, or other evidence is missing unless the user's question specifically asks for it.

Verified tool outputs:
{evidence_json}

Write the final answer:
"""

    return prompt.strip()
