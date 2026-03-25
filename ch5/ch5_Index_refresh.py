import models_config
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
reader = SimpleDirectoryReader("files", filename_as_id=True)
documents = reader.load_data()
index = VectorStoreIndex.from_documents(documents)
refreshed = index.refresh_ref_docs(documents)
print(refreshed)