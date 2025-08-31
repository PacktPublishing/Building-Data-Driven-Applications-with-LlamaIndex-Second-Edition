from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.tools.wikipedia import WikipediaToolSpec
from llama_index.core.tools.tool_spec.load_and_search import LoadAndSearchToolSpec
from llama_index.llms.ollama import Ollama

llm = Ollama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0.8,
    request_timeout=30.0
)

wiki_search = WikipediaToolSpec().to_tool_list()[1]
tools = LoadAndSearchToolSpec.from_defaults(wiki_search).to_tool_list()

agent = ReActAgent.from_tools(
    tools=tools, 
    max_iterations=25, 
    llm=llm, 
    verbose=True
)

print(agent.chat("What is the most famous place on every island in the Azores?"))

