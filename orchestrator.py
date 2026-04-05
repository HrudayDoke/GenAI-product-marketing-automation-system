"""
orchestrator.py
---------------
Runs the full GenAI content automation pipeline end-to-end.
Coordinates: copy generation → image prompt generation → output packaging → save to disk.

Can be run directly from the CLI:
  python -m src.orchestrator --product "ZenMist" --category "skincare" --description "A hydrating face mist"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Fix: ensure project root is on path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from src.copy_generator import generate_marketing_copy
from src.image_prompt_gen import generate_image_prompt, generate_image_with_dalle


def run_pipeline(
    product_name: str,
    category: str,
    description: str,
    tone: str = "Professional",
    image_style: str = "Photorealistic",
    save_output: bool = True
) -> dict:
    """
    Full pipeline: input → Claude copy → Claude image prompt → [optional DALL-E] → packaged output.

    Args:
        product_name: e.g. "ZenMist"
        category: e.g. "skincare"
        description: e.g. "A hydrating rose water face mist for dry skin"
        tone: Writing tone for copy
        image_style: Visual style for image prompt
        save_output: If True, saves JSON to outputs/ folder

    Returns:
        Complete content package as dict
    """
    print(f"\n🚀 Starting pipeline for: {product_name}")
    print("─" * 50)

    # Step 1: Generate marketing copy
    print("📝 Step 1/3 — Generating marketing copy via Claude...")
    copy_data = generate_marketing_copy(product_name, category, description, tone)
    print(f"   ✓ Generated: tagline, description, CTA, social captions")
    print(f"   ✓ Tokens used: {copy_data['_meta']['input_tokens']} in / {copy_data['_meta']['output_tokens']} out")

    # Step 2: Generate image prompt
    print("🎨 Step 2/3 — Generating image prompt via Claude...")
    image_data = generate_image_prompt(product_name, category, description, image_style)
    print(f"   ✓ DALL-E prompt generated ({len(image_data['dalle_prompt'])} chars)")

    # Step 3: Attempt DALL-E image generation (optional)
    print("🖼  Step 3/3 — Attempting image generation...")
    image_url = generate_image_with_dalle(
        image_data["dalle_prompt"],
        image_data.get("suggested_size", "1792x1024")
    )
    if image_url:
        print(f"   ✓ Image generated: {image_url[:60]}...")
    else:
        print("   ℹ  No OpenAI key found — skipping DALL-E (image prompt still saved)")

    # Package full output
    output = {
        "product_name": product_name,
        "category": category,
        "description": description,
        "tone": tone,
        "image_style": image_style,
        "generated_at": datetime.now().isoformat(),
        "copy": copy_data,
        "image": {
            **image_data,
            "generated_url": image_url
        }
    }

    # Save to disk
    if save_output:
        os.makedirs("outputs", exist_ok=True)
        filename = f"outputs/{product_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n✅ Output saved to: {filename}")

    return output


def print_summary(output: dict):
    """Pretty-prints a pipeline result to the terminal."""
    copy = output["copy"]
    image = output["image"]

    print("\n" + "═" * 50)
    print(f"  CONTENT PACKAGE — {output['product_name'].upper()}")
    print("═" * 50)
    print(f"\n  Tagline:     {copy.get('tagline', 'N/A')}")
    print(f"  CTA:         {copy.get('call_to_action', 'N/A')}")
    print(f"  Audience:    {copy.get('target_audience', 'N/A')}")
    print(f"\n  Description:\n  {copy.get('product_description', 'N/A')}")
    print(f"\n  Twitter:  {copy.get('social_captions', {}).get('twitter', 'N/A')}")
    print(f"\n  DALL-E Prompt (first 120 chars):\n  {image.get('dalle_prompt', 'N/A')[:120]}...")
    print("\n" + "═" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GenAI Marketing Content Pipeline")
    parser.add_argument("--product", required=True, help="Product name")
    parser.add_argument("--category", required=True, help="Product category")
    parser.add_argument("--description", required=True, help="Product description")
    parser.add_argument("--tone", default="Professional", help="Writing tone")
    parser.add_argument("--style", default="Photorealistic", help="Image style")
    args = parser.parse_args()

    result = run_pipeline(
        product_name=args.product,
        category=args.category,
        description=args.description,
        tone=args.tone,
        image_style=args.style
    )
    print_summary(result)
