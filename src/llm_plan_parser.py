import json

from src.tool_registry import ANALYTICS_TOOLS


def clean_llm_json_response(response_text: str) -> str:
    """
    Remove common markdown formatting around JSON.
    """

    cleaned = response_text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def parse_llm_tool_plan(response_text: str) -> list[dict]:
    """
    Parse and validate an LLM-generated tool plan.

    Expected format:
    {
      "tool_plan": [
        {
          "tool_name": "...",
          "args": {...},
          "reason": "..."
        }
      ]
    }
    """

    allowed_tool_names = {tool["tool_name"] for tool in ANALYTICS_TOOLS}

    cleaned_text = clean_llm_json_response(response_text)

    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"LLM response was not valid JSON: {error}")

    if "tool_plan" not in parsed:
        raise ValueError("LLM response must contain a 'tool_plan' key.")

    tool_plan = parsed["tool_plan"]

    if not isinstance(tool_plan, list):
        raise ValueError("'tool_plan' must be a list.")

    validated_plan = []

    for step in tool_plan:
        if not isinstance(step, dict):
            raise ValueError("Each tool plan step must be a dictionary.")

        tool_name = step.get("tool_name")
        args = step.get("args", {})
        reason = step.get("reason", "")

        if tool_name not in allowed_tool_names:
            raise ValueError(f"Unknown tool selected by LLM: {tool_name}")

        if not isinstance(args, dict):
            raise ValueError(f"Args for tool '{tool_name}' must be a dictionary.")

        if not isinstance(reason, str):
            raise ValueError(f"Reason for tool '{tool_name}' must be a string.")

        validated_plan.append({
            "tool_name": tool_name,
            "args": args,
            "reason": reason
        })

    return validated_plan
