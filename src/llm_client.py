import os

from dotenv import load_dotenv
from groq import Groq


def call_llm_planner(prompt: str) -> str:
    """
    Call the LLM planner.

    The LLM's job is only to return a JSON tool plan.
    It should not calculate KPI values or write the final business answer.
    """

    load_dotenv(dotenv_path=".env")

    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY. Add it to a .env file or export it in your terminal."
        )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a tool-planning agent. "
                    "Return valid JSON only. "
                    "Do not calculate numbers. "
                    "Do not explain. "
                    "Only choose tool calls."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
