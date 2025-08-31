import streamlit as st
from chat import render_chat_interface

def render_reports_section():
    """
    Renders the reports and chat section.
    Returns True if the section is being displayed.
    """
    # Check if we have a current report to display
    has_current_report = (
        "current_report_content" in st.session_state and 
        "current_report_name" in st.session_state and 
        "current_contract_name" in st.session_state
    )
    
    if has_current_report:
        st.header("📊 Reports & Chat")
        
        # Show current contract info
        contract_name = st.session_state["current_contract_name"]
        report_name = st.session_state["current_report_name"]
        
        # Add close button at the top
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(f"Analysis for: {contract_name}")
        with col2:
            if st.button("✕ Close", key="close_report_top"):
                _clear_current_report()
                st.rerun()
        
        # Create two columns: Report (left) and Chat (right)
        report_col, chat_col = st.columns([3, 2])
        
        with report_col:
            st.markdown("### 📋 Analysis Report")
            
            # Display report content with better formatting
            report_content = st.session_state["current_report_content"]
            
            # Create a styled container for the report
            with st.container():
                st.text_area(
                    f"Report for {report_name}",
                    value=report_content,
                    height=600,
                    key="report_display",
                    help="This is the AI-generated analysis report for the contract."
                )
            
            # Action buttons
            col_a, col_b = st.columns([3, 1])
            with col_a:
                if st.button("📥 Download Report", key="download_report"):
                    # Create download functionality
                    st.download_button(
                        label="Download as Text File",
                        data=report_content,
                        file_name=f"analysis_report_{contract_name}.txt",
                        mime="text/plain",
                        key="download_button"
                    )
            with col_b:
                if st.button("🗑️ Close", key="close_report_bottom"):
                    _clear_current_report()
                    st.rerun()
        
        with chat_col:
            # Render the chat interface for the current contract
            render_chat_interface(contract_name)
        
        return True
    
    else:
        st.header("📊 Reports")
        
        # Show helpful information when no report is selected
        st.info("💡 **No report selected**")
        st.markdown("""
        To view a report and start chatting:
        1. Upload a contract (if you haven't already)
        2. Click **Analyze** to generate a report
        3. Click **See report** to view the analysis
        4. Use the chat interface to ask questions about the contract
        """)
        
        # Show some statistics if there are contracts/reports
        _show_statistics()
        
        return False

def _clear_current_report():
    """Helper function to clear the current report from session state."""
    keys_to_clear = ["current_report_content", "current_report_name", "current_contract_name"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def _show_statistics():
    """Show some basic statistics about contracts and reports."""
    try:
        import os
        from utils import list_files
        
        # Count contracts and reports
        contract_files = list_files("data/contracts")
        report_files = []
        
        if os.path.exists("data/reports"):
            report_files = [f for f in os.listdir("data/reports") if f.endswith(".txt")]
        
        if contract_files or report_files:
            st.markdown("### 📈 Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Contracts", len(contract_files))
            
            with col2:
                st.metric("Generated Reports", len(report_files))
            
            with col3:
                completion_rate = (len(report_files) / len(contract_files) * 100) if contract_files else 0
                st.metric("Analysis Rate", f"{completion_rate:.0f}%")
    
    except Exception as e:
        # If there's any error getting statistics, just show a simple message
        st.write("Upload and analyze contracts to see statistics here.")