import models_config
from llama_index.core import SimpleDirectoryReader
from llama_cloud.lib.index import LlamaCloudIndex

documents = SimpleDirectoryReader("files").load_data()
index = LlamaCloudIndex.from_documents(
    documents,
    "my_first_index",
    project_name="Default",
    verbose=True,
)
retriever = index.as_retriever()
chat_engine = index.as_chat_engine()
response = chat_engine.chat("What types of harm are listed in Figure 1?")
print(response)
input("Press Enter to exit...")