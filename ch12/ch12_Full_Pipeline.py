# STEP 1
import models_config
import llama_index.core.instrumentation as instrument
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler

span_handler = SimpleSpanHandler()
dispatcher = instrument.get_dispatcher()
dispatcher.add_span_handler(span_handler)


# STEP 2
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
 
documents = SimpleDirectoryReader("files").load_data()
splitter = SentenceSplitter(chunk_size=512)
nodes = splitter.get_nodes_from_documents(documents)
index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine(similarity_top_k=2)


# STEP 3
from llama_index.core.evaluation import generate_question_context_pairs
from llama_index.llms.openai import OpenAI
 
judge_llm = OpenAI(model="gpt-5-mini", temperature=0)
qa_dataset = generate_question_context_pairs(
    nodes,
    llm=judge_llm,
    num_questions_per_chunk=2
)
eval_questions = list(qa_dataset.queries.values())
print(f"Generated {len(eval_questions)} evaluation questions")


# STEP 4
import asyncio
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    BatchEvalRunner,
)
faithfulness_eval = FaithfulnessEvaluator(llm=judge_llm)
relevancy_eval = RelevancyEvaluator(llm=judge_llm)
runner = BatchEvalRunner(
    {"faithfulness": faithfulness_eval,
     "relevancy": relevancy_eval},
    workers=8
)
async def run_evaluations():
    eval_results = await runner.aevaluate_queries(
        query_engine=query_engine,
        queries=eval_questions
    )
    improved_qe = index.as_query_engine(similarity_top_k=5)
    improved_results = await runner.aevaluate_queries(
        query_engine=improved_qe,
        queries=eval_questions
    )
    return eval_results, improved_results
eval_results, improved_results = asyncio.run(run_evaluations())


# STEP 5
faith_results = eval_results["faithfulness"]
rel_results = eval_results["relevancy"]
 
faith_score = sum(1 for r in faith_results if r.passing) / len(faith_results)
rel_score = sum(1 for r in rel_results if r.passing) / len(rel_results)
 
print(f"Faithfulness: {faith_score:.1%}")
print(f"Relevancy:    {rel_score:.1%}")
 
print("\nFailing queries:")
for i, (fr, rr) in enumerate(zip(faith_results, rel_results)):
    if not fr.passing or not rr.passing:
        failed = []
        if not fr.passing:
            failed.append("Faithfulness")
        if not rr.passing:
            failed.append("Relevancy")
        print(f"  Query {i}: {eval_questions[i][:80]}...")
        print(f"    Failed: {', '.join(failed)}")

for span in span_handler.completed_spans:
    if "retrieve" in span.id_.lower():
        print(f"Retrieval span: {span.id_}")
        print(f"  Duration: {span.duration}")


# STEP 6
new_faith_score = sum(1 for r in improved_results["faithfulness"]
                      if r.passing) / len(improved_results["faithfulness"])
new_rel_score = sum(1 for r in improved_results["relevancy"]
                    if r.passing) / len(improved_results["relevancy"])
 
print(f"BEFORE -> AFTER")
print(f"Faithfulness: {faith_score:.1%} -> {new_faith_score:.1%}")
print(f"Relevancy:    {rel_score:.1%} -> {new_rel_score:.1%}")
