# ⚙️ CYMONIC: Autonomous Content Factory

🌍 **Live Demo:** [INSERT_YOUR_STREAMLIT_LINK_HERE]
▶️ **Video Walkthrough:** [INSERT_YOUTUBE_OR_LOOM_LINK_HERE]

## The Problem
When product features launch, Marketing teams must manually repurpose technical specifications into blogs, social threads, and emails. This repetitive manual rewriting causes creative burnout, delays product launches, and introduces critical factual errors and inconsistent tones across different platforms.

## The Solution
An autonomous, multi-agent AI pipeline that transforms raw, messy product specifications into fact-checked, brand-safe marketing assets and custom generative visuals. 

While the minimum requirement requested a basic 2-agent system, this solution goes the "Extra Mile" by implementing a **4-Agent Human-in-the-Loop (HITL) Architecture** with an enterprise-grade UI:
1. **Fact-Check & Research Agent:** Extracts specs and builds a strict "Source of Truth" Fact-Sheet, explicitly flagging ambiguous red flags.
2. **Creative Copywriter Agent:** Generates a highly-formatted 500-word blog, a platform-specific social media thread, and an A/B tested email teaser sequence.
3. **Editor Agent (Anti-Hallucination Gate):** Autonomously cross-references the copywriter's draft against the Fact-Sheet's red flags, scrubbing unverified claims before the user sees it.
4. **Visual Director Agent:** Analyzes the polished copy and generates a highly contextual, typography-safe prompt to render a custom product image.

## 🚀 "Extra Mile" Features Implemented
* **Dynamic Web Scraping:** Integrated BeautifulSoup4 to ingest messy HTML product pages directly via URL, bypassing the need for manual copy-pasting.
* **A/B Testing Engine:** The copywriter autonomously generates two distinct psychological email variants (Logic-Driven vs. Emotion-Driven) for campaign testing.
* **Human-in-the-Loop (HITL) Editor:** A custom Streamlit session-state toggle that transforms the read-only markdown into a live, editable text area, allowing human review before export.
* **Execution Analytics Dashboard:** Real-time metrics tracking agent assembly speed and compute costs, demonstrating a focus on B2B cloud economics.
* **Bespoke UI/CSS:** Heavy CSS injection to override Streamlit's default components, creating a "Quiet Luxury", enterprise-grade Dark/Light aesthetic.

## Tech Stack
* **Programming Language:** Python 3.11
* **Frontend Framework:** Streamlit 
* **Agent Orchestration:** CrewAI
* **LLM Engine:** Groq API (Llama 3.3 70B) for ultra-fast, zero-cost inference
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
Image API Rate Limiting: The Pollinations.ai API free tier is rate-limited to 10 image generations per hour.

Context Window Limits: The web scraper automatically truncates HTML text to 2,500 characters to prevent Groq's 12k TPM rate limits from crashing the multi-agent cascade.