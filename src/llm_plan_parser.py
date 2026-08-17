import json

from src.tool_registry import ANALYTICS_TOOLS


def extract_json_from_llm_response(response_text: str) -> dict:
    """
    Extract JSON from an LLM response.

    The LLM should return JSON only, but this function is defensive in case
    the response includes markdown code fences.
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(f"LLM response was not valid JSON: {error}")


def validate_tool_plan(plan: dict, available_columns: list[str]) -> list[dict]:
    """
    Validate an LLM-generated tool plan before executing it.
    """

    if "tool_calls" not in plan:
        raise ValueError("Plan must contain a 'tool_calls' list.")

    if not isinstance(plan["tool_calls"], list):
        raise ValueError("'tool_calls' must be a list.")

    allowed_tools = {tool["tool_name"] for tool in ANALYTICS_TOOLS}
    available_column_set = set(available_columns)

    validated_calls = []

    column_arg_names = {
        "date_col",
        "revenue_col",
        "order_col",
        "segment_col"
    }

    for call in plan["tool_calls"]:
        if not isinstance(call, dict):
            raise ValueError("Each tool call must be a dictionary.")

        tool_name = call.get("tool_name")
        args = call.get("args", {})

        if tool_name not in allowed_tools:
            raise ValueError(f"Tool is not allowed: {tool_name}")

        if not isinstance(args, dict):
            raise ValueError(f"Args for {tool_name} must be a dictionary.")

        for arg_name, arg_value in args.items():
            if arg_name in column_arg_names and arg_value is not None:
                if arg_value not in available_column_set:
                    raise ValueError(
                        f"Invalid column for {arg_name}: {arg_value}. "
                        f"Available columns: {available_columns}"
                    )

        validated_calls.append({
            "tool_name": tool_name,
            "args": args
        })

    return validated_calls


def parse_and_validate_llm_plan(response_text: str, available_columns: list[str]) -> list[dict]:
    """
    Convert raw LLM response text into safe validated tool calls.
    """

    plan = extract_json_from_llm_response(response_text)
    return validate_tool_plan(plan, available_columns)
