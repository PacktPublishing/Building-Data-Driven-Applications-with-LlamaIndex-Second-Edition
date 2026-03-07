import models_config
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.chat_engine import SimpleChatEngine

SESSION_ID = "user_X"
STORE_PATH = "chat_memory.json"

try:
    chat_store = SimpleChatStore.from_persist_path(persist_path=STORE_PATH)
except FileNotFoundError:
    chat_store = SimpleChatStore()

seed_history = chat_store.get_messages(SESSION_ID)
chat_engine = SimpleChatEngine.from_defaults()

first_turn = True
while True:
    user_message = input("You: ")
    if user_message.lower() == "exit":
        break
    if first_turn and seed_history:
        response = chat_engine.chat(user_message, chat_history=seed_history)
        first_turn = False
    else:
        response = chat_engine.chat(user_message)
    print(f"Assistant: {response}")

chat_store.set_messages(SESSION_ID, chat_engine.chat_history)
chat_store.persist(persist_path=STORE_PATH)
