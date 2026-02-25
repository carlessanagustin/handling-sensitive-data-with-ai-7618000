# Simple Safe Agent - Dual LLM Pattern

A secure email processing system implementing the Dual LLM pattern with isolated Docker containers for maximum security.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User/Client                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (port 5050)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Controller Service                        │
│  • Orchestrates dual LLM system                             │
│  • Manages variable storage ($VAR1, $VAR2, etc.)            │
│  • NEVER exposes untrusted content to Privileged LLM        │
│  • Coordinates actions between services                     │
└────────────┬─────────────────────────────┬──────────────────┘
             │                             │
             │ HTTP (internal)             │ HTTP (internal)
             ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│   Privileged LLM         │  │   Quarantined LLM            │
│   • Email store          │  │   • NO tool access           │
│   • Has tool access      │  │   • Processes untrusted data │
│   • Sees only variables  │  │   • Can go rogue             │
│   • Trusted input only   │  │   • Isolated processing      │
│   • Port 5001 (internal) │  │   • Port 5002 (internal)     │
└──────────────────────────┘  └──────────────────────────────┘
```

## Security Features

### Container Isolation
- ✅ **Privileged LLM**: No direct access to untrusted content
- ✅ **Quarantined LLM**: No tool access, fully isolated
- ✅ **Controller**: Only service exposed to host (port 5000)
- ✅ **Non-root users** in all containers
- ✅ **Read-only email data** mounts
- ✅ **Resource limits** (CPU/Memory)

### Dual LLM Pattern
- ✅ Privileged LLM never sees email content directly
- ✅ Variables ($VAR1, $VAR2) used to reference untrusted data
- ✅ Quarantined LLM processes all untrusted content
- ✅ Controller manages variable substitution safely

## Quick Start

### Prerequisites
- Docker Desktop for Mac (Apple Silicon)
- OpenAI API key

### Setup (2 commands)

1. **Export your OpenAI API key:**
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

2. **Run with Docker Compose:**
```bash
docker-compose up --build
```

That's it! The system will start all three services.

## Usage

### Test the System

**Quick Test (using docker-compose):**
```bash
# Run all tests
docker-compose run --rm test
```

**Manual Testing:**

Once running, you can interact with the Controller API from inside containers:

```bash
# Health check (from inside controller)
docker exec controller python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000/health').read().decode())"

# Custom query
docker exec controller python -c "
import urllib.request, json
req = urllib.request.Request(
    'http://localhost:5000/query',
    data=json.dumps({'query': 'Summarize my latest email'}).encode(),
    headers={'Content-Type': 'application/json'}
)
print(json.loads(urllib.request.urlopen(req).read().decode()))
"
```

### Example Response

```json
{
  "status": "success",
  "llm_response": "ACTION: fetch_latest_emails(1)\nACTION: quarantined_llm('Summarize this email: $VAR1')\nACTION: display('Your latest email summary: $VAR2')",
  "actions": [
    {"type": "info", "message": "Fetched 1 email(s) and stored in $VAR1"},
    {"type": "info", "message": "Quarantined LLM completed. Result stored in $VAR2"},
    {"type": "display", "message": "Your latest email summary: ..."}
  ],
  "display": "Your latest email summary: ..."
}
```

## Architecture Details

### Service Communication

- **Controller → Privileged LLM**: HTTP POST `/process` with user query
- **Controller → Quarantined LLM**: HTTP POST `/process` with untrusted content
- **External → Controller**: HTTP POST `/query` with user queries

### Data Flow Example

```
1. User: "Summarize my latest email"
   └─> Controller receives request

2. Controller → Privileged LLM (planning)
   └─> Privileged LLM responds: "ACTION: fetch_latest_emails(1)"

3. Controller executes fetch_latest_emails(1)
   ├─> Calls Privileged LLM's email API
   ├─> Receives email data
   └─> Stores email in $VAR1 (Privileged LLM planning never sees content!)

4. Privileged LLM: "ACTION: quarantined_llm('Summarize: $VAR1')"
   └─> Controller substitutes $VAR1 with actual email content

5. Controller → Quarantined LLM (with real email content)
   └─> Quarantined LLM processes and returns summary

6. Controller stores summary in $VAR2 (tainted!)

7. Privileged LLM: "ACTION: display('Summary: $VAR2')"
   └─> Controller substitutes $VAR2 and displays to user
```

### Key Security Principle

**The Privileged LLM NEVER sees untrusted content!**

- Email content → stored as $VAR1
- Quarantined LLM output → stored as $VAR2
- Privileged LLM only sees variable names: "$VAR1", "$VAR2"
- Controller handles all variable substitution

## Development

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f controller
docker-compose logs -f privileged
docker-compose logs -f quarantined
```

### Stop Services

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up --build
```

### Resource Usage

```bash
docker stats
```

## Configuration

### Resource Limits (docker-compose.yml)

Optimized for Apple M2 Max with 64GB RAM:

- **Quarantined LLM**: 2 CPU cores, 4GB RAM
- **Privileged LLM**: 2 CPU cores, 4GB RAM  
- **Controller**: 2 CPU cores, 2GB RAM

### Model Selection

Default: `gpt-4o-mini` (fast and cost-effective)

To use a different model, edit `docker-compose.yml` and change `OPENAI_MODEL` value in the environment sections.

## Email Data

Place your email CSV file as `privileged/mock_emails.csv`. The system expects the following CSV format:

```csv
id,from,to,subject,body,date,category,risk_level
1,sender@example.com,you@example.com,Subject,Body text,2026-02-05T10:30:00Z,legitimate,safe
```

The included test data (`privileged/mock_emails.csv`) contains 30 sample emails including:
- ✅ Legitimate emails
- ⚠️ Phishing attempts
- 🚨 Prompt injection attacks
- 🔴 Data exfiltration attempts
- 🎭 Social engineering
- 💀 Advanced multi-vector attacks

Perfect for testing the security of the dual LLM pattern!

## Troubleshooting

### Container won't start
```bash
# Check if OPENAI_API_KEY is exported
echo $OPENAI_API_KEY

# Verify Docker Compose can see it
docker-compose config
```

### Connection refused
```bash
# Wait for services to be healthy
docker-compose ps

# Check health endpoints
curl http://localhost:5000/health
```

### Out of memory
Reduce resource limits in `docker-compose.yml`

## Security Considerations

### What This Protects Against

✅ **Prompt Injection**: Quarantined LLM can be compromised, but can't affect Privileged LLM  
✅ **Data Exfiltration**: No outbound URLs generated with untrusted data  
✅ **Command Execution**: Quarantined LLM has no tool access  
✅ **Cross-contamination**: Variable isolation prevents tainted data leaking

### Network Isolation

- Quarantined LLM: Cannot be accessed from host
- Privileged LLM: Cannot be accessed from host
- Controller: Only service exposed (port 5050, mapped from internal 5000)

## License

MIT

## Based On

Simon Willison's Dual LLM Pattern:  
https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
