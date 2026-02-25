# 🚀 Simplest Way to Run

Just two commands. That's it.

## Step 1: Set your OpenAI key
```bash
export OPENAI_API_KEY=sk-your-key-here
```

## Step 2: Start everything
```bash
docker compose up -d
```

**Done!** 🎉

---

## What Just Happened?

Docker Compose automatically:
- ✅ Started PostgreSQL with secure defaults
- ✅ Started Redis with secure defaults
- ✅ Started LiteLLM proxy
- ✅ Configured 4 GPT-5 models
- ✅ Set up all security features

---

## Access Your Proxy

**Proxy API**: http://localhost:4000

**Admin UI**: http://localhost:4000/ui
- Default master key: `sk-1234567890abcdef`
- Change this in production! (see below)

**Health Check**:
```bash
curl http://localhost:4000/health
```

---

## Quick Test

**Using Docker Compose (easiest):**
```bash
docker compose run --rm test
```

This automatically:
- Reads your master key from `.env`
- Waits for the proxy to be ready
- Creates a virtual key
- Makes a test request
- Shows you the results

**Manual test:**
```bash
curl http://localhost:4000/health
```

---

## ⚙️ Customization (Optional)

### For Development/Testing
The defaults work fine. Just use `docker compose up -d`

### For Production
Create a `.env` file with secure keys:

```bash
# Copy the example
cp .env.example .env

# Generate secure keys
echo "LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)" >> .env
echo "LITELLM_SALT_KEY=$(openssl rand -base64 32)" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env

# Start with custom config
docker compose up -d
```

---

## 🔒 Security Note

**Default master key**: `sk-1234567890abcdef`
- ⚠️ This is **only for testing**
- ⚠️ Change it for production
- ⚠️ Anyone with this key has full admin access

**For production**, set secure keys:
```bash
export LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
export LITELLM_SALT_KEY=$(openssl rand -base64 32)
export OPENAI_API_KEY=sk-your-key
docker compose up -d
```

---

## 📊 What Models Are Available?

Pre-configured and ready to use:
- `gpt-5.2` - Best for complex tasks
- `gpt-5-mini` - Fast and efficient  
- `gpt-5-nano` - Fastest and cheapest
- `gpt-4.1` - Non-reasoning tasks

See [MODELS.md](MODELS.md) for details.

---

## 🛠️ Common Commands

```bash
# View logs
docker compose logs -f

# Stop everything
docker compose down

# Restart after config changes
docker compose restart

# Check status
docker compose ps

# Stop and remove all data
docker compose down -v
```

---

## 📚 More Info

- [Full README](README.md) - Complete documentation
- [Security Features](SECURITY_FEATURES_SUMMARY.md) - All 57 security features
- [Models Guide](MODELS.md) - Detailed model information
- [Quick Start](QUICKSTART.md) - Detailed setup guide

---

## 🆘 Troubleshooting

### "Please set OPENAI_API_KEY"
```bash
# Make sure you exported it in your current terminal
export OPENAI_API_KEY=sk-your-key
docker compose up -d
```

### Can't access proxy
```bash
# Wait a bit longer (first start takes ~30 seconds)
sleep 10
curl http://localhost:4000/health

# Check logs
docker compose logs litellm
```

### Port 4000 busy
```bash
# Use a different port
export LITELLM_PORT=4001
docker compose up -d
```

---

**That's it! Just `export OPENAI_API_KEY=sk-... && docker compose up -d`** 🚀
