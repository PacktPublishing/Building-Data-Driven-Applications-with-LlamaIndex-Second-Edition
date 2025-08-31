import models_config
from llama_index.core import SummaryIndex, Document
from llama_index.core.node_parser import SentenceSplitter
doc = Document(text=(
    "Lionel Messi is a football player from Argentina. "
    "He has won the Ballon d'Or trophy 7 times. "
    "Lionel Messi's hometown is Rosario. "
    "He was born on June 24, 1987."
))
splitter = SentenceSplitter(chunk_size=20, chunk_overlap=0)
nodes = splitter.get_nodes_from_documents([doc])
index = SummaryIndex(nodes)

query_engine = index.as_query_engine()
response = query_engine.query("What is Messi's hometown?")
print(response)