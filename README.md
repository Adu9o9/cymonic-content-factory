# ⚙️ Cymonic AI | Automated Content Factory

An autonomous, multi-agent AI pipeline that transforms raw, messy product specifications into fact-checked, brand-safe marketing assets and custom generative visuals.

🌍 **Live Demo:** [INSERT_YOUR_STREAMLIT_LINK_HERE]

## 🚀 Architecture & Engineering Decisions

- **Orchestration:** `CrewAI` manages a sequential assembly line of 4 distinct AI personas (Researcher, Copywriter, Editor, Visual Director).
- **LLM Engine (Groq vs. Gemini/OpenAI):** `Groq (Llama 3.3 70B)` was chosen specifically for this MVP. It provides blazing-fast inference speeds and a highly capable free tier, demonstrating resourcefulness and cost-efficiency without sacrificing high-tier reasoning capabilities.
- **Frontend UI ("Quiet Luxury"):** `Streamlit` natively defaults to a data-heavy, dark-mode dashboard. To meet enterprise B2B standards, aggressive custom CSS/HTML was injected to override native components, utilizing `Playfair Display`, massive whitespace, and crisp gray borders to achieve an editorial, premium UI.

## ✨ Key Features & Innovation

1. **Context-Aware Marketing:** The pipeline dynamically selects the most relevant social media platforms based on the product's target audience. (e.g., A B2B IT notification system triggers LinkedIn/X, while an anti-aging cosmetic cream drops X entirely to focus on Instagram/Facebook).
2. **Generative Visuals (The Extra Mile):** A dedicated Visual Director agent analyzes the polished campaign and generates a highly contextual prompt for `Pollinations.ai (Flux)`. It uses strict "prompt anchoring" to dynamically place typographic product names on appropriate surfaces (e.g., a frosted glass jar vs. a sleek software monitor) while minimizing AI spelling errors.

## 🛡️ Robustness: Hallucinations & HITL

A major challenge with generative marketing is LLM hallucination—inventing features, ignoring legal constraints, or making dangerous medical claims not present in the specs. This pipeline solves this using a **Human-in-the-Loop (HITL)** architecture:
* **The Anti-Hallucination Gate:** The Researcher builds a strict "Source of Truth" with explicit 'Red Flags'. The Editor agent acts as a ruthless QA gate, autonomously scrubbing unverified claims or liabilities from the Copywriter's draft.
* **The 95/5 Rule:** The AI assembly line successfully handles 95% of the heavy lifting, formatting, and risk mitigation, leaving the final 5% QA to the human operator before deployment.

## ⚠️ Known Limitations & Trade-offs

* **Image Generation Rate Limit:** The Pollinations.ai API free tier is rate-limited to **10 image generations per hour**. If this limit is exceeded, the image will fail to render (HTTP 429/401). In a production environment, this would be routed through a paid AWS/GCP image endpoint with proper error boundary fallbacks.
* **Synchronous Execution:** The CrewAI pipeline currently runs synchronously. For a massive production scale, this would be decoupled using a task queue (e.g., Celery/Redis) with WebSockets to stream granular progress to the frontend.

## 🛠️ Local Setup Instructions

If you prefer to run the architecture locally rather than using the Live Demo, follow these steps:

**1. Clone the repository:**
```bash
git clone <your-repo-url>
cd autonomous_content_factory
2. Create a virtual environment and install dependencies:

For Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
For Windows:

DOS
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Configure Environment Variables:
Create a new file named .env in the root directory and add your API keys:

Plaintext
GROQ_API_KEY="your_groq_api_key_here"
POLLINATIONS_API_KEY="your_pollinations_secret_key_here"
4. Launch the Application:

Bash
streamlit run app.py