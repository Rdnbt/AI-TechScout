import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path so we can import tech_scout modules
sys.path.append(os.getcwd())

from tech_scout.llm import create_client, AVAILABLE_LLMS
from tech_scout.scout_technologies import scout_technologies, generate_search_queries
from tech_scout.evaluate_technologies import batch_evaluate_technologies
from tech_scout.generate_report import generate_scouting_report

# Page Config
st.set_page_config(
    page_title="AI-TechScout Dashboard",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern startup look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide default streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
        min-width: 320px !important;
        width: 320px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        width: 320px !important;
        min-width: 320px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e0e0e0;
    }
    
    /* Sidebar text overflow fix */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] {
        min-width: 0 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Glass card effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Paragraph and label text */
    p, label, .stMarkdown {
        color: #b0b0b0 !important;
    }
    
    /* Primary buttons with gradient */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Selectbox */
    [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 8px;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #888 !important;
        font-weight: 500;
        padding: 12px 24px;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px !important;
        border: none !important;
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border-left: 4px solid #10b981 !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1) !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1) !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
    }
    
    /* Multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 8px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
    }
    
    [data-testid="metric-container"] label {
        color: #888 !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e0e0e0 !important;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: #667eea !important;
    }
    
    /* Custom hero section */
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 100px;
        padding: 6px 16px;
        font-size: 0.85rem;
        color: #a78bfa;
        margin-bottom: 16px;
        font-weight: 500;
    }
    
    /* Glowing orb decorations */
    .glow-orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.3;
        pointer-events: none;
        z-index: -1;
    }
    
    .glow-orb-1 {
        width: 400px;
        height: 400px;
        background: #667eea;
        top: -100px;
        right: -100px;
    }
    
    .glow-orb-2 {
        width: 300px;
        height: 300px;
        background: #764ba2;
        bottom: -50px;
        left: -50px;
    }
    
    /* Status indicator dots */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-dot.active {
        background: #10b981;
    }
    
    .status-dot.inactive {
        background: #ef4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>

<!-- Decorative glow orbs -->
<div class="glow-orb glow-orb-1"></div>
<div class="glow-orb glow-orb-2"></div>
""", unsafe_allow_html=True)

# Session State Initialization
if 'technologies' not in st.session_state:
    st.session_state.technologies = []
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = []
if 'scouting_results' not in st.session_state:
    st.session_state.scouting_results = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Discovery"

# Sidebar Configuration
with st.sidebar:
    # Logo and branding
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 48px; margin-bottom: 8px;">🔭</div>
        <h2 style="margin: 0; font-size: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TechScout AI</h2>
        <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #666;">Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Configuration Section
    st.markdown('<p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #667eea !important; font-weight: 600; margin-bottom: 12px;">Configuration</p>', unsafe_allow_html=True)
    
    # Template Selection
    template_dir = "templates/tech_scout"
    templates = [d for d in os.listdir(template_dir) if os.path.isdir(os.path.join(template_dir, d))]
    selected_template = st.selectbox("📋 Template", ["Custom"] + templates, help="Choose a pre-configured domain template")
    
    # Model Selection
    selected_model = st.selectbox("🤖 AI Model", AVAILABLE_LLMS, index=AVAILABLE_LLMS.index("gpt-4o") if "gpt-4o" in AVAILABLE_LLMS else 0, help="Select the language model for analysis")
    
    st.markdown("---")
    
    # API Status with custom styling
    st.markdown('<p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #667eea !important; font-weight: 600; margin-bottom: 12px;">API Status</p>', unsafe_allow_html=True)
    
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "SerpAPI": os.getenv("SERPAPI_KEY"),
        "Semantic Scholar": os.getenv("S2_API_KEY")
    }
    
    for key, value in api_keys.items():
        status_class = "active" if value else "inactive"
        status_text = "Connected" if value else "Missing"
        st.markdown(f'''
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 8px; margin-bottom: 6px;">
            <span style="color: #888; font-size: 0.85rem;">{key}</span>
            <span style="display: flex; align-items: center; font-size: 0.75rem; color: {"#10b981" if value else "#666"};">
                <span class="status-dot {status_class}"></span>{status_text}
            </span>
        </div>
        ''', unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Output Section
    st.markdown('<p style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #667eea !important; font-weight: 600; margin-bottom: 12px;">Output</p>', unsafe_allow_html=True)
    output_dir = st.text_input("📁 Results Directory", "./scouting_results")
    os.makedirs(output_dir, exist_ok=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 16px 0;">
        <p style="font-size: 0.7rem; color: #444 !important;">Built with ❤️ by your team</p>
        <p style="font-size: 0.65rem; color: #333 !important;">v2.0.0 • 2026</p>
    </div>
    """, unsafe_allow_html=True)

