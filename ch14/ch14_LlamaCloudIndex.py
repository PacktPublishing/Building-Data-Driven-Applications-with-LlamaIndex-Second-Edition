import models_config
from llama_index.core import SimpleDirectoryReader
from llama_cloud_services import LlamaCloudIndex

documents = SimpleDirectoryReader("contracts").load_data()
index = LlamaCloudIndex.from_documents(
    documents,
    "my_first_index",
    project_name="Default",
    organization_id="<your-organization-id>",
    verbose=True,
)
retriever = index.as_retriever()
chat_engine = index.as_chat_engine()
response = chat_engine.chat("What is the SLA for P3 — Medium incidents?")
print(response)
input("Press Enter to exit...")