# 📋 Quick Command Reference

Copy-paste commands for common tasks. All commands use Docker Compose and automatically read from `.env` file.

## 🚀 Setup & Start

```bash
# Create .env file (Docker Compose automatically loads it!)
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start all services
docker compose up -d
```

## 🧪 Testing

### Quick Test (Pure Docker Compose)
```bash
# Run complete test suite
docker compose run --rm test
```

This automatically:
- Reads master key from `.env`
- Waits for services to be ready
- Creates a virtual key
- Makes a test request
- Shows results

### Manual Health Check
```bash
curl http://localhost:4000/health
```

### Get Master Key from .env
```bash
# View your master key
grep LITELLM_MASTER_KEY .env

# Or use in a command
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef")
echo $MASTER_KEY
```

### Create Virtual Key
```bash
# Get master key first
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef")

# Create virtual key
VIRTUAL_KEY=$(curl -s -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"max_budget": 10}' | grep -o '"key":"[^"]*' | cut -d'"' -f4)

echo "Virtual key: $VIRTUAL_KEY"
```

### Make Test Request
```bash
# Use virtual key from above
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer $VIRTUAL_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "gpt-5-nano",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Complete Test (all-in-one)
```bash
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef") && \
VIRTUAL_KEY=$(curl -s -X POST http://localhost:4000/key/generate -H "Authorization: Bearer $MASTER_KEY" -H 'Content-Type: application/json' -d '{"max_budget":10}' | grep -o '"key":"[^"]*' | cut -d'"' -f4) && \
echo "Virtual key: $VIRTUAL_KEY" && \
curl -X POST http://localhost:4000/chat/completions -H "Authorization: Bearer $VIRTUAL_KEY" -H 'Content-Type: application/json' -d '{"model":"gpt-5-nano","messages":[{"role":"user","content":"Hello!"}]}'
```

## 🔍 Monitoring

### Check Health
```bash
curl http://localhost:4000/health
```

### View Logs
```bash
# All services
docker compose logs -f

# Just proxy
docker compose logs -f litellm

# Last 100 lines
docker compose logs --tail=100 litellm
```

### Check Status
```bash
docker compose ps
```

### View Metrics
```bash
curl http://localhost:4000/metrics
```

## 🛠️ Management

### Restart Services
```bash
# Restart all
docker compose restart

# Restart proxy only
docker compose restart litellm

# Restart after config changes
docker compose restart litellm
```

### Stop/Start
```bash
# Stop everything
docker compose down

# Start everything
docker compose up -d

# Stop and remove all data (⚠️ destructive)
docker compose down -v
```

### Access Admin UI
```bash
# Get your master key
grep LITELLM_MASTER_KEY .env 2>/dev/null || echo "sk-1234567890abcdef"

# Open http://localhost:4000/ui in browser
# Login with master key
```

## 🔑 Key Management

### List Keys (via API)
```bash
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef")

curl -X GET http://localhost:4000/key/info \
  -H "Authorization: Bearer $MASTER_KEY"
```

### Delete a Key
```bash
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef")

curl -X POST http://localhost:4000/key/delete \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"key": "KEY_TO_DELETE"}'
```

### Create Key with Limits
```bash
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "sk-1234567890abcdef")

curl -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "rpm_limit": 100,
    "tpm_limit": 100000,
    "max_budget": 10.0,
    "duration": "30d"
  }'
```

## 💾 Backup

### Create Backup
```bash
# Using script (recommended)
bash scripts/backup.sh

# Manual
docker compose exec postgres pg_dump -U litellm_user litellm | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Backup
```bash
# Using script (recommended)
bash scripts/restore.sh ./backups/backup_file.sql.gz

# Manual
gunzip -c backup_file.sql.gz | docker compose exec -T postgres psql -U litellm_user litellm
```

## 🔒 Production Setup

### Generate Secure Keys (Docker Compose automatically uses .env!)
```bash
# Generate all keys and save to .env
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF

# Start with secure keys (no exports needed!)
docker compose up -d

# Test
docker compose run --rm test
```

### View Your Master Key
```bash
grep LITELLM_MASTER_KEY .env | cut -d'=' -f2
```

## 🐛 Troubleshooting

### Check All Services
```bash
docker compose ps
```

### Check Individual Service Health
```bash
# PostgreSQL
docker compose exec postgres pg_isready

# Redis
docker compose exec redis redis-cli ping

# Proxy
curl http://localhost:4000/health
```

### View Database Size
```bash
docker compose exec postgres psql -U litellm_user -d litellm -c "SELECT pg_database_size('litellm');"
```

### Clear Cache
```bash
docker compose exec redis redis-cli FLUSHALL
```

### Rebuild Everything
```bash
docker compose down -v
docker compose up -d
```

## 📚 More Info

- [START_HERE.md](START_HERE.md) - Simplest setup guide
- [README.md](README.md) - Complete documentation
- [MODELS.md](MODELS.md) - Available models
- [test.sh](test.sh) - Automated test script
