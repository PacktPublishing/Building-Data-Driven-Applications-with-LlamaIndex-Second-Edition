# loading files using SimpleDirectoryReader and filename_as_id
from llama_index.core import SimpleDirectoryReader
reader = SimpleDirectoryReader("files", filename_as_id=True)
documents = reader.load_data()
for doc in documents:
    print(doc.id_)
    
# manually setting the id_
from llama_index.core import Document
doc = Document(text="Some content", id_="my_custom_id")
print(doc)

# inserting new documents
import models_config
from llama_index.core import Document, VectorStoreIndex
index = VectorStoreIndex.from_documents(
    [Document(text="Original code ALPHA123.", id_="doc_1")]
)
index.insert(Document(text="Inserted code BETA999.", id_="doc_2"))
response = index.as_query_engine().query("What's in the documents?")
print("After insert:")
for node in response.source_nodes:
    print(node.node.text)

# updating existing documents
index.update_ref_doc(Document(text="Updated code GAMMA777.", id_="doc_2"))
response = index.as_query_engine().query("What's in the documents?")
print("\nAfter update:")
for node in response.source_nodes:
    print(node.node.text)

# deleting documents from the index
index.delete_ref_doc("doc_2", delete_from_docstore=True)
response = index.as_query_engine().query("What's in the documents?")
print("\nAfter delete:")
for node in response.source_nodes:
    print(node.node.text)