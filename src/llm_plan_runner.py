import pandas as pd

from src.llm_plan_parser import parse_and_validate_llm_plan
from src.tool_executor import execute_tool


def run_llm_tool_plan(
    response_text: str,
    df: pd.DataFrame
) -> dict:
    """
    Parse, validate, and execute an LLM-generated tool plan.

    This does not call an LLM.
    It runs a tool plan that looks like something an LLM would return.
    """

    tool_calls = parse_and_validate_llm_plan(
        response_text=response_text,
        available_columns=df.columns.tolist()
    )

    context = {"df": df}
    tool_trace = []
    results = {}

    for call in tool_calls:
        tool_name = call["tool_name"]
        args = call["args"]

        result = execute_tool(
            tool_name=tool_name,
            args=args,
            context=context
        )

        tool_trace.append({
            "tool_name": tool_name,
            "args": args,
            "result_type": type(result).__name__
        })

        results[tool_name] = result

    results["tool_calls"] = tool_calls
    results["tool_trace"] = pd.DataFrame(tool_trace)

    return results
