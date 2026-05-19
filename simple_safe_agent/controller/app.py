#!/usr/bin/env python3
"""
Controller Service
- Orchestrates Privileged and Quarantined LLMs
- Manages variable storage (untrusted content isolation)
- Executes tools on behalf of Privileged LLM
- Handles variable substitution
- User-facing HTTP API
"""

import os
import re
import requests
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Service URLs
PRIVILEGED_LLM_URL = os.getenv("PRIVILEGED_LLM_URL", "http://privileged:5001")
QUARANTINED_LLM_URL = os.getenv("QUARANTINED_LLM_URL", "http://quarantined:5002")


class QueryRequest(BaseModel):
    query: str


class Controller:
    """Controller orchestrating the dual LLM system"""

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.var_counter = 0
        self.conversation_history: List[str] = []

    def allocate_variable(self, content: Any) -> str:
        """Allocate a new variable and store content"""
        self.var_counter += 1
        var_name = f"$VAR{self.var_counter}"
        self.variables[var_name] = content
        print(f"  [Controller] Stored content in {var_name}")
        return var_name

    def substitute_variables(self, text: str) -> str:
        """Substitute variable names with actual content"""
        result = text
        for var_name, content in self.variables.items():
            if var_name in result:
                if isinstance(content, list):
                    content_str = "\n\n".join([
                        f"From: {e.get('from', 'unknown')}\n"
                        f"Subject: {e.get('subject', 'no subject')}\n"
                        f"Date: {e.get('date', 'unknown')}\n\n"
                        f"{e.get('body', 'empty')}"
                        for e in content
                    ])
                else:
                    content_str = str(content)

                result = result.replace(var_name, content_str)
        return result

    def execute_action(self, action: str) -> Optional[Dict]:
        """Execute an action requested by Privileged LLM"""
        action = action.strip()

        match = re.match(r'(\w+)\((.*?)\)', action)
        if not match:
            return {"error": "Invalid action format"}

        tool_name = match.group(1)
        params = match.group(2).strip('\'"')

        print(f"  [Controller] Executing: {tool_name}({params})")

        if tool_name == "fetch_latest_emails":
            count = int(params) if params.isdigit() else 1

            try:
                response = requests.post(
                    f"{PRIVILEGED_LLM_URL}/emails/latest",
                    json={"count": count},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                emails = data['emails']
                var_name = self.allocate_variable(emails)
                result = f"Fetched {len(emails)} email(s) and stored in {var_name}"
                self.conversation_history.append(f"Action completed: {result}")
                return {"type": "info", "message": result}

            except Exception as e:
                return {"type": "error", "message": f"Failed to fetch emails: {str(e)}"}

        elif tool_name == "search_emails":
            query = params

            try:
                response = requests.post(
                    f"{PRIVILEGED_LLM_URL}/emails/search",
                    json={"query": query},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                emails = data['emails']
                var_name = self.allocate_variable(emails)
                result = f"Found {len(emails)} email(s) matching '{query}' and stored in {var_name}"
                self.conversation_history.append(f"Action completed: {result}")
                return {"type": "info", "message": result}

            except Exception as e:
                return {"type": "error", "message": f"Failed to search emails: {str(e)}"}

        elif tool_name == "quarantined_llm":
            # Substitute variables before sending to Quarantined LLM
            prompt_with_content = self.substitute_variables(params)

            try:
                response = requests.post(
                    f"{QUARANTINED_LLM_URL}/process",
                    json={"prompt": prompt_with_content},
                    timeout=60
                )
                response.raise_for_status()
                result_data = response.json()

                # Store result in a new variable (it's tainted!)
                var_name = self.allocate_variable(result_data['result'])
                message = f"Quarantined LLM completed. Result stored in {var_name}"
                self.conversation_history.append(f"Action completed: {message}")
                return {"type": "info", "message": message}

            except Exception as e:
                return {"type": "error", "message": f"Quarantined LLM error: {str(e)}"}

        elif tool_name == "display":
            final_message = self.substitute_variables(params)
            return {"type": "display", "message": final_message}

        return {"type": "error", "message": f"Unknown tool: {tool_name}"}

    def process_user_request(self, user_input: str) -> Dict:
        """Process a user request through the dual LLM system"""
        print(f"\n[User Request] {user_input}")

        try:
            response = requests.post(
                f"{PRIVILEGED_LLM_URL}/process",
                json={
                    "user_input": user_input,
                    "conversation_history": self.conversation_history
                },
                timeout=60
            )
            response.raise_for_status()
            llm_data = response.json()
            llm_response = llm_data['response']

            print(f"[Privileged LLM] {llm_response}")

            action_pattern = r'ACTION:\s*(.+?)(?=\n|$)'
            actions = re.findall(action_pattern, llm_response, re.IGNORECASE)

            if not actions:
                return {
                    "status": "error",
                    "message": "No actions found in LLM response",
                    "llm_response": llm_response
                }

            results = []
            display_message = None

            for action in actions:
                result = self.execute_action(action)
                if result:
                    results.append(result)
                    if result.get("type") == "display":
                        display_message = result.get("message")

            return {
                "status": "success",
                "llm_response": llm_response,
                "actions": results,
                "display": display_message
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Controller error: {str(e)}"
            }


# Initialize controller
controller = Controller()


@app.get('/health')
def health():
    return {"status": "healthy", "service": "controller"}


@app.post('/query')
def query(body: QueryRequest):
    result = controller.process_user_request(body.query)
    return JSONResponse(content=result)


@app.get('/demo')
def demo():
    demo_queries = [
        "Summarize my latest email",
        "Search for emails about 'security' and tell me what you find"
    ]

    results = []
    for q in demo_queries:
        result = controller.process_user_request(q)
        results.append({"query": q, "result": result})

    return {"demo_results": results}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
