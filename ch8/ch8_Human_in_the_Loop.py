import asyncio
from llama_index.core.workflow import (
    Workflow, step, StartEvent, StopEvent
)
from llama_index.core.workflow.events import InputRequiredEvent, HumanResponseEvent

class EmailWorkflow(Workflow):
    @step
    async def draft(self, ev: StartEvent) -> InputRequiredEvent:
        draft = f"Dear {ev.get('customer')}, we approved your refund."
        print("\nDRAFT EMAIL:\n", draft)
        return InputRequiredEvent(prefix="Approve this draft? (yes/no): ")

    @step
    async def review(self, ev: HumanResponseEvent) -> StopEvent:
        if ev.response.lower().startswith("y"):
            return StopEvent(result="Email approved and sent ✅")
        return StopEvent(result="Email rejected ❌")

async def main():
    wf = EmailWorkflow(timeout=30)
    handler = wf.run(customer="Alice")

    async for event in handler.stream_events():
        if isinstance(event, InputRequiredEvent):
            answer = input(event.prefix)
            handler.ctx.send_event(HumanResponseEvent(response=answer))

    print(await handler)

if __name__ == "__main__":
    asyncio.run(main())
