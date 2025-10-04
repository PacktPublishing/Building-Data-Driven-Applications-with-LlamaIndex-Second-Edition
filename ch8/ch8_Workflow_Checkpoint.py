import asyncio
import random

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
from workflows.retry_policy import ConstantDelayRetryPolicy

class ServiceResult(Event):
    text: str

class Summarized(Event):
    summary: str

class CheckpointDemoWorkflow(Workflow):
    @step(pass_context=True, retry_policy=ConstantDelayRetryPolicy(delay=2, maximum_attempts=5))
    async def unreliable_service(self, ctx: Context, ev: StartEvent) -> ServiceResult:
        cached = await ctx.store.get("service_text", default=None)
        if cached is not None:
            return ServiceResult(text=cached)
        query = ev.get("query", "Who was Albert Einstein?")
        if random.random() < 0.5:
            raise RuntimeError("Transient external service error")
        text = f"Service response for: {query}"
        await ctx.store.set("service_text", text)
        return ServiceResult(text=text)

    @step(retry_policy=ConstantDelayRetryPolicy(delay=2, maximum_attempts=5))
    async def summarize(self, ev: ServiceResult) -> Summarized:
        if random.random() < 0.5:
            raise RuntimeError("Summarization failed (simulated)")
        llm = Settings.llm
        prompt = f"Reply with a one-sentence summary of this text:\n\n{ev.text}"
        r = await llm.acomplete(prompt)
        return Summarized(summary=r.text)

    @step(pass_context=True)
    async def finalize(self, ctx: Context, ev: Summarized) -> StopEvent:
        service_text = await ctx.store.get("service_text")
        return StopEvent(result={"service_text": service_text, "summary": ev.summary})


async def main():
    wf = CheckpointDemoWorkflow(timeout=30, verbose=True)
    handler = wf.run(query="Who was Albert Einstein?")

    try:
        result = await handler
        print("RESULT:", result)
    except Exception as e:
        print(f"[run] failed: {e!r}")
        wf2 = CheckpointDemoWorkflow(timeout=30, verbose=True)
        resumed = await wf2.run(ctx=handler.ctx, query="Who was Albert Einstein?")
        print("RESUMED RESULT:", resumed)


if __name__ == "__main__":
    asyncio.run(main())
