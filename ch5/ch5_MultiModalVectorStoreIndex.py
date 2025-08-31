from llama_index.core.indices import MultiModalVectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
documents = SimpleDirectoryReader("multimodal_files").load_data()
index = MultiModalVectorStoreIndex.from_documents(documents)
llm = Ollama(
    model="llava:7b"
)
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("What can you see in the pictures?")
print("Answer:\n", response)