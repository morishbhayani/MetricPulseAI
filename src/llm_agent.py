import pandas as pd

from src.llm_prompt_builder import build_llm_planner_prompt
from src.llm_plan_parser import parse_llm_tool_plan
from src.llm_plan_executor import run_llm_tool_plan


def run_llm_planned_agent(
    question: str,
    llm_response_text: str,
    df: pd.DataFrame,
    date_col: str,
    kpi_name: str,
    revenue_col: str | None = None,
    order_col: str | None = None,
    segment_col: str | None = None
) -> dict:
    """
    Run the LLM-planned analytics agent.

    This function does not call an LLM API yet.
    It assumes the LLM response text is already available.

    Flow:
    1. Build planner prompt
    2. Parse LLM JSON response
    3. Execute the selected tool plan
    """

    prompt = build_llm_planner_prompt(
        question=question,
        available_columns=df.columns.tolist(),
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col
    )

    tool_plan = parse_llm_tool_plan(llm_response_text)

    execution_result = run_llm_tool_plan(
        tool_plan=tool_plan,
        df=df,
        date_col=date_col,
        kpi_name=kpi_name,
        revenue_col=revenue_col,
        order_col=order_col,
        segment_col=segment_col
    )

    return {
        "question": question,
        "planner_prompt": prompt,
        "tool_plan": pd.DataFrame(tool_plan),
        "tool_trace": execution_result["tool_trace"],
        "results": execution_result["results"],
        "context": execution_result["context"]
    }
