"""
copy_generator.py
-----------------
Calls the Anthropic Claude API and parses structured JSON responses.
Implements retry logic and error handling for production reliability.
"""

import json
import re
import time
import anthropic
from src.prompt_builder import build_copy_prompt


def extract_json(text: str) -> dict:
    """
    Safely extracts JSON from Claude's response.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Strip markdown code fences if present
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\nRaw response:\n{text}")


def generate_marketing_copy(
    product_name: str,
    category: str,
    description: str,
    tone: str = "Professional",
    max_retries: int = 2
) -> dict:
    """
    Generates marketing copy using Claude claude-3-5-haiku.

    Args:
        product_name: Name of the product
        category: Product category (e.g., "skincare", "tech gadget")
        description: Short description of the product
        tone: Writing tone (Professional, Playful, Luxury, etc.)
        max_retries: Number of retries on failure

    Returns:
        dict with tagline, description, CTA, social captions, benefits, audience
    """
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment
    system_prompt, user_prompt = build_copy_prompt(product_name, category, description, tone)

    for attempt in range(max_retries + 1):
        try:
            message = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw_text = message.content[0].text
            result = extract_json(raw_text)

            # Add metadata
            result["_meta"] = {
                "model": message.model,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "product_name": product_name,
                "tone": tone
            }
            return result

        except ValueError as e:
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise e
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}")
