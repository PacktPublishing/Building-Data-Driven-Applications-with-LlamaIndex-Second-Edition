from llama_index.core import SimpleDirectoryReader
from llama_index.core.evaluation import generate_question_context_pairs
from llama_index.core.node_parser import SentenceSplitter
import models_config
 
documents = SimpleDirectoryReader("files").load_data()
splitter = SentenceSplitter(chunk_size=512)
nodes = splitter.get_nodes_from_documents(documents)
 
qa_dataset = generate_question_context_pairs(nodes, num_questions_per_chunk=2)
 
print(f"Generated {len(qa_dataset.queries)} questions")
for query_id, query_text in list(qa_dataset.queries.items())[:3]:
    print(f"  - {query_text}")