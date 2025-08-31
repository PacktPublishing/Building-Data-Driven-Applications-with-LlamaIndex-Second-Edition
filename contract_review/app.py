# app.py

import streamlit as st
from policies import render_policies_section
from contracts import render_contracts_section
from reports import render_reports_section

# Set page config to wide layout
st.set_page_config(
    page_title="Contract Advisor", 
    layout="wide",
    page_icon="📋",
    initial_sidebar_state="collapsed"
)

# App title and description
st.title("📋 Contract Review Expert")
st.markdown("Upload policies and contracts to perform AI-powered risk analysis and compliance checks.")

# --- State variables ---
is_analyzing = st.session_state.get("is_analyzing", False)
analyzing_file = st.session_state.get("is_analyzing_file", None)

# --- TOP ROW: Policies and Contracts side by side ---

col1, col2 = st.columns(2, gap="large")

# --- Policies section ---
with col1:
    policies_modified = render_policies_section(is_analyzing)

# --- Contracts section ---
with col2:
    contracts_modified, analysis_started, analysis_completed = render_contracts_section(
        is_analyzing, analyzing_file
    )

# Handle state changes
if analysis_started or analysis_completed:
    st.rerun()

# Add separator
st.markdown("---")

# --- Reports and Chat section ---
report_displayed = render_reports_section()

# --- Footer with helpful information ---
if not report_displayed:
    st.markdown("---")
    
    with st.expander("ℹ️ How to use this application"):
        st.markdown("""
        ### Getting Started:
        
        1. **Upload Policies** (left panel)
           - Add company policies, guidelines, or standards
           - Supported formats: PDF, TXT
           - These will be used as reference for compliance checks
        
        2. **Upload Contracts** (right panel)
           - Add contracts you want to analyze
           - Supported formats: PDF, TXT
           - Click 'Analyze' to generate risk and compliance reports
        
        3. **Review Reports**
           - Click 'See report' to view the AI analysis
           - The chat interface will appear alongside the report
           - Ask questions about risks, compliance, or contract terms
        
        ### Features:
        - **Risk Analysis**: Identifies potential risks in contracts
        - **Compliance Check**: Compares contracts against your policies
        - **Interactive Chat**: Ask specific questions about any contract
        - **Document Management**: Easy upload, view, and delete functionality
        """)
    
    # Show application status
    st.sidebar.title("🔧 Application Status")
    
    if is_analyzing:
        st.sidebar.warning(f"⏳ Analyzing: {analyzing_file}")
        st.sidebar.progress(0.5)  # Indeterminate progress
    else:
        st.sidebar.success("✅ Ready for analysis")
    
    # Quick stats in sidebar
    try:
        from utils import list_files
        import os
        
        policy_count = len(list_files("data/policies"))
        contract_count = len(list_files("data/contracts"))
        
        report_count = 0
        if os.path.exists("data/reports"):
            report_count = len([f for f in os.listdir("data/reports") if f.endswith(".txt")])
        
        st.sidebar.metric("Policies", policy_count)
        st.sidebar.metric("Contracts", contract_count)
        st.sidebar.metric("Reports", report_count)
        
    except Exception:
        pass  # If there's an error getting stats, just skip the sidebar metrics