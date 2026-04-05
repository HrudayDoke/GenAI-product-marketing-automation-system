"""
image_prompt_gen.py
-------------------
Generates DALL-E-compatible image prompts via Claude.
Optionally calls DALL-E 3 if an OpenAI key is available.
Falls back gracefully to showing the prompt when no key is present.
"""

import os
import json
import re
import anthropic
from src.prompt_builder import build_image_prompt


def extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def generate_image_prompt(
    product_name: str,
    category: str,
    description: str,
    style: str = "Photorealistic"
) -> dict:
    """
    Uses Claude to generate a detailed, structured DALL-E 3 image prompt.

    Returns dict with:
      - dalle_prompt: the actual prompt string to send to DALL-E
      - negative_elements: what to avoid
      - suggested_size: recommended aspect ratio
      - art_style_notes: reasoning behind the style choice
    """
    client = anthropic.Anthropic()
    system_prompt, user_prompt = build_image_prompt(product_name, category, description, style)

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    raw_text = message.content[0].text
    result = extract_json(raw_text)
    return result


def generate_image_with_dalle(dalle_prompt: str, size: str = "1792x1024") -> str | None:
    """
    Calls DALL-E 3 with the generated prompt.
    Returns image URL if successful, None if OpenAI key is not set.

    This is optional — the project works without it.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "your_openai_api_key_here":
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size=size,
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"DALL-E generation failed: {e}")
        return None
