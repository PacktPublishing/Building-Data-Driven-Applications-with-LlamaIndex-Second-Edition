import models_config
from pydantic import BaseModel, Field
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.core.prompts import ChatPromptTemplate

class Album(BaseModel):
    name: str = Field(description="Album title")
    artist: str
    songs: list[str]

chat_prompt = ChatPromptTemplate([
    ChatMessage.from_str("Generate a 3-song album by {artist}", role="user")
])

album = Settings.llm.structured_predict(
    Album,
    chat_prompt,
    artist="Taylor Swift",
)
print(album)
