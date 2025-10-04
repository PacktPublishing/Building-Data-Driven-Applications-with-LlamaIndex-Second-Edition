from llama_index.core.schema import TextNode, NodeWithScore
from llama_index.core import get_response_synthesizer

nodes = [
    NodeWithScore(
        node=TextNode(text="The town square clock was built in 1895")
    ),
    NodeWithScore(
        node=TextNode(text="A turquoise parrot lives in the Amazon")
    ),
    NodeWithScore(
        node=TextNode(text="A rare orchid blooms only at midnight")
    ),
]

synth = get_response_synthesizer(
    response_mode="refine",
    streaming=False, 
    structured_answer_filtering=False
)
response = synth.synthesize(
    "When was the clock built?", 
    nodes=nodes
)
print(response)
