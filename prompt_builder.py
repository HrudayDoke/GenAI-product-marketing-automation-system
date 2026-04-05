"""
prompt_builder.py
-----------------
Builds structured prompts for the Claude API.
Separates prompt logic from API call logic — a key prompt engineering best practice.
"""


def build_copy_prompt(product_name: str, category: str, description: str, tone: str = "professional") -> str:
    """
    Constructs a detailed system + user prompt for marketing copy generation.
    Uses few-shot formatting and explicit JSON schema to ensure reliable structured output.
    """
    system_prompt = """You are an expert marketing copywriter specializing in product launches.
Your task is to generate compelling, conversion-optimized marketing content.
You always respond with valid JSON only — no markdown, no explanation, no preamble.
The JSON must exactly match the schema provided by the user."""

    user_prompt = f"""Generate marketing copy for the following product.

PRODUCT DETAILS:
- Name: {product_name}
- Category: {category}
- Description: {description}
- Tone: {tone}

Return ONLY a valid JSON object with this exact structure:
{{
  "tagline": "A punchy one-liner under 10 words",
  "product_description": "A compelling 50-word product description highlighting key benefits",
  "call_to_action": "A strong CTA button text (3-5 words)",
  "social_captions": {{
    "twitter": "Tweet under 280 chars with 2-3 relevant hashtags",
    "instagram": "Instagram caption with emojis and 5 hashtags",
    "linkedin": "Professional LinkedIn post (2-3 sentences, no hashtags)"
  }},
  "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
  "target_audience": "Who this product is for (1 sentence)"
}}"""

    return system_prompt, user_prompt


def build_image_prompt(product_name: str, category: str, description: str, style: str = "photorealistic") -> str:
    """
    Builds a structured prompt that generates a DALL-E-compatible image prompt.
    Uses chain-of-thought prompting: Claude first thinks about the product, then writes the image prompt.
    """
    system_prompt = """You are a professional AI image prompt engineer.
You create detailed, specific DALL-E 3 prompts that produce stunning product marketing visuals.
You always respond with valid JSON only — no markdown, no preamble."""

    user_prompt = f"""Create a DALL-E 3 image generation prompt for this product's marketing campaign.

PRODUCT:
- Name: {product_name}
- Category: {category}  
- Description: {description}
- Visual style: {style}

The image should work as a hero image for a product landing page.

Return ONLY a valid JSON object:
{{
  "dalle_prompt": "Detailed DALL-E 3 prompt (100-150 words). Include: subject, setting, lighting, mood, style, composition, color palette.",
  "negative_elements": "Elements to avoid in the image",
  "suggested_size": "1792x1024 or 1024x1024 or 1024x1792",
  "art_style_notes": "Brief note on the visual style chosen and why it fits this product"
}}"""

    return system_prompt, user_prompt


def get_available_tones():
    return ["Professional", "Playful", "Luxury", "Minimalist", "Bold & Energetic", "Friendly & Warm"]


def get_available_styles():
    return ["Photorealistic", "Minimalist flat design", "Cinematic", "Lifestyle photography", "Abstract artistic"]
