import asyncio
#import models_config
from llama_index.tools.database import DatabaseToolSpec
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
#from llama_index.core import Settings


def write_text_to_file(text, filename):
    """
    Writes the text to a file with the specified filename.
    Args:
        text (str): The text to be written to the file.
        filename (str): File name to write the text into.
    Returns: None
    """
    with open(filename, 'w') as file:
        file.write(text)


save_tool = FunctionTool.from_defaults(fn=write_text_to_file)
db_tools = DatabaseToolSpec(uri="sqlite:///files//database//employees.db")
tools = [save_tool] + db_tools.to_tool_list()

agent = ReActAgent(
    tools=tools,
#    llm=Settings.llm,
    verbose=True,
    streaming=True, 
)

async def main():
    response = await agent.run(
        "For each IT department employee with a salary lower "
        "than the average organization salary, write an email,"
        "announcing a 10% raise and then save all emails into "
        "a file called 'emails.txt'"
    )
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())
