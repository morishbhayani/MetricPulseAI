import pandas as pd

from src.llm_client import call_llm_planner
from src.llm_planner_prompt import build_llm_planner_prompt
from src.llm_plan_runner import run_llm_tool_plan


def get_available_periods(df: pd.DataFrame, date_col: str) -> list[str]:
    """
    Extract available monthly periods from the dataset.
    """

    working_df = df.copy()
    working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")
    working_df = working_df.dropna(subset=[date_col])

    if working_df.empty:
        return []

    periods = (
        working_df[date_col]
        .dt.to_period("M")
        .astype(str)
        .dropna()
        .unique()
        .tolist()
    )

    return sorted(periods)


def run_metricpulse_llm_agent(
    question: str,
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> dict:
    """
    Run the real LLM-powered MetricPulse Analyst Agent.

    LLM job:
    - choose tools
    - return JSON plan

    Python job:
    - validate JSON
    - execute tools
    - calculate real results
    """

    available_periods = get_available_periods(df, date_col)

    prompt = build_llm_planner_prompt(
        question=question,
        column_names=df.columns.tolist(),
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col,
        available_periods=available_periods
    )

    llm_plan_text = call_llm_planner(prompt)

    result = run_llm_tool_plan(
        response_text=llm_plan_text,
        df=df
    )

    result["question"] = question
    result["available_periods"] = available_periods
    result["llm_plan_text"] = llm_plan_text
    result["llm_prompt"] = prompt

    return result
