import models_config
from pydantic import BaseModel, Field
from llama_index.core import Settings

class Album(BaseModel):
    name: str = Field(description="Album title")
    artist: str
    songs: list[str]

struct_llm = Settings.llm.as_structured_llm(Album)
response = struct_llm.complete("Generate a 3-song album by Taylor Swift")
print(response.raw)