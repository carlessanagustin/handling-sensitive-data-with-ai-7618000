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
from typing import List, Dict
from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

app = Flask(__name__)

# Initialize LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable required")

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0.3,
    api_key=OPENAI_API_KEY
)

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
        """Load emails from CSV file"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.emails = list(reader)
            print(f"✓ Loaded {len(self.emails)} emails")
        except Exception as e:
            print(f"WARNING: Failed to load emails: {e}")
            self.emails = []
    
    def fetch_latest_emails(self, count: int = 1) -> List[Dict]:
        """Fetch the latest N emails"""
        return self.emails[-count:] if self.emails else []
    
    def search_emails(self, query: str) -> List[Dict]:
        """Search emails by subject or body content"""
        query_lower = query.lower()
        results = []
        for email in self.emails:
            subject = email.get('subject', '').lower()
            body = email.get('body', '').lower()
            if query_lower in subject or query_lower in body:
                results.append(email)
        return results


# Initialize email store
email_store = EmailStore("/app/mock_emails.csv")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "privileged-llm",
        "emails_loaded": len(email_store.emails)
    })


@app.route('/emails/latest', methods=['POST'])
def fetch_latest_emails():
    """
    Fetch latest emails
    
    Expected JSON body:
    {
        "count": 1
    }
    """
    try:
        data = request.get_json() or {}
        count = data.get('count', 1)
        
        emails = email_store.fetch_latest_emails(count)
        
        return jsonify({
            "emails": emails,
            "count": len(emails),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/emails/search', methods=['POST'])
def search_emails():
    """
    Search emails
    
    Expected JSON body:
    {
        "query": "security"
    }
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        query = data['query']
        emails = email_store.search_emails(query)
        
        return jsonify({
            "emails": emails,
            "count": len(emails),
            "query": query,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/process', methods=['POST'])
def process():
    """
    Process user request and return action plan
    
    Expected JSON body:
    {
        "user_input": "Summarize my latest email",
        "conversation_history": ["previous context..."]
    }
    """
    try:
        data = request.get_json()
        if not data or 'user_input' not in data:
            return jsonify({"error": "Missing 'user_input' field"}), 400
        
        user_input = data['user_input']
        conversation_history = data.get('conversation_history', [])
        
        # Build conversation context
        history_context = "\n".join(conversation_history) if conversation_history else "No previous context."
        
        full_prompt = f"""Previous context:
{history_context}

User request: {user_input}

What actions should be taken? Respond with ACTION: statements."""
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=full_prompt)
        ]
        
        response = llm.invoke(messages)
        
        return jsonify({
            "response": response.content,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run on port 5001, accessible only within Docker network
    app.run(host='0.0.0.0', port=5001, debug=False)
