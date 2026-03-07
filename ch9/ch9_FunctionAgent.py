import asyncio
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.tools.database import DatabaseToolSpec

def write_text_to_file(text, filename):
    """
    Writes the text to a file with the specified filename.

    Args:
        text (str): The text to be written to the file.
        filename (str): File name to write the text into.

    Returns:
        None
    """
    with open(filename, 'w') as file:
        file.write(text)

save_tool = FunctionTool.from_defaults(fn=write_text_to_file)
db_tools = DatabaseToolSpec(uri="sqlite:///files/database/employees.db")
tools = [save_tool] + db_tools.to_tool_list()

llm=Ollama(model="qwen3:8b", 
    base_url="http://localhost:11434",
    temperature=0.1,
    request_timeout=30.0
)

agent = FunctionAgent(
    tools=tools,
    llm=llm,
    streaming=True,
)

async def main():
    handler = agent.run(
        "For each IT department employee with a salary lower "
        "than the average organization salary, write an email, "
        "announcing a 10% raise and then save all emails into "
        "a file called 'emails.txt, then stop. '"
    )
    async for event in handler.stream_events():
        if hasattr(event, "delta") and event.delta:
            print(event.delta, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
