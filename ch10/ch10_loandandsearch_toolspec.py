import asyncio
import models_config
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.tools.tool_spec.load_and_search import LoadAndSearchToolSpec
from llama_index.tools.database import DatabaseToolSpec

async def main() -> None:
    db_tools = DatabaseToolSpec(uri="sqlite:///files/database/employees.db")
    tool_list = db_tools.to_tool_list()
    load_data_tool = next(t for t in tool_list if t.metadata.name == "load_data")
    tools = LoadAndSearchToolSpec.from_defaults(load_data_tool).to_tool_list()
    agent = ReActAgent(
        tools=tools,
        verbose=True,
        streaming=False,
    )
    handler = agent.run(
        "Who has the highest salary in the Employees table? "
        "Use the tools and return the exact name and salary."
    )
    async for ev in handler.stream_events():
        cls = ev.__class__.__name__
        if "Tool" in cls or "Agent" in cls or "Step" in cls:
            print(f"{cls}: {ev}")
    response = await handler
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
