# ⚙️ Autonomous Content Factory

🌍 **Live Demo:** [INSERT_YOUR_STREAMLIT_LINK_HERE]
▶️ **Video Walkthrough:** [INSERT_YOUTUBE_OR_LOOM_LINK_HERE]

## The Problem
When product features launch, Marketing teams must manually repurpose technical specifications into blogs, social threads, and emails. This repetitive manual rewriting causes creative burnout, delays product launches, and introduces critical factual errors and inconsistent tones across different platforms.

## The Solution
An autonomous, multi-agent AI pipeline that transforms raw, messy product specifications into fact-checked, brand-safe marketing assets and custom generative visuals. 

While the minimum requirement requested a 2-agent system, this solution goes the "Extra Mile" by implementing a **4-Agent Human-in-the-Loop (HITL) Architecture**:
1. **Fact-Check & Research Agent:** Extracts specs and builds a strict "Source of Truth" Fact-Sheet, explicitly flagging ambiguous red flags.
2. **Creative Copywriter Agent:** Generates a 500-word blog, a 5-post social media thread, and an email teaser, dynamically adjusting tone.
3. **Editor Agent (Anti-Hallucination Gate):** Autonomously cross-references the copywriter's draft against the Fact-Sheet's red flags, scrubbing unverified claims before the user sees it.
4. **Visual Director Agent:** Analyzes the polished copy and generates a highly contextual prompt to render a custom product image.

## Tech Stack
* **Programming Language:** Python 3.11
* **Frontend Framework:** Streamlit (with custom CSS/HTML injections for an editorial B2B UI)
* **Agent Orchestration:** CrewAI
* **LLM Engine:** Groq API (Llama 3.3 70B) via LiteLLM routing
* **Image Generation API:** Pollinations.ai (Flux Model)

## Setup Instructions

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
Known Limitations & Trade-offs
API Rate Limiting: The Pollinations.ai API free tier is rate-limited to 10 image generations per hour.

Text/URL Ingestion: Currently optimized for raw text pasting. Future iterations would include a BeautifulSoup4 scraper to ingest URLs directly.