import models_config
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
documents = SimpleDirectoryReader("files").load_data()
index = VectorStoreIndex.from_documents(documents)
retriever = index.as_retriever(similarity_top_k=5)
results = retriever.retrieve("Who built the Colosseum?")
for i, item in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Score:", item.score)
    print("Node ID:", item.node.node_id)
    print("Metadata:", item.node.metadata)
    print(item.node.text[:30])
