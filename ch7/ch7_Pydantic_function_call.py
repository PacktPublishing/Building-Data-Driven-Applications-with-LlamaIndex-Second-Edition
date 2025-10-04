import json
import models_config
from llama_index.core import Settings
from pydantic import BaseModel, Field, ValidationError
from llama_index.llms.openai import OpenAI

class Invoice(BaseModel):
    invoice_id: str = Field(description="unique invoice identifier")
    total: float = Field(description="total amount")

llm = Settings.llm

schema = json.dumps(Invoice.model_json_schema(), indent=2)
text = "Invoice #INV-001 | Total: $42.90 | Thanks!"

prompt = f"""
You are an information extractor. Using ONLY the schema below,
return a single JSON object that conforms to this schema.
No preambles, no markdown, no extra text.
No ```json at the beginning

SCHEMA:
{schema}

TEXT:
{text}
"""

raw = llm.complete(prompt)
invoice = Invoice.model_validate_json(raw.text)

print(invoice)

