from app.core.settings import settings
from app.core.config import logging
from typing import Optional
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)



# Configure logging


def get_llm_response(user_prompt: str, system_prompt: str, response_format) -> Optional[dict]:
    """
    Sends a request to OpenAI's chat completion API with a system prompt and user input.
    
    :param user_prompt: The prompt provided by the user.
    :param system_prompt: Instructions to guide the LLM response.
    :param response_format: Expected response format.
    :return: Parsed LLM response or None in case of failure.
    """
    try:
        response = client.beta.chat.completions.parse(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format
        )
        res = response.choices[0].message.parsed
        return res
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        return None


def get_llm_response_without_fmt(user_prompt: str) -> Optional[str]:
    """
    Sends a request to OpenAI's chat completion API without a system prompt or response format.
    
    :param user_prompt: The prompt provided by the user.
    :return: Raw LLM response content or None in case of failure.
    """
    try:
        response = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )
        res = response.choices[0].message.content
        return res
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        return None
