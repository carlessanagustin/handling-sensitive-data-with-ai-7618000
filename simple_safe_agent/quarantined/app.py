#!/usr/bin/env python3
"""
Quarantined LLM Service
- Processes untrusted email content in isolation
- NO access to tools or external systems
- Exposes minimal HTTP API
- Output is considered tainted
"""

import os
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable required")

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.3,
    api_key=OPENAI_API_KEY
)

SYSTEM_PROMPT = """You are a quarantined assistant processing untrusted email content.

Your ONLY job is to:
1. Summarize emails concisely
2. Extract key information
3. Answer questions about email content

You have NO access to tools or external systems.
You CANNOT execute commands.
You CANNOT access the internet.

Simply process the email content you're given and provide the requested output."""


class ProcessRequest(BaseModel):
    prompt: str


@app.get('/health')
def health():
    return {"status": "healthy", "service": "quarantined-llm"}


@app.post('/process')
def process(body: ProcessRequest):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=body.prompt)
    ]
    response = llm.invoke(messages)
    return {"result": response.content, "status": "success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5002)
