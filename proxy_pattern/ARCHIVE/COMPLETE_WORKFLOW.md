# ✨ Complete Workflow - Pure Docker Compose

The absolute simplest way to run a secure LiteLLM proxy. Everything uses Docker Compose and the `.env` file.

## 🎯 Overview

**No bash scripts. No exports. Just Docker Compose + .env file.**

Docker Compose automatically:
- Loads `.env` file (no need to `export` anything)
- Uses secure defaults for everything
- Manages all services
- Runs tests in containers

---

## 🚀 Quick Start (3 Steps)

### 1. Create `.env` file
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 2. Start everything
```bash
docker compose up -d
```

### 3. Test it
```bash
docker compose run --rm test
```

**Done!** 🎉

---

## 📋 What Just Happened?

### When you ran `docker compose up -d`:

1. **Docker Compose automatically loaded `.env`** - No exports needed!
2. **Started PostgreSQL** with secure defaults
3. **Started Redis** with secure defaults
4. **Started LiteLLM proxy** with:
   - 4 GPT-5 models configured
   - Master key from `.env` (or default: `sk-1234567890abcdef`)
   - 57 security features enabled
   - Encrypted API key storage

### When you ran `docker compose run --rm test`:

1. **Waited for proxy to be healthy**
2. **Read master key from `.env`** automatically
3. **Created a virtual key**
4. **Made a test request** to GPT-5-nano
5. **Showed you the virtual key** to use in your app

---

## 🔧 The `.env` File

Docker Compose automatically loads `.env` from the current directory.

### Minimal `.env` (for development):
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Full `.env` (for production):
```bash
OPENAI_API_KEY=sk-your-key-here
LITELLM_MASTER_KEY=sk-abc123...
LITELLM_SALT_KEY=xyz789...
POSTGRES_PASSWORD=secure_pass
REDIS_PASSWORD=secure_pass
```

**Generate production keys:**
```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF
```

---

## 🧪 Testing Workflow

### Option 1: Docker Compose Test Service (Recommended)
```bash
docker compose run --rm test
```

**What it does:**
- ✅ Reads `LITELLM_MASTER_KEY` from `.env`
- ✅ Waits for services to be healthy
- ✅ Creates a virtual API key
- ✅ Makes a test request
- ✅ Shows results and your new key

### Option 2: Quick Health Check
```bash
curl http://localhost:4000/health
```

### Option 3: Manual Testing
```bash
# Get master key from .env
MASTER_KEY=$(grep LITELLM_MASTER_KEY .env | cut -d'=' -f2)

# Create virtual key using docker exec
docker compose exec litellm curl -s -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $MASTER_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"max_budget": 10}'
```

---

## 🔍 Monitoring with Docker Compose

### View All Services
```bash
docker compose ps
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

### Check Health
```bash
# Via compose exec
docker compose exec litellm curl -s http://localhost:4000/health

# Or from host
curl http://localhost:4000/health
```

### Resource Usage
```bash
docker compose stats
```

---

## 🛠️ Common Operations

### Restart After Config Changes
```bash
# Edit config
nano litellm_config.yaml

# Restart proxy (reads .env automatically)
docker compose restart litellm
```

### Stop Everything
```bash
docker compose down
```

### Start Again
```bash
docker compose up -d
```

### Complete Reset (⚠️ Deletes all data)
```bash
docker compose down -v
docker compose up -d
```

### View Environment Variables
```bash
# See what's loaded from .env
docker compose config

# Or view specific service
docker compose exec litellm env | grep LITELLM
```

---

## 🔑 Key Management via Docker Compose

### Create a Virtual Key
```bash
# Using test service (easiest)
docker compose run --rm test

# Or manually
docker compose exec litellm curl -s -X POST http://localhost:4000/key/generate \
  -H "Authorization: Bearer $(grep LITELLM_MASTER_KEY .env | cut -d'=' -f2)" \
  -H 'Content-Type: application/json' \
  -d '{"max_budget": 10, "rpm_limit": 100}'
```

### List Keys
```bash
docker compose exec litellm curl -s http://localhost:4000/key/info \
  -H "Authorization: Bearer $(grep LITELLM_MASTER_KEY .env | cut -d'=' -f2)"
```

### Access Admin UI
```bash
# Get your master key
grep LITELLM_MASTER_KEY .env

# Open http://localhost:4000/ui in browser
# Login with the master key
```

---

## 💾 Backup & Restore with Docker Compose

### Create Backup
```bash
# Backup database
docker compose exec postgres pg_dump -U litellm_user litellm | gzip > backup_$(date +%Y%m%d).sql.gz

# Backup Redis
docker compose exec redis redis-cli SAVE
```

### Restore Backup
```bash
# Restore database
gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U litellm_user litellm

# Restart services
docker compose restart
```

---

## 🌍 Different Environments

### Development
```bash
# .env.dev
OPENAI_API_KEY=sk-dev-key
LITELLM_MASTER_KEY=sk-1234567890abcdef

# Use it
docker compose --env-file .env.dev up -d
```

### Production
```bash
# .env.prod
OPENAI_API_KEY=sk-prod-key
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Use it
docker compose --env-file .env.prod up -d
```

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check logs
docker compose logs

# Check .env file exists
cat .env

# Verify OPENAI_API_KEY is set
grep OPENAI_API_KEY .env
```

### Test Service Fails
```bash
# Check proxy is running
docker compose ps

# Check proxy health
docker compose exec litellm curl http://localhost:4000/health

# View test logs
docker compose run --rm test 2>&1
```

### Can't Connect
```bash
# Verify port is exposed
docker compose ps | grep litellm

# Check if port 4000 is available
lsof -i :4000

# Try different port in .env
echo "LITELLM_PORT=4001" >> .env
docker compose up -d
```

---

## ✨ Why This Is Better

### Before (complicated):
```bash
# Create .env
# Export variables
# Run bash script
# Wait for setup
# Test manually
```

### Now (simple):
```bash
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d
docker compose run --rm test
```

### Benefits:
- ✅ **No bash scripts** - Pure Docker Compose
- ✅ **No exports** - `.env` loaded automatically
- ✅ **No manual testing** - Built-in test service
- ✅ **Isolated** - Tests run in containers
- ✅ **Reproducible** - Same everywhere
- ✅ **Secure** - Keys only in `.env` file

---

## 📚 Complete Command Reference

```bash
# Setup
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d

# Test
docker compose run --rm test

# Monitor
docker compose logs -f
docker compose ps
docker compose stats

# Manage
docker compose restart
docker compose stop
docker compose down

# Health
curl http://localhost:4000/health
docker compose exec litellm curl http://localhost:4000/health

# Keys
grep LITELLM_MASTER_KEY .env
docker compose config | grep LITELLM

# Backup
docker compose exec postgres pg_dump -U litellm_user litellm | gzip > backup.sql.gz

# Clean restart
docker compose down -v
docker compose up -d
```

---

## 🎓 Learn More

- [START_HERE.md](START_HERE.md) - Quick start guide
- [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Comprehensive Docker Compose guide
- [COMMANDS.md](COMMANDS.md) - All copy-paste commands
- [MODELS.md](MODELS.md) - Available models
- [README.md](README.md) - Full documentation

---

**Summary: Just create `.env`, run `docker compose up -d`, test with `docker compose run --rm test`. That's it!** 🚀
