import streamlit as st
import os
import urllib.parse
from dotenv import load_dotenv
from crewai import Crew, Process
from core.agents import ContentFactoryAgents
from core.tasks import ContentFactoryTasks

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
        
        /* Style the Primary Button */
        div[data-testid="stButton"] > button {
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
        div[data-testid="stButton"] > button:hover {
            background-color: #333333 !important;
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
    # Slightly larger, spaced-out label for the input
    st.markdown("<p style='font-family: Inter; font-size: 1rem; letter-spacing: 1.5px; color: #666; margin-bottom: 10px; margin-top: 20px; text-align: center;'>ENTER RAW SPECIFICATIONS</p>", unsafe_allow_html=True)
    
    source_text = st.text_area("HiddenLabel", height=160, label_visibility="collapsed", placeholder="E.g., The SuperWidget 3000 features a quantum processor, 16GB RAM, and all-day battery...")
    
    st.markdown("<br>", unsafe_allow_html=True) # Extra whitespace before the button
    
    # Adjusted column math to perfectly dead-center the button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.2, 1])
    with btn_col2:
        run_button = st.button("Initialize Pipeline")

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
            write_campaign = tasks.copywriting_task(copywriter, context_task=extract_truth)
            
            st.write("🛡️ **Agent 3:** Auditing against Red Flags...")
            editor = agents.editor_agent()
            audit_campaign = tasks.editing_task(editor, extract_truth, write_campaign)
            
            st.write("🎨 **Agent 4:** Generating visual prompt...")
            director = agents.visual_director_agent()
            design_visual = tasks.image_prompt_task(director, audit_task=audit_campaign)
            
            crew = Crew(
                agents=[researcher, copywriter, editor, director],
                tasks=[extract_truth, write_campaign, audit_campaign, design_visual],
                process=Process.sequential, 
                verbose=False
            )
            
            result = crew.kickoff()
            
            final_campaign_text = audit_campaign.output.raw
            image_prompt_text = design_visual.output.raw
            pollinations_key = os.environ.get("POLLINATIONS_API_KEY", "")
            safe_prompt = urllib.parse.quote(image_prompt_text.strip())
            image_url = f"https://gen.pollinations.ai/image/{safe_prompt}?model=flux&key={pollinations_key}"
            
            status.update(label="Pipeline Execution Complete", state="complete", expanded=False)

        st.markdown("<br><hr style='border: 0; height: 1px; background: #E2E8F0;'><br>", unsafe_allow_html=True)
        
        # --- RESULTS SECTION ---
        col_img, col_text = st.columns([1, 1.2], gap="large")
        
        with col_img:
            st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>Visual Asset</h3>", unsafe_allow_html=True)
            st.markdown(f'<img src="{image_url}" alt="Campaign Cover" width="100%" style="border-radius: 2px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">', unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 0.8rem; color: #888; margin-top: 10px;'><strong>Flux Prompt:</strong> {image_prompt_text}</p>", unsafe_allow_html=True)
            st.caption("⚠️ *Note: API rate-limited to 10 image generations per hour.*")
            
        with col_text:
            st.markdown("<h3 style='font-family: Playfair Display, serif; font-weight: 600; color: #111;'>Fact-Checked Copy</h3>", unsafe_allow_html=True)
            st.markdown(final_campaign_text)
            
            st.markdown("<br>", unsafe_allow_html=True)
            full_download_content = f"![Campaign Cover]({image_url})\n\n{final_campaign_text}"
            st.download_button(
                label="Download Assets (.md)",
                data=full_download_content,
                file_name="cymonic_campaign.md",
                mime="text/markdown",
            )