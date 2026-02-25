# 🚀 Quick Start Guide

Get your secure LiteLLM proxy running in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- Terminal access

## Setup Steps

### 1. Generate Secure Keys (30 seconds)

```bash
cd proxy_pattern
./scripts/generate_keys.sh
```

This generates all required security keys automatically.

### 2. Add Your API Keys (2 minutes)

Edit `.env` file and add your LLM provider API keys:

```bash
nano .env
```

Add your keys (uncomment and fill in):

```bash
# Example: For OpenAI
OPENAI_API_KEY=sk-your-actual-key-here

# Example: For Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Configure Models (1 minute)

Edit `litellm_config.yaml` and uncomment the models you want to use:

```bash
nano litellm_config.yaml
```

Example configuration:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      timeout: 60
```

### 4. Start the Proxy (1 minute)

```bash
docker compose up -d
```

Wait for services to be healthy:

```bash
./scripts/health_check.sh
```

### 5. Create Your First Key (30 seconds)

```bash
# Replace YOUR_MASTER_KEY with the one from your .env file
curl -X POST 'http://localhost:4000/key/generate' \
  -H 'Authorization: Bearer YOUR_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "rpm_limit": 100,
    "max_budget": 10.0,
    "duration": "30d"
  }'
```

Save the returned key - this is your virtual API key!

### 6. Test It! (30 seconds)

```bash
# Replace YOUR_VIRTUAL_KEY with the key from step 5
curl -X POST 'http://localhost:4000/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_VIRTUAL_KEY' \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Hello! This is a test."}
    ]
  }'
```

## 🎉 Success!

Your secure proxy is now running at `http://localhost:4000`

Access the Admin UI at: `http://localhost:4000/ui`

## Common Commands

```bash
# Check health status
./scripts/health_check.sh

# View logs
docker compose logs -f

# Stop proxy
docker compose down

# Backup database
./scripts/backup.sh

# Restart after configuration changes
docker compose restart
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Review [SECURITY_FEATURES.md](SECURITY_FEATURES.md) to understand security
- Set up SSL/HTTPS for production use
- Configure monitoring and alerting
- Set up automated backups

## Need Help?

- Check logs: `docker compose logs -f litellm`
- Verify services: `docker compose ps`
- Run health check: `./scripts/health_check.sh`

## Common Issues

**Port already in use?**
```bash
# Change port in .env
LITELLM_PORT=4001
docker compose up -d
```

**Permission denied on scripts?**
```bash
chmod +x scripts/*.sh
```

**Services won't start?**
```bash
# Check Docker is running
docker ps

# View specific service logs
docker compose logs postgres
docker compose logs redis
docker compose logs litellm
```
