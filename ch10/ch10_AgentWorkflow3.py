import asyncio
import models_config
import json
import re
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.workflow import Context, HumanResponseEvent, InputRequiredEvent
from llama_index.readers.web import RssReader

NIST_NVD_RSS_URL = "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml"
_RSS_ITEMS: list[dict] = []

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
    max_items: int = 60,
) -> str:
    global _RSS_ITEMS
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
    _RSS_ITEMS = items
    print(f"RSS READ (filtered='{keyword}'): {len(_RSS_ITEMS)} items")
    return f"Read {len(_RSS_ITEMS)} filtered RSS items from {feed_url}."

def get_rss_items() -> str:
    return json.dumps(
        {"source_url": NIST_NVD_RSS_URL, "items": _RSS_ITEMS},
        ensure_ascii=False,
    )

async def request_approval(ctx: Context, summary: str) -> str:
    cached = await ctx.get("approval_json", default=None)
    if cached:
        return cached

    prompt = f"\nHUMAN APPROVAL REQUIRED\n\n{summary.strip()}\n\nApprove? (y/n)\n> "
    ctx.write_event_to_stream(InputRequiredEvent(prefix=prompt, user_name="approver"))
    ev = await ctx.wait_for_event(HumanResponseEvent, requirements={"user_name": "approver"})
    approved = ev.response.strip().lower().startswith("y")
    out = json.dumps({"approved": approved}, ensure_ascii=False)
    await ctx.set("approval_json", out)
    return out

async def main() -> None:
    rss_agent = FunctionAgent(
        tools=[fetch_nist_nvd_rss],
        system_prompt=(
            "Call fetch_nist_nvd_rss exactly once. "
            "Use keyword='Windows'. Return a short confirmation."
        ),
        name="RssAgent",
        description="Fetches the NIST NVD RSS feed (filtered).",
    )

    main_agent = FunctionAgent(
        name="MainAgent",
        tools=[get_rss_items, request_approval],
        description="Selects top 3 items, requires approval, returns a structured digest.",
        system_prompt=(
            "You orchestrate this workflow.\n"
            "1) Hand off to RssAgent.\n"
            "2) Call get_rss_items and read ALL returned items.\n"
            "3) Select exactly 3 items to highlight.\n"
            "4) Build a 3-line summary (one line per item: title + CVE if present).\n"
            "5) You MUST call request_approval(summary) after selecting the 3 items.\n"
            "6) Use ONLY the tool result to set approved in AdvisoryDigest.\n"
            "7) Return AdvisoryDigest structured output.\n"
            "Rules: Do not invent items. Use only titles/links/published/cve_id from get_rss_items.\n"
        ),
        can_handoff_to=["RssAgent"],
        output_cls=AdvisoryDigest,
    )

    workflow = AgentWorkflow(
        agents=[main_agent, rss_agent],
        root_agent=main_agent.name,
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
