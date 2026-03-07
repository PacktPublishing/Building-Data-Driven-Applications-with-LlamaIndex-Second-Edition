import asyncio
import json
import re
from typing import List, Literal, Optional

import models_config
from pydantic import BaseModel, Field

from llama_index.core.agent.workflow import AgentWorkflow, ReActAgent
from llama_index.core.workflow import Context, HumanResponseEvent, InputRequiredEvent
from llama_index.readers.web import RssReader

NIST_NVD_RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"


class AdvisoryItem(BaseModel):
    title: str = Field(..., description="Title from the RSS item.")
    link: Optional[str] = Field(None, description="URL to the advisory.")
    published: Optional[str] = Field(None, description="Published date/time if available.")
    cve_id: Optional[str] = Field(None, description="Extracted CVE ID if present, else null.")
    severity: Literal["critical", "high", "medium", "low", "unknown"] = Field(
        "unknown",
        description="Best-effort severity classification based on available info.",
    )
    suggested_action: str = Field(..., description="One concrete next step.")


class AdvisoryDigest(BaseModel):
    source_url: str = Field(..., description="RSS source URL.")
    approved: bool = Field(..., description="Whether a human approved publishing.")
    items: List[AdvisoryItem] = Field(..., description="Exactly 3 highlighted advisories.")


def fetch_nist_nvd_rss(
    keyword: str = "Windows",
    feed_url: str = NIST_NVD_RSS_URL,
    max_items: int = 200,
) -> str:
    docs = RssReader().load_data(urls=[feed_url])
    kw = (keyword or "").strip().lower()
    items: list[dict] = []

    for d in docs:
        meta = getattr(d, "metadata", {}) or {}
        title = meta.get("title") or ""
        link = meta.get("link")
        published = meta.get("date")
        text = getattr(d, "text", "") or ""

        haystack = f"{title}\n{text}".lower()
        if kw and kw not in haystack:
            continue

        m = re.search(r"CVE-\d{4}-\d{4,}", f"{title}\n{link or ''}\n{text}")
        cve_id = m.group(0) if m else None

        items.append(
            {
                "title": title,
                "link": link,
                "published": published,
                "cve_id": cve_id,
                "text": text[:1200],
            }
        )

        if len(items) >= max_items:
            break

    print(f"RSS READ (filtered='{keyword}'): {len(items)} items")
    return json.dumps({"source_url": feed_url, "items": items}, ensure_ascii=False)


async def request_approval(ctx: Context, summary: str) -> str:
    approved = await ctx.store.get("approved", default=None)
    if approved is not None:
        return json.dumps({"approved": bool(approved)}, ensure_ascii=False)

    prompt = f"\nHUMAN APPROVAL REQUIRED\n\n{summary.strip()}\n\nApprove? (y/n)\n> "
    ctx.write_event_to_stream(InputRequiredEvent(prefix=prompt, user_name="approver"))
    ev = await ctx.wait_for_event(HumanResponseEvent, requirements={"user_name": "approver"})
    approved_now = ev.response.strip().lower().startswith("y")
    await ctx.store.set("approved", approved_now)
    return json.dumps({"approved": approved_now}, ensure_ascii=False)


async def main() -> None:
    fetch_agent = ReActAgent(
        name="FetchAgent",
        description="Fetch Windows-related entries from the NIST NVD RSS feed.",
        tools=[fetch_nist_nvd_rss],
        can_handoff_to=["TriageAgent"],
        max_iterations=3,
        verbose=False,
        streaming=False,
        system_prompt=(
            "Call fetch_nist_nvd_rss exactly once.\n"
            "Use keyword='Windows'.\n"
            "Return ONLY the tool output JSON.\n"
            "Then hand off to TriageAgent.\n"
        ),
    )

    triage_agent = ReActAgent(
        name="TriageAgent",
        description="Select top 3 items and require human approval before returning a digest.",
        tools=[request_approval],
        can_handoff_to=[],
        max_iterations=6,
        verbose=False,
        streaming=False,
        output_cls=AdvisoryDigest,
        system_prompt=(
            "You will receive JSON with keys: source_url, items.\n"
            "Steps:\n"
            "1) Read ALL items.\n"
            "2) Pick exactly 3 to highlight.\n"
            "3) Build a 3-line summary (one line per item: title + CVE if present).\n"
            "4) Call request_approval(summary) exactly once.\n"
            "5) Set approved based ONLY on the tool result.\n"
            "6) Return AdvisoryDigest structured output.\n"
            "Rules:\n"
            "- Do not invent items.\n"
            "- Use the original title/link/published/cve_id fields.\n"
        ),
    )

    workflow = AgentWorkflow(
        agents=[fetch_agent, triage_agent],
        root_agent=fetch_agent.name,
        initial_state={"approved": None},
        output_cls=AdvisoryDigest,
        timeout=180,
    )

    user_msg = "Fetch Windows-related NIST NVD RSS items, pick the top 3, require approval, return a digest."
    print(f"INPUT: {user_msg}")

    handler = workflow.run(user_msg=user_msg)

    current_agent = None
    async for ev in handler.stream_events():
        if isinstance(ev, InputRequiredEvent):
            user_text = await asyncio.to_thread(input, ev.prefix)
            handler.ctx.send_event(HumanResponseEvent(response=user_text, user_name=ev.user_name))
            continue

        agent_name = getattr(ev, "current_agent_name", None)
        if agent_name and agent_name != current_agent:
            current_agent = agent_name
            print(f"AGENT: {current_agent}")

    response = await handler
    model = response.get_pydantic_model(AdvisoryDigest)

    print("OUTPUT:")
    print(json.dumps(model.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
