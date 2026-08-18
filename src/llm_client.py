import os

from dotenv import load_dotenv
from groq import Groq


def get_groq_client_and_model():
    """
    Load Groq API key and model from .env.
    """

    load_dotenv(dotenv_path=".env")

    api_key = os.environ.get("GROQ_API_KEY")
    model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY. Add it to a .env file or export it in your terminal."
        )

    client = Groq(api_key=api_key)

    return client, model


def call_llm_planner(prompt: str) -> str:
    """
    Call the LLM planner.

    The planner's job:
    - choose analytics tools
    - return JSON only
    - do not calculate KPI values
    """

    client, model = get_groq_client_and_model()

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


def call_llm_explainer(prompt: str) -> str:
    """
    Call the LLM explainer.

    The explainer's job:
    - explain verified Python tool outputs
    - do not invent numbers
    - do not invent causes
    """

    client, model = get_groq_client_and_model()

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a business analytics explainer. "
                    "Use only verified Python tool outputs. "
                    "Do not invent numbers or causes."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
