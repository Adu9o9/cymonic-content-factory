import streamlit as st
import json
import os
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from crewai import Crew, Process
from core.agents import ContentFactoryAgents
from core.tasks import ContentFactoryTasks

# --- AI ROUTING FIX: Strip unsupported params for Groq ---
import litellm
litellm.drop_params = True

def scrape_website(url):
    """Scrapes the main text content from a given URL."""
    try:
        # Pretend to be a normal web browser so websites don't block us
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip away the messy code, navbars, and scripts
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Get the clean text
        text = soup.get_text(separator=' ', strip=True)
        return text[:2500] # Reduced from 5000 to prevent Groq 12k TPM Rate Limits!
        
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

load_dotenv()

st.set_page_config(page_title="Cymonic AI | Content Factory", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

# --- MASSIVE CSS OVERRIDE & FONT IMPORTS ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        /* Hide the default Streamlit header */
        [data-testid="stHeader"] { display: none; }
        
        /* Force clean white background globally */
        .stApp {
            background-color: #FDFDFD !important;
            color: #1A1A1A !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Add massive breathing room at the top and bottom */
        .block-container {
            padding-top: 4rem !important;
            padding-bottom: 5rem !important;
            max-width: 1100px;
        }
        
        /* Force Text Area to be light, with larger font and more internal padding */
        div[data-baseweb="textarea"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 4px !important;
            padding: 0.5rem !important;
        }
        textarea {
            color: #1A1A1A !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
            caret-color: #2563EB !important; /* <-- This fixes the invisible typing cursor! */
        }
        /* Force the placeholder text to be visible and gray */
        textarea::placeholder {
            color: #888888 !important;
            opacity: 1 !important;
        }
        input::placeholder {
            color: #888888 !important;
            opacity: 1 !important;
        }
        
        /* Style the Primary Button ONLY */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 500 !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            font-size: 0.85rem !important;
            padding: 0.75rem 2rem !important;
            width: 100%;
            transition: background-color 0.3s ease;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #333333 !important;
        }

        /* Style Secondary Buttons (Like the Upload Sample Data button) */
        div[data-testid="stButton"] button[kind="secondary"] {
            background-color: transparent !important;
            color: #111111 !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 4px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover {
            background-color: #F3F4F6 !important;
            border-color: #9CA3AF !important;
        }
        
        /* Style the Download Button slightly differently */
        div[data-testid="stDownloadButton"] > button {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
            border: 1px solid #1A1A1A !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: #F3F4F6 !important;
        }

        /* Center the tabs and space them out */
        [data-baseweb="tab-list"] {
            justify-content: center;
            gap: 2rem;
            border-bottom: 1px solid #e0e0e0;
        }
        
        /* Unselected Tab - Gray but completely visible */
        [data-baseweb="tab"] {
            color: #888888 !important;
            background-color: transparent !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
        }
        
        /* Selected Tab - Bold and Black */
        [aria-selected="true"] {
            color: #111111 !important;
            font-weight: 700 !important;
            /* We deleted the manual border-bottom from here! */
        }
        
        /* Force the native sliding tab indicator to be Black instead of Red */
        div[data-baseweb="tab-highlight"] {
            background-color: #111111 !important;
        }
        /* Fix the URL Input Box to be White like the Text Area */
        .stTextInput input {
            background-color: #ffffff !important;
            color: #111111 !important;
            caret-color: #111111 !important; /* <--- This brings the blinking cursor back! */
            border: 1px solid #cccccc !important;
            border-radius: 4px !important;
        }

        /* --- Fix Metric Dashboard Visibility & Styling --- */
        [data-testid="stMetricValue"] {
            color: #111111 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            margin-top: 12px !important; /* This adds the beautiful spacing from the label! */
        }
        [data-testid="stMetricLabel"] {
            color: #666666 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }
        [data-testid="stMetricDelta"] {
            color: #555555 !important;
            font-weight: 500 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }
        /* --- Fix Alert & Warning Box Text Colors --- */
        div[data-testid="stAlert"] * {
            color: #1A1A1A !important;
        }
        
        /* Ensure the icons inside the boxes don't get overridden by the dark color */
        div[data-testid="stAlert"] svg {
            fill: inherit !important;
        }
        /* --- Foolproof Toggle Visibility --- */
        [data-testid="stToggle"] div[data-baseweb="checkbox"] > div:first-child {
            background-color: #E2E8F0 !important;
            border: 2px solid #CBD5E1 !important; /* Forces a visible outline! */
        }
    </style>
""", unsafe_allow_html=True)

# --- EDITORIAL HERO SECTION ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem; margin-top: 1rem;">
        <h1 style="font-family: 'Playfair Display', serif; font-size: 6rem; font-weight: 400; color: #111111; margin-bottom: -15px; letter-spacing: -2px;">CYMONIC</h1>
        <p style="font-family: 'Inter', sans-serif; font-weight: 300; font-size: 1.2rem; color: #555555; letter-spacing: 2px; text-transform: uppercase;">Automated Content Factory</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN INTERFACE ---
col_spacer1, col_main, col_spacer2 = st.columns([1, 4, 1])

with col_main:
    # --- INPUT SECTION WITH TABS ---
    st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>ENTER RAW SPECIFICATIONS</h3>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Paste Text", "🌐 Scrape URL"])
    
    with tab1:
        def apply_sample_text():
            st.session_state.my_raw_text = (
                "Introducing the new SuperWidget 3000! It features a quantum processor "
                "and is literally the fastest tool on the market. It has 16GB of RAM and a battery "
                "that lasts all day, maybe even two days depending on how you use it. "
                "Perfect for enterprise software developers. We might add a cloud sync feature later this year."
            )

        st.markdown("<br>", unsafe_allow_html=True)

        samp_col1, samp_col2, samp_col3 = st.columns([1, 1.5, 1])
        with samp_col2:
            st.button("Upload Sample Data", on_click=apply_sample_text, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        source_text_input = st.text_area(
            label="Raw Text Input",
            label_visibility="collapsed",
            key="my_raw_text",
            height=200,
            placeholder=(
                "Example: Introducing the new SuperWidget 3000! It features a quantum processor "
                "and is literally the fastest tool on the market. It has 16GB of RAM and a battery "
                "that lasts all day, maybe even two days depending on how you use it. "
                "Perfect for enterprise software developers. We might add a cloud sync feature later this year."
            )
        )
        
    with tab2:
        url_input = st.text_input("Product Website URL", placeholder="e.g., https://www.apple.com/macbook-pro/")
        st.caption("The AI will invisibly scrape and read the webpage for you. *(Find a product page online, e.g., a smartwatch on Amazon or a software tool's landing page, and paste the URL here)*")

    # Determine which input to use
    source_text = ""
    if url_input:
        with st.spinner("Scraping website data..."):
            source_text = scrape_website(url_input)
            if "Error" in source_text:
                st.error(source_text)
                source_text = "" # Reset if it failed
            else:
                st.success("Website successfully scraped!")
    elif source_text_input:
        source_text = source_text_input
    
    st.markdown("<br>", unsafe_allow_html=True) # Extra whitespace before the button
    
    # Adjusted column math to perfectly dead-center the button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.2, 1])
    with btn_col2:
        run_button = st.button("Initialize Pipeline", type="primary")

# --- INITIALIZE MEMORY ---
# This prevents the UI from wiping out when you click the toggle
if "campaign_data" not in st.session_state:
    st.session_state.campaign_data = None
if "text_vault" not in st.session_state:
    st.session_state.text_vault = ""

if run_button:
    if not source_text.strip():
        st.warning("⚠️ Please provide product specifications to begin.")
    else:
        with st.status("Executing Multi-Agent Pipeline...", expanded=True) as status:
            st.write("🕵️‍♂️ **Agent 1:** Extracting Source of Truth...")
            agents = ContentFactoryAgents()
            tasks = ContentFactoryTasks()
            researcher = agents.research_agent()
            extract_truth = tasks.extraction_task(researcher, source_text)
            
            st.write("✍️ **Agent 2:** Drafting multi-channel campaign...")
            copywriter = agents.copywriter_agent()
            draft_campaign = tasks.copywriting_task(copywriter, context_task=extract_truth)
            
            st.write("🛡️ **Agent 3:** Auditing against Red Flags...")
            editor = agents.editor_agent()
            audit_campaign = tasks.editing_task(editor, extract_truth, draft_campaign)
            
            st.write("🎨 **Agent 4:** Generating visual prompt...")
            visual_director = agents.visual_director_agent()
            design_visual = tasks.image_prompt_task(visual_director, audit_task=audit_campaign)
            
            st.write("🚀 **Pipeline:** Initiating multi-agent collaboration...")
            crew = Crew(
                agents=[researcher, copywriter, editor, visual_director],
                tasks=[extract_truth, draft_campaign, audit_campaign, design_visual],
                verbose=True
            )
            
            # --- THE STOPWATCH ---
            start_time = time.time()
            result = crew.kickoff()
            end_time = time.time()
            execution_time = round(end_time - start_time, 2)

            raw_output = audit_campaign.output.raw
            image_prompt_text = design_visual.output.raw

            # --- AI GUARDRAIL: DELIMITER PARSING ---
            if "===AUDIT_LOG===" in raw_output:
                parts = raw_output.split("===AUDIT_LOG===")
                final_campaign_text = parts[0].strip()

                try:
                    json_str = parts[1].replace("```json", "").replace("```", "").strip()
                    audit_log_data = json.loads(json_str)
                except Exception:
                    audit_log_data = {"removed_features": [], "corrected_facts": []}
            else:
                final_campaign_text = raw_output.replace("```json", "").replace("```", "")
                audit_log_data = {"removed_features": [], "corrected_facts": []}
            pollinations_key = os.environ.get("POLLINATIONS_API_KEY", "")
            safe_prompt = urllib.parse.quote(image_prompt_text.strip())
            image_url = f"https://gen.pollinations.ai/image/{safe_prompt}?model=flux&key={pollinations_key}"
            
            # --- SAVE TO MEMORY ---
            st.session_state.campaign_data = {
                "image_url": image_url,
                "prompt": image_prompt_text,
                "time": execution_time,
                "audit_log": audit_log_data
            }
            # Lock the initial AI output into the vault
            st.session_state.text_vault = final_campaign_text
            
            status.update(label="Pipeline Execution Complete", state="complete", expanded=False)

# --- RENDER RESULTS FROM MEMORY ---
# This block runs even after a toggle interaction because the data is saved
if st.session_state.campaign_data:
    data = st.session_state.campaign_data
    
    st.markdown("<br><hr style='border: 0; height: 1px; background: #E2E8F0;'><br>", unsafe_allow_html=True)
    
    # --- RESULTS SECTION ---
    col_img, col_text = st.columns([1, 1.2], gap="large")

    # === LEFT COLUMN: Image & Audit Log ===
    with col_img:
        st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>Visual Asset</h3>", unsafe_allow_html=True)
        st.markdown(
            f'<img src="{data["image_url"]}" alt="Campaign Cover" width="100%" style="border-radius: 2px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">',
            unsafe_allow_html=True
        )
        st.markdown(
            f"<p style='font-size: 0.8rem; color: #888; margin-top: 10px;'><strong>Flux Prompt:</strong> {data['prompt']}</p>",
            unsafe_allow_html=True
        )
        st.caption("⚠️ *Note: API rate-limited to 10 image generations per hour.*")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>🛡️ AI Audit Log</h3>", unsafe_allow_html=True)
        st.caption("Active guardrails filtered these claims before production.")

        audit_log = data.get("audit_log") if isinstance(data.get("audit_log"), dict) else {}
        removed_items = audit_log.get("removed_features", []) if isinstance(audit_log.get("removed_features"), list) else []
        corrected_items = audit_log.get("corrected_facts", []) if isinstance(audit_log.get("corrected_facts"), list) else []

        if not removed_items:
            st.success("✅ No unverified claims found.")
        else:
            for item in removed_items:
                st.error(
                    f"❌ **Removed:** {item.get('feature', 'Unknown')}  \n*Reason:* {item.get('reason', 'Failed validation')}"
                )

        if corrected_items:
            for item in corrected_items:
                st.warning(
                    f"🔄 **Changed:** '{item.get('original', '')}' ➡️ '{item.get('corrected', '')}'"
                )

    # === RIGHT COLUMN: Campaign Copy & Fixed Toggle ===
    with col_text:
        header_col, toggle_col = st.columns([0.8, 0.2])
        with header_col:
            st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>Fact-Checked Copy</h3>", unsafe_allow_html=True)
        with toggle_col:
            edit_mode = st.toggle("✏️ Edit Mode")

        st.markdown("---")

        def save_edits():
            st.session_state.text_vault = st.session_state.temp_editor

        if edit_mode:
            st.info("💡 **Human-in-the-Loop:** Edit your campaign below. Toggle off to preview the final format.")
            st.text_area(
                label="Campaign Editor",
                value=st.session_state.text_vault,
                key="temp_editor",
                on_change=save_edits,
                height=600,
                label_visibility="collapsed"
            )
        else:
            st.markdown(st.session_state.text_vault)

        st.markdown("<br>", unsafe_allow_html=True)

        full_download_content = f"![Campaign Cover]({data['image_url']})\n\n{st.session_state.text_vault}"
        st.download_button(
            label="💾 Download Campaign (.md)",
            data=full_download_content,
            file_name="cymonic_campaign.md",
            mime="text/markdown",
            use_container_width=True
        )

    # --- EXECUTION ANALYTICS WIDGET ---
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: Playfair Display; color: #111;'>📊 Pipeline Execution Analytics</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="⏱️ Assembly Line Speed", value=f"{data['time']} sec")

    with col2:
        st.metric(label="🤖 Agents Orchestrated", value="4 Autonomous Nodes")

    with col3:
        st.metric(label="💰 Est. Compute Cost", value="$0.00", delta="-100% vs OpenAI")