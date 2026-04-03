import asyncio
from llama_cloud import AsyncLlamaCloud
client = AsyncLlamaCloud()
async def parse_document():
    file_obj = await client.files.create(
        file="./files/nist.ai.100-1.pdf",
        purpose="parse",
    )
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="cost_effective",
        version="latest",
        expand=["markdown"],
    )
    for page in result.markdown.pages:
        print(page.markdown[:500])
        print("---")

asyncio.run(parse_document())