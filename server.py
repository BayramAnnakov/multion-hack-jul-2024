from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Structured(BaseModel):
    title: str
    overview: str
    emoji: str
    category: str
    actionItems: List[str]


class Memory(BaseModel):
    id: int
    createdAt: str
    transcript: str
    structured: Structured
    pluginsResponse: List[str] = []
    discarded: bool


@app.post("/webhook")
def webhook(memory: Memory):
    print(memory) # process your memory here
    return memory

