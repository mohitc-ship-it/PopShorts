# llm_query and llm_structrued api call

from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def llm_query(prompt: str) -> str:
    """
    Simple Gemini 2 text generation
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    print(response.text)



def llm_structured(
    prompt: str,
    output_model: BaseModel,
    model: str = "gemini-2.5-flash",
):
    """
    Gemini structured output using native Pydantic JSON schema
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": output_model.model_json_schema(),
        },
    )

    # Gemini guarantees JSON matching schema
    return output_model.model_validate_json(response.text)

# print(llm_query("who is akshay kumar"))
# class KeywordExtractionResponse(BaseModel):
#     keywords: list[str]
# print(llm_structured("extract keywords from the following text: 'Akshay Kumar is a popular Bollywood actor.'", KeywordExtractionResponse))
