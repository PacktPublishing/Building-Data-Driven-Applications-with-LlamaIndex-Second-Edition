# config.py

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Configure the LLM model
Settings.llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434",
    temperature=0.8,
    context_window=16000,
    request_timeout=30.0
)

# Configure the embedding model
Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434",
    request_timeout=30.0
)

# Paths for persisting indexes
POLICIES_INDEX_PATH = "data/persistence/policies_index"
CONTRACTS_INDEX_PATH = "data/persistence/contracts_index"
REPORTS_INDEX_PATH = "data/persistence/reports_index"
