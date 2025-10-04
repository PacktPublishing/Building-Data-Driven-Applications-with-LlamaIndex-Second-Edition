import asyncio
from llama_index.core.workflow import (
    Workflow, step, Event, StartEvent, StopEvent
)

class CalcQuery(Event):
    expr: str

class RagQuery(Event):
    question: str

class DraftAnswer(Event):
    text: str

class NeedsFix(Event):
    prior: str

class FinalAnswer(Event):
    text: str

class BranchLoopWorkflow(Workflow):
    @step
    async def classify(self, ev: StartEvent) -> CalcQuery | RagQuery:
        q = ev.get("query", "")
        if any(ch.isdigit() for ch in q) and any(op in q for op in "+-*/"):
            return CalcQuery(expr=q)
        return RagQuery(question=q)

    @step
    async def calculator(self, ev: CalcQuery) -> DraftAnswer:
        try:
            result = str(eval(ev.expr, {"__builtins__": {}}))
        except Exception as e:
            result = f"error: {e}"
        return DraftAnswer(text=result)

    @step
    async def retriever(self, ev: RagQuery) -> DraftAnswer:
        return DraftAnswer(text=f"(draft) answer to: {ev.question}")

    @step
    async def validate(self, ev: DraftAnswer) -> FinalAnswer | NeedsFix:
        if len(ev.text) < 10:
            return NeedsFix(prior=ev.text)
        return FinalAnswer(text=ev.text)

    @step
    async def fix(self, ev: NeedsFix) -> DraftAnswer:
        return DraftAnswer(text=ev.prior + " (expanded to be clearer)")

    @step
    async def finalize(self, ev: FinalAnswer) -> StopEvent:
        return StopEvent(result=ev.text)
async def main():
    wf = BranchLoopWorkflow(timeout=20, verbose=True)
    print(await wf.run(query="2+2"))
    print(await wf.run(query="Explain RAG workflows"))

if __name__ == "__main__":
    asyncio.run(main())
