import asyncio
import models_config
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.evaluation import FaithfulnessEvaluator, RelevancyEvaluator
from llama_index.core.evaluation import BatchEvalRunner, generate_question_context_pairs
from llama_index.core.node_parser import SentenceSplitter
 
documents = SimpleDirectoryReader("files").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
splitter = SentenceSplitter(chunk_size=512)
nodes = splitter.get_nodes_from_documents(documents)
 
qa_dataset = generate_question_context_pairs(nodes, num_questions_per_chunk=2)
faithfulness_eval = FaithfulnessEvaluator()
relevancy_eval = RelevancyEvaluator()
 
runner = BatchEvalRunner(
    {"faithfulness": faithfulness_eval,
     "relevancy": relevancy_eval},
    workers=8
)
eval_questions = list(qa_dataset.queries.values())
 
eval_results = asyncio.run(
    runner.aevaluate_queries(
        query_engine=query_engine,
        queries=eval_questions
    )
)

faithfulness_score = sum(
    1 for r in eval_results["faithfulness"] if r.passing
) / len(eval_results["faithfulness"])
 
relevancy_score = sum(
    1 for r in eval_results["relevancy"] if r.passing
) / len(eval_results["relevancy"])
 
print(f"Faithfulness: {faithfulness_score:.1%}")
print(f"Relevancy:    {relevancy_score:.1%}")