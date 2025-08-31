import models_config
from llama_index.core import PropertyGraphIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("files").load_data()
index = PropertyGraphIndex.from_documents(documents, max_triplets_per_chunk=2, use_async=False)
query_engine = index.as_query_engine()
response = query_engine.query("Tell me about dogs.")
print(response)
