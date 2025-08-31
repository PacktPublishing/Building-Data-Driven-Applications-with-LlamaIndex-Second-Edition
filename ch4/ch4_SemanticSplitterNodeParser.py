import models_config
from llama_index.core import Settings
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.readers.file import FlatReader
from pathlib import Path
reader = FlatReader()
document = reader.load_data(Path("files/black_bears.txt"))

parser = SemanticSplitterNodeParser.from_defaults(
    embed_model=Settings.embed_model,
    buffer_size=1,
    breakpoint_percentile_threshold=95
)
nodes = parser.get_nodes_from_documents(document)
for node in nodes:
    print(f"Metadata {node.metadata} \nText: {node.text}")

