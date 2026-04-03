from llama_index.core import SimpleDirectoryReader
documents = SimpleDirectoryReader("./files").load_data()
print(len(documents))
for i, doc in enumerate(documents[:5]):
    print(f"--- Page {i + 1} ---")
    print(doc.text[:500])