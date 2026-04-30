import asyncio
from llama_index.core import Settings
from llama_index.core.agent.workflow import (
    AgentOutput,
    AgentWorkflow,
    ReActAgent,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama


Settings.llm = Ollama(
    model="qwen3.5:9b",
    base_url="http://localhost:11434",
    temperature=0.0,
    context_window=16000,
    request_timeout=120.0,
)


def lookup_expense_policy(category: str) -> str:
    """Look up the reimbursement policy for an expense category."""
    category_lower = category.lower()

    if any(
        term in category_lower
        for term in ("monitor", "hardware", "equipment", "work equipment")
    ):
        return (
            "External monitors are reimbursable up to 250 EUR when used for "
            "remote work. A receipt is required for hardware expenses over "
            "50 EUR."
        )

    return (
        "General business expenses are reimbursable when they are work-related, "
        "reasonable, and supported by a receipt."
    )


def lookup_worker_rules(worker_type: str) -> str:
    """Look up reimbursement rules for a worker type."""
    worker_type_lower = worker_type.lower()

    if "contractor" in worker_type_lower:
        return (
            "Contractors may expense approved work equipment only after manager "
            "approval. The approval must be obtained before reimbursement."
        )

    if "employee" in worker_type_lower:
        return (
            "Full-time employees may expense approved work equipment directly, "
            "as long as the expense follows the category policy."
        )

    return (
        "The worker type is not recognized. Apply the strictest rule and ask "
        "for manager approval before reimbursement."
    )


async def save_policy_finding(ctx: Context, finding: str) -> str:
    """Save the policy finding for the response agent."""
    async with ctx.store.edit_state() as ctx_state:
        ctx_state["state"]["policy_finding"] = finding

    return "Policy finding saved."


async def read_policy_finding(ctx: Context) -> str:
    """Read the saved policy finding."""
    state = await ctx.store.get("state", default={})
    finding = state.get("policy_finding")

    if not finding:
        return "No policy finding was saved."

    return finding


async def main() -> None:
    policy_agent = ReActAgent(
        name="PolicyAgent",
        description=(
            "Looks up expense policy rules and saves a concise policy finding."
        ),
        tools=[
            lookup_expense_policy,
            lookup_worker_rules,
            save_policy_finding,
        ],
        can_handoff_to=["ResponseAgent"],
        llm=Settings.llm,
        max_iterations=8,
        verbose=False,
        streaming=False,
        system_prompt=(
            "You are PolicyAgent. Inspect the user's request, identify the expense "
            "category and worker type, then use the available tools to check the "
            "relevant policy. Save one concise policy finding. After saving it, hand "
            "off to ResponseAgent. Do not write the final answer."
        ),
    )

    response_agent = ReActAgent(
        name="ResponseAgent",
        description=(
            "Writes the final employee-facing answer from the saved policy "
            "finding."
        ),
        tools=[read_policy_finding],
        can_handoff_to=[],
        llm=Settings.llm,
        max_iterations=4,
        verbose=False,
        streaming=False,
        system_prompt=(
            "You are ResponseAgent. Call read_policy_finding exactly once. "
            "Then write the final answer in plain language. Keep it short. "
            "Do not invent policy details."
        ),
    )

    workflow = AgentWorkflow(
        agents=[policy_agent, response_agent],
        root_agent=policy_agent.name,
        initial_state={"policy_finding": ""},
        timeout=120,
        verbose=False,
    )

    user_msg = (
        "A contractor asks whether they can expense a 180 EUR monitor for "
        "remote work. Check the policy and write a short answer."
    )

    print(f"INPUT: {user_msg}")

    handler = workflow.run(user_msg=user_msg)

    current_agent = None

    async for event in handler.stream_events():
        agent_name = getattr(event, "current_agent_name", None)

        if agent_name and agent_name != current_agent:
            current_agent = agent_name
            print(f"\nAGENT: {current_agent}")

        if isinstance(event, AgentOutput):
            if event.tool_calls:
                tool_names = [call.tool_name for call in event.tool_calls]
                print(f"PLANNED TOOLS: {tool_names}")

        elif isinstance(event, ToolCall):
            print(f"CALLING TOOL: {event.tool_name}")
            print(f"TOOL INPUT: {event.tool_kwargs}")

        elif isinstance(event, ToolCallResult):
            print(f"TOOL RESULT: {event.tool_output}")

    response = await handler

    print("\nFINAL RESPONSE:")
    print(str(response))


if __name__ == "__main__":
    asyncio.run(main())