import streamlit as st
import json
import os
import re
import hashlib
from datetime import datetime
from tenacity import retry, wait_exponential, stop_after_attempt

# --- ABSOLUTE FIRST THING: Force LiteLLM to drop Groq's unsupported params ---
os.environ["LITELLM_DROP_PARAMS"] = "True"
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
    """Scrapes the main text content from a given URL and yields it in chunks."""
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
        
        # Yield in memory-safe 1000-character chunks
        chunk_size = 1000
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]
            
    except Exception as e:
        yield f"Error scraping URL: {str(e)}"

def chunk_text(text, chunk_size=1000):
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def run_transformation_pipeline(chunk_text_data):
    agents = ContentFactoryAgents()
    tasks = ContentFactoryTasks()
    
    researcher = agents.research_agent()
    extract_truth = tasks.extraction_task(researcher, chunk_text_data)
    
    copywriter = agents.copywriter_agent()
    draft_campaign = tasks.copywriting_task(copywriter, context_task=extract_truth)
    
    editor = agents.editor_agent()
    audit_campaign = tasks.editing_task(editor, extract_truth, draft_campaign)
    
    crew = Crew(
        agents=[researcher, copywriter, editor],
        tasks=[extract_truth, draft_campaign, audit_campaign],
        process=Process.sequential,
        max_rpm=2,
        verbose=True
    )
    crew.kickoff()
    return audit_campaign, draft_campaign

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
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="base-input"] textarea,
        textarea {
            background-color: #FFFFFF !important;
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
        
        /* Keep both tab labels visible against Streamlit's theme */
        [data-baseweb="tab"],
        [data-baseweb="tab"] p,
        [data-baseweb="tab"] span {
            color: #111111 !important;
            background-color: transparent !important;
            font-weight: 500 !important;
            font-size: 1.1rem !important;
        }
        
        /* Selected Tab - Bold and Black */
        [data-baseweb="tab"][aria-selected="true"],
        [data-baseweb="tab"][aria-selected="true"] p,
        [data-baseweb="tab"][aria-selected="true"] span {
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
    source_chunks = []
    if url_input:
        with st.spinner("Scraping website data..."):
            for chunk in scrape_website(url_input):
                if chunk.startswith("Error"):
                    st.error(chunk)
                else:
                    source_chunks.append(chunk)
            if source_chunks:
                st.success("Website successfully scraped!")
    elif source_text_input:
        source_chunks = list(chunk_text(source_text_input))
    
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
    if not source_chunks:
        st.warning("⚠️ Please provide product specifications to begin.")
    else:
        with st.status("Executing Multi-Agent ETL Pipeline...", expanded=True) as status:
            CACHE_FILE = "processed_hashes.json"
            DLQ_FILE = "quarantine_records.json"
            
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    try:
                        cache = json.load(f)
                    except:
                        cache = {}
            else:
                cache = {}
                
            dlq_count = 0
            aggregated_campaign_text = ""
            total_execution_time = 0
            overall_audit_log = {"removed_features": [], "corrected_facts": []}

            # Loop over chunks
            for i, chunk in enumerate(source_chunks):
                st.write(f"🔄 Processing Chunk {i+1}/{len(source_chunks)}...")
                chunk_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
                
                if chunk_hash in cache:
                    st.write(f"⚡ Cache Hit for Chunk {i+1} (Idempotent)")
                    result_data = cache[chunk_hash]
                    aggregated_campaign_text += result_data['campaign_text'] + "\n\n"
                    
                    if 'audit_log' in result_data:
                        overall_audit_log['removed_features'].extend(result_data['audit_log'].get('removed_features', []))
                        overall_audit_log['corrected_facts'].extend(result_data['audit_log'].get('corrected_facts', []))
                    continue
                
                # Cache miss
                st.write(f"🚀 Transforming Chunk {i+1} via Multi-Agent Crew...")
                start_time = time.time()
                try:
                    audit_campaign, draft_campaign = run_transformation_pipeline(chunk)
                    end_time = time.time()
                    total_execution_time += round(end_time - start_time, 2)
                    
                    def clean_think_tags(text):
                        if not text:
                            return ""
                        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
                        return re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL).strip()

                    raw_output = clean_think_tags(audit_campaign.output.raw)
                    copywriter_draft = clean_think_tags(draft_campaign.output.raw)

                    if "===AUDIT_LOG===" in raw_output:
                        parts = raw_output.split("===AUDIT_LOG===")
                        final_campaign_text = parts[0].strip() or copywriter_draft
                        try:
                            json_str = parts[1].replace("```json", "").replace("```", "").strip()
                            audit_log_data = json.loads(json_str)
                        except Exception:
                            audit_log_data = {"removed_features": [], "corrected_facts": []}
                    else:
                        final_campaign_text = raw_output.replace("```json", "").replace("```", "").strip()
                        if not final_campaign_text or "i need the draft" in final_campaign_text.lower():
                            final_campaign_text = copywriter_draft
                        audit_log_data = {"removed_features": [], "corrected_facts": []}
                        
                    # Save to cache
                    result_data = {
                        "campaign_text": final_campaign_text,
                        "audit_log": audit_log_data
                    }
                    cache[chunk_hash] = result_data
                    with open(CACHE_FILE, 'w') as f:
                        json.dump(cache, f, indent=4)
                        
                    aggregated_campaign_text += final_campaign_text + "\n\n"
                    overall_audit_log['removed_features'].extend(audit_log_data.get('removed_features', []))
                    overall_audit_log['corrected_facts'].extend(audit_log_data.get('corrected_facts', []))
                    
                except Exception as e:
                    dlq_count += 1
                    st.write(f"❌ Chunk {i+1} failed after retries. Routing to DLQ.")
                    error_entry = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": chunk,
                        "error_message": str(e)
                    }
                    if os.path.exists(DLQ_FILE):
                        with open(DLQ_FILE, 'r') as f:
                            try:
                                dlq = json.load(f)
                            except:
                                dlq = []
                    else:
                        dlq = []
                    dlq.append(error_entry)
                    with open(DLQ_FILE, 'w') as f:
                        json.dump(dlq, f, indent=4)
            
            if dlq_count > 0:
                st.warning(f"Pipeline finished with {dlq_count} record(s) routed to DLQ.")
                
            if not aggregated_campaign_text.strip():
                st.error("Pipeline failed to generate any valid campaign content. Check DLQ.")
            else:
                st.write("🎨 **Generating final visual asset from aggregated results...**")
                agg_hash = hashlib.sha256(aggregated_campaign_text.encode('utf-8')).hexdigest()
                final_image_url = None
                final_prompt = None
                
                if agg_hash in cache and 'image_url' in cache[agg_hash] and cache[agg_hash]['image_url']:
                    st.write("⚡ Cache Hit for Final Image")
                    final_image_url = cache[agg_hash]['image_url']
                    final_prompt = cache[agg_hash].get('prompt', '')
                else:
                    from crewai import Task
                    agents = ContentFactoryAgents()
                    visual_director = agents.visual_director_agent()
                    
                    image_task = Task(
                        description=f"Read the following campaign text: {aggregated_campaign_text[:1500]}. Output a 30-word image generation prompt. Ask to write the Product Name subtly on a relevant physical surface.",
                        expected_output="A single sentence image prompt.",
                        agent=visual_director
                    )
                    image_crew = Crew(
                        agents=[visual_director],
                        tasks=[image_task],
                        process=Process.sequential,
                        verbose=True
                    )
                    image_crew.kickoff()
                    
                    def clean_think_tags_final(text):
                        if not text:
                            return ""
                        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
                        return re.sub(r"<think>.*", "", cleaned, flags=re.DOTALL).strip()
                        
                    final_prompt = clean_think_tags_final(image_task.output.raw)
                    pollinations_key = os.environ.get("POLLINATIONS_API_KEY", "")
                    safe_prompt = urllib.parse.quote(final_prompt.strip())
                    final_image_url = f"https://gen.pollinations.ai/image/{safe_prompt}?model=flux&key={pollinations_key}"
                    
                    cache[agg_hash] = {
                        "image_url": final_image_url,
                        "prompt": final_prompt
                    }
                    with open(CACHE_FILE, 'w') as f:
                        json.dump(cache, f, indent=4)
                
                st.session_state.campaign_data = {
                    "image_url": final_image_url or "https://via.placeholder.com/600x400?text=No+Image",
                    "prompt": final_prompt or "N/A",
                    "time": total_execution_time,
                    "audit_log": overall_audit_log
                }
                st.session_state.text_vault = aggregated_campaign_text.strip()
                
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