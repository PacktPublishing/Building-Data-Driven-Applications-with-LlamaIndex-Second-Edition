import models_config
from llama_index.core import SummaryIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("files").load_data()
summary_index = SummaryIndex.from_documents(documents)
retriever = summary_index.as_retriever()
result = retriever.retrieve("Tell me about ancient Rome")
print(result[0].text)
