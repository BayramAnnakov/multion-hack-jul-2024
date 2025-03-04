import dotenv

dotenv.load_dotenv()

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

from mem0 import Memory

app = FastAPI()

config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                }
            },
        }

m = Memory.from_config(config)


class Structured(BaseModel):
    title: str
    overview: str
    emoji: str
    category: str
    actionItems: List[str]


class FriendMemory(BaseModel):
    id: int
    createdAt: str
    transcript: str
    structured: Structured
    pluginsResponse: List[str] = []
    discarded: bool


@app.post("/webhook")
def webhook(memory: FriendMemory):
    print(memory) # process your memory here
    m.add(memory.transcript, user_id="Bayram", metadata={"category": "daily memories"})
    return memory

