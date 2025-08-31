from llama_index.core import Document
from llama_index.core.schema import TextNode
doc = Document(text="This is a sample document text")
n1 = TextNode(
    text=doc.text[0:16],
    metadata={"parent_doc_id": doc.doc_id}
)
n2 = TextNode(
    text=doc.text[17:],
    metadata={"parent_doc_id": doc.doc_id}
)
print(n1.id_)
print(n1.get_content())
print(n2.id_)
print(n2.get_content())