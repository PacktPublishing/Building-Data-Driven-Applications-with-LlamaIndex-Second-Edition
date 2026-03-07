from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import models_config
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
)
 
documents = SimpleDirectoryReader("files").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

query = "What are the main obligations of the service provider?"
response = query_engine.query(query)
print(response)

judge_llm = OpenAI(model="gpt-5-mini", temperature=0)
faithfulness_evaluator = FaithfulnessEvaluator(llm=judge_llm)
faith_result = faithfulness_evaluator.evaluate_response(
    response=response
)
print(f"Passing: {faith_result.passing}")


relevancy_evaluator = RelevancyEvaluator(llm=judge_llm)
rel_result = relevancy_evaluator.evaluate_response(
    query=query,
    response=response
)
print(f"Passing: {rel_result.passing}")


correctness_evaluator = CorrectnessEvaluator(llm=judge_llm)
cor_result = correctness_evaluator.evaluate(
    query=query,
    response=str(response),
    reference="The service provider is obligated to deliver monthly reports, maintain uptime of 99.9%, and respond to support requests within 4 hours."
)
print(f"Score: {cor_result.score}")
print(f"Passing: {cor_result.passing}")
print(f"Feedback: {cor_result.feedback}")