import asyncio
import models_config
from llama_index.core import Settings
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Event,
)

class Generated(Event):
    text: str

class SimpleWorkflow(Workflow):
    @step()
    async def generate(self, ev: StartEvent) -> Generated:
        query = ev.get("query")
        llm = Settings.llm
        response = await llm.acomplete(query)
        return Generated(text=response.text)

    @step()
    async def summarize(self, ev: Generated) -> StopEvent:
        llm = Settings.llm
        prompt = f"reply only with a one-sentence summary of this text:\n\n{ev.text}"
        summary = await llm.acomplete(prompt)
        return StopEvent(result=summary.text)

async def main():
    workflow = SimpleWorkflow(timeout=30)
    result = await workflow.run(query="Who was Albert Einstein?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
