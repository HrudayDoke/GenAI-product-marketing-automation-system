# GenAI Product Marketing Automation System

An end-to-end Generative AI pipeline that takes a product name and description,
then automatically produces marketing copy (tagline, description, CTA, social captions)
and an AI image prompt — all displayed in an interactive Streamlit dashboard.

---

## Project Structure

```
genai-marketing-automation/
├── src/
│   ├── prompt_builder.py      # Builds structured prompts for Claude
│   ├── copy_generator.py      # Calls Claude API, parses marketing copy
│   ├── image_prompt_gen.py    # Generates DALL-E-ready image prompts
│   └── orchestrator.py        # Runs the full pipeline end-to-end
├── outputs/                   # Auto-saved JSON results per run
├── app.py                     # Streamlit dashboard (main UI)
├── requirements.txt
├── .env.example               # Copy to .env and add your keys
└── README.md
```

---

## Setup

### 1. Clone / download the project

```bash
cd genai-marketing-automation
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your API key (free tier available)

- Go to https://console.anthropic.com
- Sign up → Create API Key → copy it

### 5. Set up your environment file

```bash
cp .env.example .env
# Open .env and paste your Anthropic API key
```

### 6. Run the app

```bash
streamlit run app.py
```

---

## How It Works

1. **User inputs** a product name, category, and short description via the UI
2. **Prompt builder** constructs a detailed, structured prompt
3. **Claude API** generates a full JSON content package:
   - Tagline
   - Product description (50 words)
   - Call-to-action
   - 3 social media captions (Twitter, Instagram, LinkedIn)
   - DALL-E image prompt
4. **Streamlit dashboard** displays everything with copy buttons and export
5. **Outputs** are auto-saved as JSON in the `outputs/` folder

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude (claude-3-5-haiku) |
| Image prompts | DALL-E 3 compatible structured prompts |
| UI | Streamlit |
| Data | JSON, Pandas |
| Env management | python-dotenv |

---

## Resume Talking Points

- Built end-to-end GenAI pipeline using **prompt engineering** and **LLM API integration**
- Implemented **structured output parsing** to extract JSON from Claude responses reliably
- Designed **prompt chaining** architecture separating copy generation from image prompt generation
- Deployed interactive UI using **Streamlit** for non-technical stakeholder access
- Automated content workflows reducing manual copywriting effort by ~80%
