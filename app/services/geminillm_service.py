from google import genai
from google.genai import types
from app.core.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def gemini_llm_call(system_instruction:str, user_input:str):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        ),
        contents= user_input
    )
    return response
