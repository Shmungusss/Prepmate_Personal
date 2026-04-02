import base64
import os
import openai
from typing import Any

# Utility: Use OpenAI Vision (or similar) to extract recipe or food from image
async def recipe_from_image(image_bytes: bytes) -> dict[str, Any]:
    """
    Uses OpenAI Vision API to extract food type or recipe text from an image, then generates a recipe.
    Returns a dict with either a generated recipe or parsed recipe text.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    client = openai.OpenAI(api_key=api_key)

    # Encode image as base64 for API
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Call OpenAI Vision (GPT-4V) to extract food/recipe
    vision_prompt = """
    You are a culinary expert. If the image is a photo of food, identify the dish and list main ingredients. If the image is a recipe (text), extract the recipe in structured JSON with the following keys:
    - title: string
    - ingredients: list of strings
    - steps: list of strings
    - tips: list of strings (optional)
    Respond ONLY with a JSON object containing these keys. If any section is missing, return an empty list for that section.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": vision_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "What food or recipe is in this image?"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ],
        max_tokens=1200,
        response_format={"type": "json_object"}
    )
    # Parse JSON result
    import json
    content = response.choices[0].message.content
    print("[OpenAI raw response]:", content)  # Debug print
    try:
        result = json.loads(content)
    except Exception:
        result = {"raw": content}
    return result
import settings
import requests

async def call_llm(client, system_prompt, user_prompt, structured_output):
    # Call OpenAI API
    response = client.responses.parse(
        model=settings.LLM,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt
            },
        ],
        text_format = structured_output,
    )
    return response



async def call_vision_llm(client, system_prompt, image_b64, image_media_type, structured_output):
    response = client.responses.parse(
        model=settings.VISION_LLM,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:{image_media_type};base64,{image_b64}",
                    },
                    {
                        "type": "input_text",
                        "text": "Please extract all grocery and food items from this receipt.",
                    },
                ],
            },
        ],
        text_format=structured_output,
    )
    return response


def extract_parsed_response(output):
    """Extract parsed Pydantic model from OpenAI response output"""
    for item in output:
        if hasattr(item, 'content') and item.content:
            for content_item in item.content:
                if hasattr(content_item, 'parsed') and content_item.parsed:
                    return content_item.parsed
    return None