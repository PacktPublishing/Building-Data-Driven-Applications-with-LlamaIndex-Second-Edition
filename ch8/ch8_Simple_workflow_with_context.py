import asyncio
import models_config
from llama_index.core import Settings
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Event,
    Context,
)

class Generated(Event):
    text: str

class Summarized(Event):
    summary: str

class SimpleWorkflow(Workflow):
    @step(pass_context=True)
    async def generate(self, ctx: Context, ev: StartEvent) -> Generated:
        query = ev.get("query")
        llm = Settings.llm
        response = await llm.acomplete(query)
        await ctx.store.set("raw_answer", response.text)
        return Generated(text=response.text)

    @step()
    async def summarize(self, ev: Generated) -> Summarized:
        llm = Settings.llm
        prompt = f"reply only with a one-sentence summary of this text:\n\n{ev.text}"
        summary = await llm.acomplete(prompt)
        return Summarized(summary=summary.text)

    @step(pass_context=True)
    async def extract_keywords(self, ctx: Context, ev: Summarized) -> StopEvent:
        llm = Settings.llm
        raw_answer = await ctx.store.get("raw_answer")
        prompt = f"extract 5 concise keywords from the following text, comma-separated only:\n\n{raw_answer}"
        kw = await llm.acomplete(prompt)
        keywords = [k.strip() for k in kw.text.split(",") if k.strip()]
        await ctx.store.set("keywords", keywords)
        return StopEvent(result={"summary": ev.summary, "keywords": keywords})

async def main():
    workflow = SimpleWorkflow(timeout=30)
    result = await workflow.run(query="Who was Albert Einstein?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
