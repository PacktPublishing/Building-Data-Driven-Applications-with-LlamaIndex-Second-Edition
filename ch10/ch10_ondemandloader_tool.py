import asyncio
import models_config
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.tools.ondemand_loader_tool import OnDemandLoaderTool
from llama_index.readers.wikipedia import WikipediaReader


async def main() -> None:
    tool = OnDemandLoaderTool.from_defaults(
        WikipediaReader(),
        name="WikipediaReader",
        description="args: {'pages': [<list of pages>], 'query_str': <query>}",
    )
    agent = ReActAgent(
        tools=[tool],
        verbose=True,
        streaming=False,
    )
    handler = agent.run("List top 3 countries by population")
    async for ev in handler.stream_events():
        cls = ev.__class__.__name__
        if "Tool" in cls or "Agent" in cls or "Step" in cls:
            print(f"{cls}: {ev}")
    response = await handler
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
