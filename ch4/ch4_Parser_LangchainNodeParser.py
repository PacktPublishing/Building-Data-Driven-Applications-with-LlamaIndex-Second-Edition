from llama_index.core.node_parser import LangchainNodeParser
from langchain.text_splitter import NLTKTextSplitter
from llama_index.readers.file import FlatReader
from pathlib import Path

reader = FlatReader()
document = reader.load_data(Path("files/sample_document1.txt"))
lc_splitter = NLTKTextSplitter(chunk_size=160, chunk_overlap=0)
parser = LangchainNodeParser(lc_splitter)
nodes = parser.get_nodes_from_documents(document)
for node in nodes:
    print(f"Metadata {node.metadata} \nText: {node.text}")