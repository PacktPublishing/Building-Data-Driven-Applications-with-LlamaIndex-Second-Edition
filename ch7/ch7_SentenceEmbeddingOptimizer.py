from llama_index.core.postprocessor import SentenceEmbeddingOptimizer
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

reader = SimpleDirectoryReader('files/other')
documents = reader.load_data()
index = VectorStoreIndex.from_documents(documents)

optimizer = SentenceEmbeddingOptimizer(
    percentile_cutoff=0.8,
    threshold_cutoff=0.7
)
query_engine = index.as_query_engine(
    optimizer=optimizer
)
response = query_engine.query("Who is Fluffy?")
print(response)
