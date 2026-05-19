#!/usr/bin/env python3
"""
Privileged LLM Service
- Core AI assistant with tool access
- Processes trusted user input
- NEVER sees untrusted content directly (only variable names)
- Manages email store
- Coordinates with Controller via HTTP API
"""

import os
import csv
from typing import List, Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI()

# Initialize LLM
PROVIDER = os.getenv("PROVIDER", "claude").lower()
if PROVIDER == "claude":
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable required")
    llm = ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
        temperature=0.3,
        api_key=ANTHROPIC_API_KEY,
    )
elif PROVIDER == "ollama":
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        temperature=0.3,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
    )
elif PROVIDER == "mistral":
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

SYSTEM_PROMPT = """You are a privileged AI assistant with access to tools.

AVAILABLE TOOLS:
1. fetch_latest_emails(count) - Fetch the N most recent emails
   Returns: Assigns email content to a variable (e.g., $VAR1)

2. search_emails(query) - Search emails by subject or body
   Returns: Assigns matching emails to a variable (e.g., $VAR1)

3. quarantined_llm(prompt) - Process untrusted content safely
   Use this to summarize or analyze email content stored in variables
   Example: quarantined_llm('Summarize this email: $VAR1')
   Returns: Assigns result to a variable (e.g., $VAR2)

4. display(message) - Display a message to the user
   Use variables in your message (e.g., "Your summary: $VAR2")
   The Controller will substitute variables when displaying to user

CRITICAL RULES:
- You NEVER see actual email content, only variable names ($VAR1, $VAR2, etc.)
- Always use quarantined_llm() to process any variable containing email content
- When displaying results to users, reference variables that will be substituted
- Plan your actions step by step

Your responses should be tool calls in this format:
ACTION: tool_name(parameters)

You can chain multiple actions. Think step by step."""


class EmailStore:
    """Email storage and retrieval"""

    def __init__(self, csv_path: str):
        self.emails = []
        self.load_emails(csv_path)

    def load_emails(self, csv_path: str):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.emails = list(reader)
            print(f"✓ Loaded {len(self.emails)} emails")
        except Exception as e:
            print(f"WARNING: Failed to load emails: {e}")
            self.emails = []

    def fetch_latest_emails(self, count: int = 1) -> List[Dict]:
        return self.emails[-count:] if self.emails else []

    def search_emails(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        return [
            e for e in self.emails
            if query_lower in e.get('subject', '').lower()
            or query_lower in e.get('body', '').lower()
        ]


# Initialize email store
email_store = EmailStore("/app/mock_emails.csv")


# --- Request/response models ---

class FetchLatestRequest(BaseModel):
    count: int = 1


class SearchRequest(BaseModel):
    query: str


class ProcessRequest(BaseModel):
    user_input: str
    conversation_history: Optional[List[str]] = []


# --- Routes ---

@app.get('/health')
def health():
    return {"status": "healthy", "service": "privileged-llm", "emails_loaded": len(email_store.emails)}


@app.post('/emails/latest')
def fetch_latest_emails(body: FetchLatestRequest):
    emails = email_store.fetch_latest_emails(body.count)
    return {"emails": emails, "count": len(emails), "status": "success"}


@app.post('/emails/search')
def search_emails(body: SearchRequest):
    emails = email_store.search_emails(body.query)
    return {"emails": emails, "count": len(emails), "query": body.query, "status": "success"}


@app.post('/process')
def process(body: ProcessRequest):
    history_context = "\n".join(body.conversation_history) if body.conversation_history else "No previous context."

    full_prompt = f"""Previous context:
{history_context}

User request: {body.user_input}

What actions should be taken? Respond with ACTION: statements."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=full_prompt)
    ]

    response = llm.invoke(messages)
    return {"response": response.content, "status": "success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
