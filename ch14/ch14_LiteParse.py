import models_config
from liteparse import LiteParse
from llama_index.core import Document, VectorStoreIndex
parser = LiteParse()
result = parser.parse("./files/nist.ai.100-1.pdf", ocr_enabled=True)
documents = [Document(text=result.text)]
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is described in Figure 1?")
print(response)