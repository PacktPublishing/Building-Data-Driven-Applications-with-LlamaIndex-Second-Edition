# utils.py

import os
import config
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.readers.file.base import SimpleDirectoryReader

# Save an uploaded file to a specified folder
def save_file(uploaded_file, folder):
    Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Load or build the policies index with persistence
def load_policies_index():
    index_file = os.path.join(config.POLICIES_INDEX_PATH, "docstore.json")
    if os.path.exists(index_file):
        print("Loading existing policies index from persistence...")
        storage_context = StorageContext.from_defaults(persist_dir=config.POLICIES_INDEX_PATH)
        index = load_index_from_storage(storage_context)
    else:
        print("No valid index found - rebuilding policies index...")
        reader = SimpleDirectoryReader("data/policies")
        docs = reader.load_data()
        index = VectorStoreIndex.from_documents(docs)
        os.makedirs(config.POLICIES_INDEX_PATH, exist_ok=True)
        index.storage_context.persist(persist_dir=config.POLICIES_INDEX_PATH)
    return index

# List all existing reports, grouped by contract name
def list_reports():
    Path("data/reports").mkdir(parents=True, exist_ok=True)
    reports = {}
    for fname in os.listdir("data/reports"):
        if fname.endswith(".txt"):
            contract = fname.split("_")[0]
            reports.setdefault(contract, []).append(os.path.join("data/reports", fname))
    return reports

# Load the content of a specific report file
def load_report(report_path):
    with open(report_path, "r", encoding="utf-8") as f:
        return f.read()

# List files in a folder (generic helper)
def list_files(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
