from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.postprocessor.presidio import PresidioPIINodePostprocessor
text = "Hi John Doe, your email is john@example.com"
node = TextNode(text=text)
processor = PresidioPIINodePostprocessor()
clean_nodes = processor.postprocess_nodes([NodeWithScore(node=node)])
print(clean_nodes[0].node.get_text())
print(clean_nodes[0].node.metadata["__pii_node_info__"])