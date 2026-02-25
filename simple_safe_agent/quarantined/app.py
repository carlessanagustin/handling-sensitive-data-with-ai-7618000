#!/usr/bin/env python3
"""
Quarantined LLM Service
- Processes untrusted email content in isolation
- NO access to tools or external systems
- Exposes minimal HTTP API
- Output is considered tainted
"""

import os
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

SYSTEM_PROMPT = """You are a quarantined assistant processing untrusted email content.

Your ONLY job is to:
1. Summarize emails concisely
2. Extract key information
3. Answer questions about email content

You have NO access to tools or external systems.
You CANNOT execute commands.
You CANNOT access the internet.

Simply process the email content you're given and provide the requested output."""


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "quarantined-llm"})


@app.route('/process', methods=['POST'])
def process():
    """
    Process untrusted content
    
    Expected JSON body:
    {
        "prompt": "Summarize this email: ..."
    }
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        prompt = data['prompt']
        
        # Process with LLM
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        
        return jsonify({
            "result": response.content,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run on port 5002, accessible only within Docker network
    app.run(host='0.0.0.0', port=5002, debug=False)
