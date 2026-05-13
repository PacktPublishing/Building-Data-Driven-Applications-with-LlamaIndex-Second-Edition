import asyncio
import models_config
from llama_index.core import VectorStoreIndex
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.objects import ObjectIndex
from llama_index.core.tools import FunctionTool

def hr_vacation_policy_lookup(topic: str) -> str:
    return (
        "HR policy excerpt: Contractors are not eligible for paid vacation. "
        "Exceptions require VP approval and must be documented in the contract addendum."
    )

def hr_holiday_calendar(country_code: str) -> str:
    return f"Holiday calendar for {country_code}: New Year, Easter, Labour Day, Christmas."

def finance_sales_by_region(quarter: str) -> str:
    return f"Sales by region for {quarter}: NA $12.4M, EMEA $9.1M, APAC $7.6M."

def it_create_ticket(title: str, details: str) -> str:
    return f"Created ticket: {title} (details: {details})"

def slack_send_message(channel: str, text: str) -> str:
    return f"Sent message to {channel}: {text}"

def util_generate_uuid() -> str:
    return "9f2c2e9a-8f30-4d3b-baa6-4a9f3bd1a2f1"


async def main() -> None:
    tools = [
        FunctionTool.from_defaults(
            fn=hr_vacation_policy_lookup,
            name="hr_vacation_policy_lookup",
            description="Look up HR vacation policy rules and exceptions by topic.",
        ),
        FunctionTool.from_defaults(
            fn=hr_holiday_calendar,
            name="hr_holiday_calendar",
            description="Return the holiday calendar for a given country code.",
        ),
        FunctionTool.from_defaults(
            fn=finance_sales_by_region,
            name="finance_sales_by_region",
            description="Return sales totals split by region for a quarter like 'Q3 2025'.",
        ),
        FunctionTool.from_defaults(
            fn=it_create_ticket,
            name="it_create_ticket",
            description="Create an IT support ticket with a title and details.",
        ),
        FunctionTool.from_defaults(
            fn=slack_send_message,
            name="slack_send_message",
            description="Send a Slack message to a channel.",
        ),
        FunctionTool.from_defaults(
            fn=util_generate_uuid,
            name="util_generate_uuid",
            description="Generate a random UUID string.",
        ),
    ]

    tool_index = ObjectIndex.from_objects(tools, index_cls=VectorStoreIndex)
    tool_retriever = tool_index.as_retriever(similarity_top_k=2)

    preview = tool_retriever.retrieve("vacation policy exceptions for contractors")
    print([t.metadata.name for t in preview])

    agent = ReActAgent(
        tool_retriever=tool_retriever,
        verbose=True,
        streaming=False,
    )

    handler = agent.run(
        "Summarize the vacation policy exceptions for contractors in 2 bullets. "
        "Use tools."
    )
    response = await handler
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