# Utils
def load_template_config(template_name):
    if template_name == "Custom":
        return {"focus_areas": [], "domain": ""}
    
    path = os.path.join(template_dir, template_name)
    config = {"focus_areas": [], "domain": ""}
    
    if os.path.exists(os.path.join(path, "prompt.json")):
        with open(os.path.join(path, "prompt.json")) as f:
            p = json.load(f)
            config["domain"] = p.get("domain", "")
            config["focus_areas"] = p.get("focus_areas", [])
            
    return config

# Load config based on selection
template_config = load_template_config(selected_template)

# Main Application
st.markdown("""
<div style="margin-bottom: 32px;">
    <span class="hero-badge">✨ AI-Powered Intelligence</span>
    <h1 style="margin: 0 0 8px 0;">Technology Scouting Dashboard</h1>
    <p style="font-size: 1.1rem; color: #666 !important; margin: 0; max-width: 600px;">Discover, evaluate, and track emerging technologies with AI-driven insights and comprehensive analysis.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Discovery", "📊 Evaluation", "📄 Reports"])

# === TAB 1: DISCOVERY ===
with tab1:
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0; font-size: 1.2rem;">🎯 Configure Scout</h3>', unsafe_allow_html=True)
        
        domain = st.text_input("Technology Domain", value=template_config.get("domain", ""), placeholder="e.g. Generative AI, Quantum Computing")
        focus_areas_str = st.text_area("Focus Areas", value=",".join(template_config.get("focus_areas", [])), height=120, placeholder="Enter focus areas separated by commas...")
        focus_areas = [f.strip() for f in focus_areas_str.split(",") if f.strip()]
        
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        start_scout = st.button("🚀 Launch Scout Mission", use_container_width=True, type="primary")
        
        st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        if st.button("📂 Load Previous Results", use_container_width=True):
            try:
                res_path = os.path.join(output_dir, "scouting_results.json")
                if os.path.exists(res_path):
                    with open(res_path, 'r') as f:
                        data = json.load(f)
                        st.session_state.scouting_results = data
                        st.session_state.technologies = data.get("technologies", [])
                    st.success(f"✅ Loaded {len(st.session_state.technologies)} technologies")
                else:
                    st.warning("No previous results found in the output directory.")
            except Exception as e:
                st.error(f"Error loading results: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-top: 0; font-size: 1.2rem;">📡 Results</h3>', unsafe_allow_html=True)
        
        if start_scout:
            if not domain:
                st.warning("⚠️ Please enter a technology domain to begin.")
            else:
                try:
                    with st.spinner(f"🔍 Scanning for {domain} technologies..."):
                        # Initialize Client
                        client, model_name = create_client(selected_model)
                        
                        # Generate search queries first
                        st.info("🧠 Generating intelligent search queries...")
                        search_queries = generate_search_queries(
                            client=client,
                            model=selected_model,
                            domain=domain,
                            focus_areas=focus_areas if focus_areas else [domain],
                            num_queries=10
                        )
                        
                        if not search_queries:
                            st.warning("Could not generate search queries. Using domain as fallback.")
                            search_queries = [domain] + focus_areas
                        
                        # Run Scouting
                        results = scout_technologies(
                            base_dir=output_dir,
                            client=client,
                            model=selected_model,
                            domain=domain,
                            focus_areas=focus_areas if focus_areas else [domain],
                            search_queries=search_queries,
                            skip_search=False,
                            num_reflections=2,
                            year_lookback=3
                        )
                        
                        st.session_state.scouting_results = results
                        st.session_state.technologies = results.get("technologies", [])
                        st.success(f"🎉 Mission Complete! Discovered {len(st.session_state.technologies)} technologies.")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ Mission failed: {str(e)}")
                    with st.expander("View Error Details"):
                        st.exception(e)

        # Display Results
        if st.session_state.technologies:
            tech_df = pd.DataFrame(st.session_state.technologies)
            if not tech_df.empty:
                # Metrics row
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Technologies Found", len(tech_df))
                with m2:
                    avg_year = int(tech_df['year'].mean()) if 'year' in tech_df.columns else "N/A"
                    st.metric("Avg. Year", avg_year)
                with m3:
                    st.metric("Domain", domain[:15] + "..." if len(domain) > 15 else domain)
                
                st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
                
                # Data table
                cols = [c for c in ['name', 'description', 'year'] if c in tech_df.columns]
                st.dataframe(tech_df[cols], use_container_width=True, height=300)
                
                with st.expander("🔍 View Raw JSON Data"):
                    st.json(st.session_state.technologies)
            else:
                st.info("No technologies discovered in this scan.")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; color: #666;">
                <div style="font-size: 48px; margin-bottom: 16px;">🛰️</div>
                <p style="font-size: 1.1rem; margin-bottom: 8px;">Ready for Launch</p>
                <p style="font-size: 0.9rem;">Configure your parameters and start a scouting mission.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# === TAB 2: EVALUATION ===
with tab2:
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 24px;">🔬 Technology Evaluation</h2>', unsafe_allow_html=True)
    
    if not st.session_state.technologies:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
            <p style="font-size: 1.1rem; color: #888; margin-bottom: 8px;">No Technologies Available</p>
            <p style="font-size: 0.9rem; color: #666;">Complete a Discovery mission first to unlock evaluation features.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        tech_df = pd.DataFrame(st.session_state.technologies)
        tech_names = tech_df['name'].tolist() if not tech_df.empty else []
        
        col_select, col_action = st.columns([3, 1])
        
        with col_select:
            selected_tech_names = st.multiselect(
                "Select Technologies to Evaluate", 
                options=tech_names,
                default=tech_names[:5],
                help="Choose which technologies to run deep evaluation on"
            )
        
        with col_action:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            run_eval = st.button("🚀 Run Evaluation", use_container_width=True, type="primary")
        
        if run_eval:
            if not selected_tech_names:
                st.warning("Please select at least one technology to evaluate.")
            else:
                with st.spinner("🔬 Analyzing technologies..."):
                    try:
                        techs_to_eval = [t for t in st.session_state.technologies if t['name'] in selected_tech_names]
                        
                        client, model_name = create_client(selected_model)
                        
                        eval_results = batch_evaluate_technologies(
                            base_dir=output_dir,
                            client=client,
                            model=selected_model,
                            technologies=techs_to_eval,
                            organization_context=None
                        )
                        
                        st.session_state.evaluations = eval_results.get("individual_evaluations", [])
                        st.success("✅ Evaluation Complete!")
                        
                    except Exception as e:
                        st.error(f"❌ Evaluation failed: {str(e)}")
        
        # Visualizations
        if st.session_state.evaluations:
            st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
            st.markdown('<h3 style="font-size: 1.2rem; margin-bottom: 16px;">📈 Analysis Dashboard</h3>', unsafe_allow_html=True)
            
            # Flatten data for display
            flat_evals = []
            for e in st.session_state.evaluations:
                tech_name = e.get("technology", {}).get("name") or e.get("name") or "Unknown"
                
                item = {
                    "name": tech_name,
                    "recommendation": e.get("recommendation", {}).get("recommended_action", "evaluate"),
                    "maturity_level": e.get("maturity", {}).get("trl_level", 0),
                    "strategic_fit": e.get("strategic_fit", {}).get("overall_fit_score", 0),
                    "overall_score": e.get("recommendation", {}).get("overall_score", 0),
                    "investment": e.get("recommendation", {}).get("investment_recommendation", "N/A")
                }
                flat_evals.append(item)
            
            eval_df = pd.DataFrame(flat_evals)
            
            if not eval_df.empty:
                # Summary metrics
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Evaluated", len(eval_df))
                with m2:
                    avg_maturity = round(eval_df['maturity_level'].mean(), 1)
                    st.metric("Avg. TRL", avg_maturity)
                with m3:
                    avg_fit = round(eval_df['strategic_fit'].mean(), 1)
                    st.metric("Avg. Fit Score", avg_fit)
                with m4:
                    pursue_count = len(eval_df[eval_df['recommendation'] == 'pursue_actively'])
                    st.metric("Recommended", pursue_count)
                
                st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
                
                # Data table with styling
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.dataframe(eval_df, use_container_width=True, height=250)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
                
                # Scatter Plot with modern styling
                if 'maturity_level' in eval_df.columns and 'strategic_fit' in eval_df.columns:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    
                    color_map = {
                        'pursue_actively': '#10b981',
                        'monitor_and_pilot': '#3b82f6',
                        'watch': '#f59e0b',
                        'deprioritize': '#ef4444',
                        'evaluate': '#8b5cf6'
                    }
                    
                    fig = px.scatter(
                        eval_df, 
                        x='maturity_level', 
                        y='strategic_fit', 
                        hover_name='name',
                        color='recommendation',
                        size='overall_score',
                        size_max=50,
                        color_discrete_map=color_map,
                        labels={
                            'maturity_level': 'Technology Readiness Level (TRL)', 
                            'strategic_fit': 'Strategic Alignment Score'
                        },
                        range_x=[0, 10],
                        range_y=[0, 10]
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#888'),
                        title=dict(
                            text='Technology Portfolio Map',
                            font=dict(size=18, color='#fff')
                        ),
                        legend=dict(
                            bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#888')
                        ),
                        xaxis=dict(
                            gridcolor='rgba(255,255,255,0.05)',
                            zerolinecolor='rgba(255,255,255,0.1)'
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255,255,255,0.05)',
                            zerolinecolor='rgba(255,255,255,0.1)'
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Numerical scores not available for visualization.")

# === TAB 3: REPORT ===
with tab3:
    st.markdown('<h2 style="font-size: 1.5rem; margin-bottom: 24px;">📄 Generate Report</h2>', unsafe_allow_html=True)
    
    col_info, col_action = st.columns([2, 1])
    
    with col_info:
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0; color: #fff;">📊 What's Included</h4>
            <ul style="color: #888; line-height: 2;">
                <li>Executive Summary for Leadership</li>
                <li>Technology Deep-Dives & Analysis</li>
                <li>Strategic Recommendations</li>
                <li>Competitive Landscape Overview</li>
                <li>Investment Priority Matrix</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_action:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 48px; margin-bottom: 16px;">📝</div>', unsafe_allow_html=True)
        
        tech_count = len(st.session_state.technologies)
        eval_count = len(st.session_state.evaluations)
        st.markdown(f'<p style="color: #888; margin-bottom: 16px;">{tech_count} technologies • {eval_count} evaluations</p>', unsafe_allow_html=True)
        
        generate_btn = st.button("✨ Generate Report", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_btn:
        if not st.session_state.scouting_results:
            st.error("❌ No scouting results available. Please run a Discovery mission first.")
        else:
            with st.spinner("✍️ Crafting your report..."):
                client, model_name = create_client(selected_model)
                
                report_path = generate_scouting_report(
                    base_dir=output_dir,
                    client=client,
                    model=selected_model,
                    scouting_results=st.session_state.scouting_results,
                    evaluations=st.session_state.evaluations,
                    output_format="markdown"
                )
                st.success(f"✅ Report generated successfully!")
                st.balloons()
                
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_content = f.read()
                    
                    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
                    
                    # Download buttons
                    dl1, dl2, dl3 = st.columns([1, 1, 2])
                    with dl1:
                        st.download_button(
                            label="⬇️ Download .md",
                            data=report_content,
                            file_name="techscout_report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with dl2:
                        st.download_button(
                            label="⬇️ Download .txt",
                            data=report_content,
                            file_name="techscout_report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    st.markdown('<div style="height: 24px;"></div>', unsafe_allow_html=True)
                    
                    # Display report in styled container
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown(report_content)
                    st.markdown('</div>', unsafe_allow_html=True)
