"""
app.py
------
Streamlit dashboard for the GenAI Product Marketing Automation System.
Run with: streamlit run app.py
"""

import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# Fix: ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.orchestrator import run_pipeline
from src.prompt_builder import get_available_tones, get_available_styles

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Marketing Automation",
    page_icon="✨",
    layout="wide"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.content-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    border-left: 4px solid #7C3AED;
}
.tagline-text {
    font-size: 1.6rem;
    font-weight: 700;
    color: #7C3AED;
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #f3f0ff, #ede9fe);
    border-radius: 12px;
}
.cta-button-display {
    display: inline-block;
    background: #7C3AED;
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
}
.social-card {
    background: white;
    border-radius: 8px;
    padding: 14px;
    margin: 8px 0;
    border: 1px solid #e5e7eb;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.prompt-box {
    background: #1e1e2e;
    color: #cdd6f4;
    padding: 16px;
    border-radius: 8px;
    font-family: monospace;
    font-size: 0.85rem;
    white-space: pre-wrap;
    word-break: break-word;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.title("✨ GenAI Product Marketing Automation")
st.markdown("*Generate professional marketing copy + AI image prompts for any product — powered by Claude*")
st.divider()

# ─── Sidebar — Input form ────────────────────────────────────────────────────
with st.sidebar:
    st.header("📦 Product Details")

    product_name = st.text_input(
        "Product Name *",
        placeholder="e.g. ZenMist, BrewMax, GlowFuel",
        help="The name of your product"
    )

    category = st.selectbox(
        "Category *",
        options=[
            "Skincare & Beauty",
            "Health & Wellness",
            "Tech Gadget",
            "Food & Beverage",
            "Fashion & Apparel",
            "Home & Lifestyle",
            "Fitness & Sports",
            "Pet Products",
            "Eco & Sustainable",
            "Other"
        ]
    )

    description = st.text_area(
        "Product Description *",
        placeholder="What does it do? Who is it for? What makes it special?",
        height=120,
        help="2-4 sentences about your product"
    )

    st.divider()
    st.subheader("🎨 Style Options")

    tone = st.selectbox("Copy Tone", options=get_available_tones())
    image_style = st.selectbox("Image Style", options=get_available_styles())

    st.divider()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_anthropic_api_key_here":
        st.warning("⚠️ No API key found. Add your `ANTHROPIC_API_KEY` to the `.env` file.")
        api_key_input = st.text_input("Or paste API key here:", type="password")
        if api_key_input:
            os.environ["ANTHROPIC_API_KEY"] = api_key_input

    generate_btn = st.button("🚀 Generate Content", type="primary", use_container_width=True)

# ─── Main area ───────────────────────────────────────────────────────────────

# Previous runs in session
if "history" not in st.session_state:
    st.session_state.history = []

if generate_btn:
    # Validation
    if not product_name.strip():
        st.error("Please enter a product name.")
    elif not description.strip():
        st.error("Please enter a product description.")
    elif not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Please provide your Anthropic API key.")
    else:
        with st.spinner(f"Generating content for **{product_name}**... (takes ~10 seconds)"):
            try:
                result = run_pipeline(
                    product_name=product_name,
                    category=category,
                    description=description,
                    tone=tone,
                    image_style=image_style,
                    save_output=True
                )
                st.session_state.current = result
                st.session_state.history.append({
                    "product": product_name,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "result": result
                })
                st.success("✅ Content generated successfully!")
            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                st.info("Make sure your ANTHROPIC_API_KEY is valid and you have credits.")

# ─── Results display ─────────────────────────────────────────────────────────
if "current" in st.session_state:
    result = st.session_state.current
    copy = result["copy"]
    image = result["image"]

    st.header(f"📣 Content Package — {result['product_name']}")

    # Tagline hero
    st.markdown(
        f'<div class="tagline-text">"{copy.get("tagline", "")}"</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    # Main columns
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📝 Marketing Copy")

        st.markdown("**Product Description**")
        st.markdown(
            f'<div class="content-card">{copy.get("product_description", "")}</div>',
            unsafe_allow_html=True
        )

        st.markdown("**Call to Action**")
        st.markdown(
            f'<div class="content-card"><span class="cta-button-display">{copy.get("call_to_action", "")}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown("**Key Benefits**")
        benefits = copy.get("key_benefits", [])
        for b in benefits:
            st.markdown(f"✅ {b}")

        st.markdown("**Target Audience**")
        st.info(f"👥 {copy.get('target_audience', '')}")

    with col2:
        st.subheader("📱 Social Media Captions")
        social = copy.get("social_captions", {})

        with st.expander("🐦 Twitter / X", expanded=True):
            tweet = social.get("twitter", "")
            st.markdown(f'<div class="social-card">{tweet}</div>', unsafe_allow_html=True)
            st.code(tweet, language=None)

        with st.expander("📸 Instagram", expanded=True):
            ig = social.get("instagram", "")
            st.markdown(f'<div class="social-card">{ig}</div>', unsafe_allow_html=True)
            st.code(ig, language=None)

        with st.expander("💼 LinkedIn", expanded=True):
            li = social.get("linkedin", "")
            st.markdown(f'<div class="social-card">{li}</div>', unsafe_allow_html=True)
            st.code(li, language=None)

    st.divider()

    # Image prompt section
    st.subheader("🎨 AI Image Prompt")

    img_col1, img_col2 = st.columns([2, 1])

    with img_col1:
        dalle_prompt = image.get("dalle_prompt", "")
        st.markdown("**DALL-E 3 Prompt** *(copy this into ChatGPT or Midjourney)*")
        st.markdown(
            f'<div class="prompt-box">{dalle_prompt}</div>',
            unsafe_allow_html=True
        )
        st.code(dalle_prompt, language=None)

    with img_col2:
        st.markdown("**Image Details**")
        st.markdown(f"📐 **Size:** `{image.get('suggested_size', '1792x1024')}`")
        st.markdown(f"🎭 **Style:** {result.get('image_style', '')}")
        st.markdown(f"🚫 **Avoid:** {image.get('negative_elements', 'N/A')}")
        st.markdown(f"💡 **Style Notes:** {image.get('art_style_notes', '')}")

        if image.get("generated_url"):
            st.success("🖼 Image Generated!")
            st.image(image["generated_url"], caption=f"{result['product_name']} — AI Generated")
        else:
            st.info("💡 Add OpenAI API key to `.env` for automatic DALL-E 3 image generation.")

    st.divider()

    # Export section
    st.subheader("📥 Export")
    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="⬇️ Download Full JSON",
            data=json_str,
            file_name=f"{product_name.lower().replace(' ', '_')}_content.json",
            mime="application/json",
            use_container_width=True
        )

    with exp_col2:
        # Build a markdown report
        md_report = f"""# Marketing Content — {result['product_name']}
*Generated: {result['generated_at']}*

---

## Tagline
> {copy.get('tagline', '')}

## Product Description
{copy.get('product_description', '')}

## Call to Action
**{copy.get('call_to_action', '')}**

## Key Benefits
{chr(10).join(f'- {b}' for b in copy.get('key_benefits', []))}

## Target Audience
{copy.get('target_audience', '')}

---

## Social Media Captions

### Twitter
{social.get('twitter', '')}

### Instagram
{social.get('instagram', '')}

### LinkedIn
{social.get('linkedin', '')}

---

## DALL-E 3 Image Prompt
```
{image.get('dalle_prompt', '')}
```
"""
        st.download_button(
            label="⬇️ Download Markdown Report",
            data=md_report,
            file_name=f"{product_name.lower().replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    # Token usage info
    meta = copy.get("_meta", {})
    if meta:
        with st.expander("📊 API Usage Stats"):
            st.markdown(f"- **Model:** `{meta.get('model', 'N/A')}`")
            st.markdown(f"- **Input tokens:** {meta.get('input_tokens', 0)}")
            st.markdown(f"- **Output tokens:** {meta.get('output_tokens', 0)}")
            st.markdown(f"- **Estimated cost:** ~${((meta.get('input_tokens',0)*0.25 + meta.get('output_tokens',0)*1.25)/1_000_000):.4f} USD")

# ─── History sidebar ──────────────────────────────────────────────────────────
else:
    # Welcome screen
    st.markdown("""
    ### 👈 Fill in the product details on the left to get started

    This system will generate:
    - ✍️ **Marketing tagline** — punchy, memorable
    - 📄 **Product description** — 50-word benefit-focused copy
    - 🎯 **Call-to-action** — conversion-optimized button text
    - 📱 **Social captions** — Twitter, Instagram, LinkedIn
    - 🎨 **AI image prompt** — ready for DALL-E 3 or Midjourney

    ---
    **Example products to try:**
    - ZenMist — *"A hydrating rose water face mist for dry skin"*
    - BrewMax — *"A portable espresso maker for travelers"*
    - GlowFuel — *"A vegan protein powder with collagen for women"*
    """)

if st.session_state.history:
    with st.sidebar:
        st.divider()
        st.subheader("🕐 Recent Runs")
        for item in reversed(st.session_state.history[-5:]):
            if st.button(f"📦 {item['product']} ({item['time']})", use_container_width=True, key=f"hist_{item['time']}"):
                st.session_state.current = item["result"]
                st.rerun()
