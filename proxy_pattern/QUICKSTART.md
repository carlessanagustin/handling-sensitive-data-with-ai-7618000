# Quick Start Guide - Pure Docker Compose

Get your secure LiteLLM proxy running in 2 simple steps.

## 🚀 Step 1: Set Your Key

```bash
export OPENAI_API_KEY=sk-your-key-here
```

## 🚀 Step 2: Start Everything

```bash
docker compose up -d
```

This will:
- Start PostgreSQL with secure defaults
- Start Redis with secure defaults
- Start LiteLLM proxy with GPT-5 models
- Apply all 57 security features

## ✅ Step 3: Test It (Optional)

Models are already configured! Just test:

```bash
# Get default master key
curl http://localhost:4000/health

# Create virtual key
curl -X POST http://localhost:4000/key/generate \
  -H 'Authorization: Bearer sk-1234567890abcdef' \
  -H 'Content-Type: application/json' \
  -d '{"max_budget": 10}'
```

## 🔧 Customize Models (Optional)

Already configured with GPT-5 models, but you can add more.

Edit `litellm_config.yaml`:

```yaml
model_list:
  # Current OpenAI Models (2026)
  - model_name: gpt-5.2
    litellm_params:
      model: openai/gpt-5.2
      api_key: os.environ/OPENAI_API_KEY

  - model_name: gpt-5-mini
    litellm_params:
      model: openai/gpt-5-mini
      api_key: os.environ/OPENAI_API_KEY

  # For Azure OpenAI (if needed)
  - model_name: gpt-4o-azure
    litellm_params:
      model: azure/your-deployment
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
```

Restart the proxy:

```bash
docker compose restart litellm
```

## 🧪 Make Your First Request

### Default master key (for testing):

```bash
sk-1234567890abcdef
```

⚠️ **Change this for production!** Set `LITELLM_MASTER_KEY` environment variable.

### Create a virtual key:

```bash
# Use the master key from above
VIRTUAL_KEY=$(curl -s -X POST 'http://localhost:4000/key/generate' \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "rpm_limit": 100,
    "max_budget": 10.0,
    "duration": "30d"
  }' | grep -o '"key":"[^"]*' | cut -d'"' -f4)

echo "Virtual key: $VIRTUAL_KEY"
```

### Make a test request:

```bash
# Use the virtual key from above
curl -X POST 'http://localhost:4000/chat/completions' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $VIRTUAL_KEY" \
  -d '{
    "model": "gpt-5-nano",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## 📊 Access Admin UI

Open in your browser: http://localhost:4000/ui

Login with: `sk-1234567890abcdef` (or your custom master key)

## 🛠️ Common Commands

```bash
# View logs
docker compose logs -f

# Check health
curl http://localhost:4000/health

# Stop services
docker compose down

# Start services
docker compose up -d

# Restart after config changes
docker compose restart litellm

# View service status
docker compose ps
```

## 📚 Next Steps

1. ✅ Read [README.md](README.md) for full documentation
2. ✅ Review [SECURITY_FEATURES.md](SECURITY_FEATURES.md) for security details
3. ✅ Set up monitoring and alerts
4. ✅ Configure SSL/HTTPS for production
5. ✅ Set up regular backups

## 🆘 Troubleshooting

### Services won't start

```bash
# Check what's wrong
docker compose logs

# Try rebuilding
docker compose down
docker compose up -d
```

### Can't connect to proxy

```bash
# Check if it's running
docker compose ps

# Check health
curl http://localhost:4000/health

# Wait a bit longer - it may still be starting
sleep 10
curl http://localhost:4000/health
```

### Database connection errors

```bash
# Check database is healthy
docker compose exec postgres pg_isready

# Check logs
docker compose logs postgres

# Restart everything
docker compose restart
```

## 🔐 Security Reminder

- ✅ Never commit `.env` to git
- ✅ Store your master key securely
- ✅ Don't change `LITELLM_SALT_KEY` after first use
- ✅ Use strong, unique passwords for all services
- ✅ Enable HTTPS in production

## 💡 Pro Tips

1. **Use the Admin UI** - Easier than CLI for key management
2. **Set budgets** - Prevent surprise bills
3. **Enable caching** - Save money on repeated requests
4. **Monitor metrics** - http://localhost:4000/metrics
5. **Regular backups** - Run `bash scripts/backup.sh` weekly

---

Need help? Check the [README.md](README.md) or [LiteLLM docs](https://docs.litellm.ai/)
