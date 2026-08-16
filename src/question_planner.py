def add_tool(plan: list[dict], tool_name: str, reason: str) -> None:
    """
    Add a tool to the plan only once.
    """

    existing_tools = [step["tool_name"] for step in plan]

    if tool_name not in existing_tools:
        plan.append({
            "tool_name": tool_name,
            "reason": reason
        })


def plan_tools_for_question(question: str) -> list[dict]:
    """
    Choose which analytics tools are needed based on the user's question.

    This is a rule-based planner, not an LLM planner yet.
    Later, an LLM can replace this logic and produce the same kind of plan.
    """

    q = question.lower().strip()

    plan = []

    add_tool(
        plan,
        "profile_dataset",
        "Understand the dataset structure before analysis."
    )

    add_tool(
        plan,
        "calculate_kpi_trend",
        "Calculate the KPI trend needed for most analytics questions."
    )

    change_keywords = [
        "change",
        "changed",
        "drop",
        "dropped",
        "decrease",
        "decreased",
        "increase",
        "increased",
        "grew",
        "growth",
        "decline",
        "declined",
        "compare",
        "comparison"
    ]

    root_cause_keywords = [
        "why",
        "root cause",
        "cause",
        "driver",
        "drivers",
        "contributed",
        "contribution",
        "region",
        "category",
        "channel",
        "segment"
    ]

    anomaly_keywords = [
        "anomaly",
        "anomalies",
        "unusual",
        "spike",
        "dip",
        "outlier",
        "weird"
    ]

    forecast_keywords = [
        "forecast",
        "predict",
        "prediction",
        "future",
        "next month",
        "next few months",
        "next quarter"
    ]

    sql_keywords = [
        "sql",
        "query",
        "duckdb"
    ]

    summary_keywords = [
        "summary",
        "summarize",
        "explain",
        "insight",
        "insights",
        "business"
    ]

    if any(keyword in q for keyword in change_keywords):
        add_tool(
            plan,
            "compare_periods",
            "The question asks about KPI change between periods."
        )

    if any(keyword in q for keyword in root_cause_keywords):
        add_tool(
            plan,
            "compare_periods",
            "Root-cause analysis needs a period comparison first."
        )
        add_tool(
            plan,
            "analyze_root_cause",
            "The question asks why the KPI changed or what drove the change."
        )

    if any(keyword in q for keyword in anomaly_keywords):
        add_tool(
            plan,
            "detect_anomalies",
            "The question asks whether any KPI periods look unusual."
        )

    if any(keyword in q for keyword in forecast_keywords):
        add_tool(
            plan,
            "forecast_kpi",
            "The question asks about future KPI values."
        )

    if any(keyword in q for keyword in sql_keywords):
        add_tool(
            plan,
            "run_sql_query",
            "The question asks for SQL-style analysis."
        )

    if any(keyword in q for keyword in summary_keywords) or len(plan) > 2:
        add_tool(
            plan,
            "generate_insight_summary",
            "Generate a stakeholder-ready explanation from the tool outputs."
        )

    if len(plan) == 2:
        add_tool(
            plan,
            "compare_periods",
            "Default comparison helps answer general KPI questions."
        )
        add_tool(
            plan,
            "generate_insight_summary",
            "Generate a concise explanation of the KPI result."
        )

    return plan
