from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

doc = Document(
    text=(
        "This is sentence 1. This is sentence 2. "
        "Sentence 3 here."
    ),
    metadata={"author": "John Smith"}
)

splitter = SentenceSplitter(
    chunk_size=12,  
    chunk_overlap=0
)

nodes = splitter.get_nodes_from_documents([doc])

for node in nodes:
    print(node.text)
    print(node.metadata)