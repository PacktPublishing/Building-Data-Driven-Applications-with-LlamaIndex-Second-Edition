import models_config
from llama_cloud import LlamaCloud
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
client = LlamaCloud()
result = client.parsing.parse(
    upload_file="./files/nist.ai.100-1.pdf",
    tier="cost_effective",
    version="latest",
    expand=["markdown"],
)
documents = [Document(text=str(result.markdown))]
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=512, chunk_overlap=50),
    ]
)
nodes = pipeline.run(documents=documents)
index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()
response = query_engine.query("What types of harm are listed in Figure 1?")
print(response)