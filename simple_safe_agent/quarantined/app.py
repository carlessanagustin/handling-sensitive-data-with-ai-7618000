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
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI()

PROVIDER = os.getenv("PROVIDER", "claude").lower()
if PROVIDER == "claude":
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable required")
    llm = ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
        temperature=0.3,
        api_key=ANTHROPIC_API_KEY,
    )
elif PROVIDER == "ollama":
    from langchain_ollama import ChatOllama
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        temperature=0.3,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
    )
elif PROVIDER == "mistral":
    from langchain_mistralai import ChatMistralAI
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY environment variable required")
    llm = ChatMistralAI(
        model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        temperature=0.3,
        api_key=MISTRAL_API_KEY,
    )
else:
    raise RuntimeError(f"Unknown PROVIDER '{PROVIDER}': must be 'claude', 'ollama', or 'mistral'")

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
