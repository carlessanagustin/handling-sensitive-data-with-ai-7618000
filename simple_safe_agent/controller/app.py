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
from flask import Flask, request, jsonify

app = Flask(__name__)

# Service URLs
PRIVILEGED_LLM_URL = os.getenv("PRIVILEGED_LLM_URL", "http://privileged:5001")
QUARANTINED_LLM_URL = os.getenv("QUARANTINED_LLM_URL", "http://quarantined:5002")


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
                    # List of emails
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
        
        # Parse action
        match = re.match(r'(\w+)\((.*?)\)', action)
        if not match:
            return {"error": "Invalid action format"}
        
        tool_name = match.group(1)
        params = match.group(2).strip('\'"')
        
        print(f"  [Controller] Executing: {tool_name}({params})")
        
        # Execute tool
        if tool_name == "fetch_latest_emails":
            count = int(params) if params.isdigit() else 1
            
            try:
                # Call Privileged LLM's email API
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
                # Call Privileged LLM's email search API
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
            # Substitute variables in the prompt before sending to Quarantined LLM
            prompt_with_content = self.substitute_variables(params)
            
            # Call Quarantined LLM via HTTP
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
            # Substitute variables and return for display
            final_message = self.substitute_variables(params)
            return {"type": "display", "message": final_message}
        
        return {"type": "error", "message": f"Unknown tool: {tool_name}"}
    
    def process_user_request(self, user_input: str) -> Dict:
        """Process a user request through the dual LLM system"""
        print(f"\n[User Request] {user_input}")
        
        # Call Privileged LLM via HTTP
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
            
            # Extract and execute actions
            action_pattern = r'ACTION:\s*(.+?)(?=\n|$)'
            actions = re.findall(action_pattern, llm_response, re.IGNORECASE)
            
            if not actions:
                return {
                    "status": "error",
                    "message": "No actions found in LLM response",
                    "llm_response": llm_response
                }
            
            # Execute each action
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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "controller"})


@app.route('/query', methods=['POST'])
def query():
    """
    Main user-facing endpoint
    
    Expected JSON body:
    {
        "query": "Summarize my latest email"
    }
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"error": "Missing 'query' field"}), 400
        
        user_query = data['query']
        result = controller.process_user_request(user_query)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/demo', methods=['GET'])
def demo():
    """Run a simple demo"""
    demo_queries = [
        "Summarize my latest email",
        "Search for emails about 'security' and tell me what you find"
    ]
    
    results = []
    for query in demo_queries:
        result = controller.process_user_request(query)
        results.append({"query": query, "result": result})
    
    return jsonify({"demo_results": results})


if __name__ == '__main__':
    # Run on port 5000, this is the user-facing service
    app.run(host='0.0.0.0', port=5000, debug=False)
