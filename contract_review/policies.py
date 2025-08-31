import streamlit as st
import os
from utils import save_file, load_policies_index, list_files
from chat import clear_chat_cache

def render_policies_section(is_analyzing):
    """
    Renders the policies management section.
    Returns True if policies were modified (for cache clearing).
    """
    st.header("📂 Policies")
    policies_modified = False
    
    # Upload new policy
    if "policy_uploaded_done" not in st.session_state:
        uploaded_policy = st.file_uploader("Add Policy (.pdf, .txt)", key="policy_uploader")
        if uploaded_policy and "policy_uploaded" not in st.session_state and not is_analyzing:
            save_file(uploaded_policy, "data/policies")
            st.session_state["policy_uploaded"] = True
            st.success("Policy added and indexed!")

            load_policies_index()
            st.success("Index updated!")

            st.session_state["policy_uploaded_done"] = True
            policies_modified = True

    else:
        if st.button("Upload another policy", disabled=is_analyzing):
            del st.session_state["policy_uploaded_done"]
            if "policy_uploaded" in st.session_state:
                del st.session_state["policy_uploaded"]

    # List existing policies
    policy_files = list_files("data/policies")
    
    if not policy_files:
        st.info("No policies uploaded yet. Upload a policy to get started.")
        return policies_modified

    for file in policy_files:
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.write(f"📄 {file}")
        with col_b:
            if st.button("❌", key=f"delete_policy_{file}", disabled=is_analyzing):
                try:
                    os.remove(os.path.join("data/policies", file))
                    st.success(f"Deleted policy: {file}")
                    
                    # Clear chat cache for all contracts since policies changed
                    contract_files = list_files("data/contracts")
                    for contract_file in contract_files:
                        contract_name = os.path.splitext(contract_file)[0]
                        clear_chat_cache(contract_name)
                    
                    policies_modified = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting policy: {str(e)}")
    
    # Show policy count
    if policy_files:
        st.caption(f"Total policies: {len(policy_files)}")
    
    return policies_modified