import streamlit as st
import os
from utils import load_policies_index, load_report
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.readers.file.base import SimpleDirectoryReader

def render_chat_interface(contract_name):
    """
    Renders the chat interface for a given contract.
    This function is designed to be called from the main app.
    """
    if not contract_name:
        st.warning("No contract selected for chat.")
        return
    
    st.markdown("### 💬 Chat with Contract")
    st.markdown(f"**Current Contract:** {contract_name}")
    
    # Try different file extensions
    contract_filename = None
    for ext in [".txt", ".pdf"]:
        potential_path = os.path.join("data/contracts", f"{contract_name}{ext}")
        if os.path.exists(potential_path):
            contract_filename = f"{contract_name}{ext}"
            break
    
    if not contract_filename:
        st.error(f"Contract file not found for '{contract_name}'. Please check if the file exists in the contracts folder.")
        return
    
    # Initialize chat engine (with caching to avoid rebuilding)
    chat_engine_key = f"chat_engine_{contract_name}"
    if chat_engine_key not in st.session_state:
        with st.spinner("Loading contract and policies..."):
            # Load contract
            contract_path = os.path.join("data/contracts", contract_filename)
            contract_reader = SimpleDirectoryReader(input_files=[contract_path])
            contract_docs = contract_reader.load_data()
            
            # Load policies
            policies_index = load_policies_index()
            policies_reader = SimpleDirectoryReader(input_dir="data/policies")
            policies_docs = policies_reader.load_data()
            
            # Load report if exists
            report_name = f"analysis report for {contract_name}.txt"
            report_path = os.path.join("data/reports", report_name)
            report_docs = []
            if os.path.exists(report_path):
                report_text = load_report(report_path)
                report_docs.append(Document(text=report_text))
            
            # Combine all docs
            all_docs = contract_docs + policies_docs + report_docs
            
            # Build index and chat engine with proper configuration
            index = VectorStoreIndex.from_documents(all_docs)
            chat_engine = index.as_chat_engine(
                chat_mode="condense_question",
                verbose=True,
                similarity_top_k=3,
                streaming=False
            )
            
            # Cache the chat engine
            st.session_state[chat_engine_key] = chat_engine
    else:
        chat_engine = st.session_state[chat_engine_key]
    
    # Initialize chat history with a unique key for this contract
    chat_key = f"chat_history_{contract_name}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Chat input
    user_input = st.text_input(
        f"Ask about '{contract_name}':", 
        key=f"chat_input_{contract_name}",
        placeholder="e.g., What are the main risks in this contract?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("Ask", key=f"ask_btn_{contract_name}")
    with col2:
        if st.session_state[chat_key]:
            clear_button = st.button("Clear Chat", key=f"clear_btn_{contract_name}")
            if clear_button:
                st.session_state[chat_key] = []
                st.rerun()
    
    if ask_button and user_input.strip():
        with st.spinner("Thinking..."):
            try:
                # Add timeout and better error handling
                response = chat_engine.chat(user_input)
                response_text = str(response)
                
                # Ensure response isn't empty
                if not response_text.strip():
                    response_text = "I couldn't generate a proper response. Please try rephrasing your question."
                
                st.session_state[chat_key].append((user_input, response_text))
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "max iterations" in error_msg.lower():
                    st.error("The AI took too long to respond. Please try a simpler question or rephrase your query.")
                    # Try a direct query instead
                    try:
                        query_engine = index.as_query_engine(similarity_top_k=3)
                        response = query_engine.query(user_input)
                        st.session_state[chat_key].append((user_input, f"Direct query result: {str(response)}"))
                        st.rerun()
                    except:
                        st.session_state[chat_key].append((user_input, "I'm having trouble processing this question. Please try a different approach."))
                        st.rerun()
                else:
                    st.error(f"Error generating response: {error_msg}")
                    st.session_state[chat_key].append((user_input, f"Error: {error_msg}"))
                    st.rerun()
    
    # Display chat history
    if st.session_state[chat_key]:
        st.markdown("### Chat History")
        # Create a container with max height for scrolling
        with st.container():
            for i, (q, a) in enumerate(reversed(st.session_state[chat_key])):
                with st.expander(f"Q: {q[:50]}{'...' if len(q) > 50 else ''}", expanded=(i == 0)):
                    st.markdown(f"**Question:** {q}")
                    st.markdown(f"**Answer:** {a}")
    else:
        st.info("No chat history yet. Ask a question about the contract above!")

def clear_chat_cache(contract_name):
    """
    Clears the cached chat engine for a contract.
    Useful when contract or policies are updated.
    """
    chat_engine_key = f"chat_engine_{contract_name}"
    if chat_engine_key in st.session_state:
        del st.session_state[chat_engine_key]