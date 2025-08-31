# models_config.py

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Automatically configure on import
Settings.llm = Ollama(
    model="gemma3:4b",
    base_url="http://localhost:11434",
    temperature=0.8,
    context_window=16000,
    request_timeout=30.0
)

Settings.embed_model = OllamaEmbedding(
    model_name="nomic-embed-text",
    base_url="http://localhost:11434",
    request_timeout=30.0
)
