# LiteLLM Proxy - Security Hardened Setup

A production-ready, security-hardened LiteLLM proxy configuration optimized for Apple M2 Max (arm64) with 64GB RAM.

## ⚡ Quick Start (3 Commands)

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker compose up -d
docker compose run --rm test
```

**Done!** See [COMPLETE_WORKFLOW.md](COMPLETE_WORKFLOW.md) for the full workflow or [START_HERE.md](START_HERE.md) for quick start.

## 🔒 Security Features

This setup implements 57 security features for maximal data safety. See [SECURITY_FEATURES_SUMMARY.md](SECURITY_FEATURES_SUMMARY.md) for the complete list.

## 📋 Prerequisites

- Docker Desktop for Mac (Apple Silicon version)
- At least 16GB RAM available for Docker
- Basic understanding of Docker and environment variables

## 🚀 Quick Start

### Super Simple (2 Commands)

```bash
# Set your OpenAI key
export OPENAI_API_KEY=sk-your-key-here

# Start everything
docker compose up -d
```

**That's it!** See [RUN_SIMPLE.md](RUN_SIMPLE.md) for details.

### For Production (Secure Keys)

```bash
# Set your keys
export OPENAI_API_KEY=sk-your-key-here
export LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
export LITELLM_SALT_KEY=$(openssl rand -base64 32)

# Start
docker compose up -d
```

### 2. Configure Models

Edit `litellm_config.yaml` and uncomment/configure your LLM providers:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/your-deployment
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
```

### 3. Start the Proxy

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check health status
curl http://localhost:4000/health
```

### 4. Create Your First API Key

```bash
# Create a virtual key with rate limits
curl -X POST 'http://localhost:4000/key/generate' \
  -H 'Authorization: Bearer YOUR_MASTER_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "rpm_limit": 100,
    "tpm_limit": 100000,
    "max_budget": 10.0,
    "duration": "30d"
  }'
```

### 5. Test the Proxy

```bash
# Make a test request
curl -X POST 'http://localhost:4000/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_VIRTUAL_KEY' \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Client App    │
└────────┬────────┘
         │ HTTPS (with virtual key)
         ▼
┌─────────────────┐
│  LiteLLM Proxy  │ ◄── Rate limiting, authentication, caching
│   (Port 4000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌──────┐ ┌──────┐  ┌────────────┐
│ DB   │ │Redis │  │ OpenAI     │
│(PG)  │ │Cache │  │ GPT-5.2    │
└──────┘ └──────┘  │ 2026 Models│
                   └────────────┘
```

## 🤖 Pre-configured Models

**Latest OpenAI GPT-5 Series (2026)**:
- `gpt-5.2` - Flagship model for coding & agents
- `gpt-5-mini` - Fast & cost-efficient
- `gpt-5-nano` - Fastest & cheapest
- `gpt-4.1` - Non-reasoning alternative

See [MODELS.md](MODELS.md) for detailed model information.

## 📊 Admin UI

Access the admin UI at: `http://localhost:4000/ui`

Use your `LITELLM_MASTER_KEY` to log in.

## 🔧 Configuration

### Environment Variables

All sensitive configuration is stored in `.env`:

| Variable | Purpose | Required |
|----------|---------|----------|
| `LITELLM_MASTER_KEY` | Admin API key | ✅ |
| `LITELLM_SALT_KEY` | Encryption salt | ✅ |
| `POSTGRES_PASSWORD` | Database password | ✅ |
| `REDIS_PASSWORD` | Cache password | ✅ |
| Provider API keys | LLM provider access | ⚠️  |

### Model Configuration

Models are configured in `litellm_config.yaml`. The proxy supports:

- OpenAI
- Anthropic (Claude)
- Azure OpenAI
- AWS Bedrock
- Google Vertex AI
- Cohere
- Hugging Face
- And many more...

See [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers)

## 🛡️ Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore` by default
2. **Rotate keys regularly** - Update `LITELLM_MASTER_KEY` periodically
3. **Use strong passwords** - All passwords should be 32+ characters
4. **Enable SSL in production** - Use reverse proxy (nginx/Caddy) with Let's Encrypt
5. **Monitor logs** - Check `./logs/` directory regularly
6. **Set rate limits** - Prevent abuse with per-key limits
7. **Use IP whitelisting** - Restrict access to known IPs (optional)
8. **Enable audit logs** - Track all API usage in database

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:4000/health
```

### Prometheus Metrics

Metrics available at: `http://localhost:4000/metrics`

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f litellm
docker compose logs -f postgres
docker compose logs -f redis
```

## 🔄 Maintenance

### Backup Database

```bash
# Create backup (no chmod needed)
bash scripts/backup.sh

# Restore backup (no chmod needed)
bash scripts/restore.sh ./backups/litellm_backup_20260209_120000.sql.gz

# OR manually:
docker compose exec postgres pg_dump -U litellm_user litellm | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Update Proxy

```bash
# Pull latest image
docker compose pull

# Restart services
docker compose up -d
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v
```

## 🐛 Troubleshooting

### Connection Errors

```bash
# Check service status
docker compose ps

# Inspect logs
docker compose logs litellm

# Restart services
docker compose restart
```

### Database Issues

```bash
# Check database connection
docker compose exec postgres psql -U litellm_user -d litellm -c "SELECT 1;"

# View database size
docker compose exec postgres psql -U litellm_user -d litellm -c "SELECT pg_database_size('litellm');"
```

### Permission Errors

Logs are now stored in Docker volumes to avoid permission issues. View them with:

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f litellm

# View last 100 lines
docker compose logs --tail=100 litellm
```

## 📚 Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Proxy API Reference](https://docs.litellm.ai/docs/proxy/all_endpoints)
- [Security Best Practices](SECURITY_FEATURES.md)
- [Provider Configuration](https://docs.litellm.ai/docs/providers)

## 🤝 Support

For issues or questions:

1. Check the [Troubleshooting section](#-troubleshooting)
2. Review [LiteLLM Issues](https://github.com/BerriAI/litellm/issues)
3. Join [LiteLLM Discord](https://discord.gg/wuPM9dRgDw)

## 📄 License

This configuration is provided as-is for use with LiteLLM. See LiteLLM's license for proxy usage terms.

## ⚠️ Important Security Notes

- **NEVER** commit your `.env` file
- **NEVER** share your `LITELLM_MASTER_KEY`
- **NEVER** change `LITELLM_SALT_KEY` after initial setup
- **ALWAYS** use HTTPS in production
- **ALWAYS** keep Docker images updated
- **ALWAYS** monitor your API usage and costs
