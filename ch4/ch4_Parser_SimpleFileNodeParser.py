from llama_index.readers.file import FlatReader
from llama_index.core.node_parser import SimpleFileNodeParser
from pathlib import Path

documents = FlatReader().load_data(Path("files/sample_document1.txt"))
parser = SimpleFileNodeParser()
nodes = parser.get_nodes_from_documents(documents)