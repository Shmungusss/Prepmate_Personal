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



def extract_parsed_response(output):
    """Extract parsed Pydantic model from OpenAI response output"""
    for item in output:
        if hasattr(item, 'content') and item.content:
            for content_item in item.content:
                if hasattr(content_item, 'parsed') and content_item.parsed:
                    return content_item.parsed
    return None