import streamlit as st
import os
from utils import save_file, load_policies_index, load_report, list_files
from analysis import perform_risk_analysis, perform_compliance_check
from chat import clear_chat_cache

def render_contracts_section(is_analyzing, analyzing_file):
    """
    Renders the contracts management section.
    Returns a tuple: (contracts_modified, analysis_started, analysis_completed)
    """
    st.header("📄 Contracts")
    contracts_modified = False
    analysis_started = False
    analysis_completed = False
    
    # Upload new contract
    if "contract_uploaded_done" not in st.session_state:
        uploaded_contract = st.file_uploader("Add Contract (.pdf, .txt)", key="contract_uploader")
        if uploaded_contract and "contract_uploaded" not in st.session_state and not is_analyzing:
            save_file(uploaded_contract, "data/contracts")
            st.session_state["contract_uploaded"] = True
            st.success("Contract added!")

            st.session_state["contract_uploaded_done"] = True
            contracts_modified = True

    else:
        if st.button("Upload another contract", disabled=is_analyzing):
            del st.session_state["contract_uploaded_done"]
            if "contract_uploaded" in st.session_state:
                del st.session_state["contract_uploaded"]

    # List existing contracts
    contract_files = list_files("data/contracts")
    
    if not contract_files:
        st.info("No contracts uploaded yet. Upload a contract to get started.")
        return contracts_modified, analysis_started, analysis_completed

    if not is_analyzing:
        # Display contract list with actions
        for file in contract_files:
            contract_name = os.path.splitext(file)[0]
            report_name = f"analysis report for {contract_name}.txt"
            report_path = os.path.join("data/reports", report_name)
            
            # Create columns for contract display
            col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
            
            with col_a:
                # Show contract with icon and report status
                if os.path.exists(report_path):
                    st.write(f"📄 {file} ✅")
                else:
                    st.write(f"📄 {file}")
            
            with col_b:
                if st.button("Analyze", key=f"analyze_contract_{file}"):
                    st.session_state["is_analyzing"] = True
                    st.session_state["is_analyzing_file"] = file
                    analysis_started = True
            
            with col_c:
                if os.path.exists(report_path):
                    if st.button("See report", key=f"see_report_{file}"):
                        report_content = load_report(report_path)
                        st.session_state["current_report_content"] = report_content
                        st.session_state["current_report_name"] = file
                        st.session_state["current_contract_name"] = contract_name
                else:
                    st.write("—")
            
            with col_d:
                if st.button("❌", key=f"delete_contract_{file}"):
                    try:
                        # Remove contract file
                        os.remove(os.path.join("data/contracts", file))
                        
                        # Remove associated report if exists
                        if os.path.exists(report_path):
                            os.remove(report_path)
                        
                        # Clear chat cache for this contract
                        clear_chat_cache(contract_name)
                        
                        # Clear current report if it's for this contract
                        if st.session_state.get("current_contract_name") == contract_name:
                            for key in ["current_report_content", "current_report_name", "current_contract_name"]:
                                if key in st.session_state:
                                    del st.session_state[key]
                        
                        st.success(f"Deleted contract: {file}")
                        contracts_modified = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting contract: {str(e)}")

    else:
        # Show analysis progress
        st.info(f"🔄 Analyzing: {analyzing_file}")
        
        with st.spinner("Analyzing contract..."):
            file = st.session_state["is_analyzing_file"]
            
            try:
                policies_index = load_policies_index()
                contract_path = os.path.join("data/contracts", file)

                # Perform analysis
                risk_report = perform_risk_analysis(contract_path, policies_index)
                compliance_report = perform_compliance_check(contract_path, policies_index)

                # Save report
                contract_name = os.path.splitext(file)[0]
                report_name = f"analysis report for {contract_name}.txt"
                
                # Ensure reports directory exists
                os.makedirs("data/reports", exist_ok=True)
                
                with open(f"data/reports/{report_name}", "w", encoding="utf-8") as f:
                    f.write("RISK ANALYSIS:\n")
                    f.write("=" * 50 + "\n")
                    f.write(risk_report)
                    f.write("\n\n" + "=" * 50 + "\n")
                    f.write("COMPLIANCE CHECK:\n")
                    f.write("=" * 50 + "\n")
                    f.write(compliance_report)

                # Clear chat cache since we have a new report
                clear_chat_cache(contract_name)

                # Reset analysis state
                st.session_state["is_analyzing"] = False
                del st.session_state["is_analyzing_file"]
                
                analysis_completed = True
                st.success(f"✅ Analysis completed! Report saved: {report_name}")
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.session_state["is_analyzing"] = False
                if "is_analyzing_file" in st.session_state:
                    del st.session_state["is_analyzing_file"]
    
    # Show contract count
    if contract_files:
        analyzed_count = sum(1 for file in contract_files 
                           if os.path.exists(os.path.join("data/reports", f"analysis report for {os.path.splitext(file)[0]}.txt")))
        st.caption(f"Total contracts: {len(contract_files)} | Analyzed: {analyzed_count}")
    
    return contracts_modified, analysis_started, analysis_completed