import models_config
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
)
nodes = [
    TextNode(
        text="An incident is an accidental or malicious event affecting security.",
        metadata={"department": "Security", "level": 2},
    ),
    TextNode(
        text="An incident is an interruption or degradation of an IT service.",
        metadata={"department": "IT", "level": 1},
    ),
]
index = VectorStoreIndex(nodes)
filters = MetadataFilters(
    filters=[MetadataFilter(key="department", value="Security")]
)
retriever = index.as_retriever(filters=filters)
results = retriever.retrieve("What is an incident?")

for item in results:
    print(item.node.metadata)
    print(item.node.text)

