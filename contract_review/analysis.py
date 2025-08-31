# analysis.py

from llama_index.core.readers.file.base import SimpleDirectoryReader

# Perform risk analysis on contract
def perform_risk_analysis(contract_path, policies_index):
    reader = SimpleDirectoryReader(input_files=[contract_path])
    contract_docs = reader.load_data()
    contract_text = contract_docs[0].text

    query_risk = "Perform a detailed risk analysis of this contract. Cite sources."
    risk_response = policies_index.as_query_engine().query(f"{query_risk}\n\n{contract_text}")

    return str(risk_response)

# Perform compliance check on contract
def perform_compliance_check(contract_path, policies_index):
    reader = SimpleDirectoryReader(input_files=[contract_path])
    contract_docs = reader.load_data()
    contract_text = contract_docs[0].text

    query_compliance = "Check this contract against internal company policies. List any non-compliances. Cite sources. Don't mention any other issues."
    compliance_response = policies_index.as_query_engine().query(f"{query_compliance}\n\n{contract_text}")

    return str(compliance_response)
