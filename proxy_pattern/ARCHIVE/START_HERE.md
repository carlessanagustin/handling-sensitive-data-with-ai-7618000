# ⚡ START HERE - Simplest Setup Ever

## 🚀 Two Commands. That's All.

**Option 1 - Using environment variable:**
```bash
export OPENAI_API_KEY=sk-your-key-here
docker compose up -d
```

**Option 2 - Using .env file (recommended):**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
docker compose up -d
```

**DONE!** Your secure proxy is running at http://localhost:4000

> Docker Compose automatically loads `.env` file - no need to export!

---

## ✅ What You Get

- ✅ **4 GPT-5 models** ready to use (latest 2026 models)
- ✅ **57 security features** enabled automatically
- ✅ **PostgreSQL database** with encryption
- ✅ **Redis caching** for speed
- ✅ **Rate limiting** and budget controls
- ✅ **Admin UI** at http://localhost:4000/ui

---

## 🧪 Test It Now

**Using Docker Compose (recommended):**
```bash
docker compose run --rm test
```

This automatically:
- ✅ Reads master key from `.env` 
- ✅ Waits for proxy to be healthy
- ✅ Creates a virtual key
- ✅ Makes a test request
- ✅ Shows you the virtual key to use

**Using curl (if you prefer):**
```bash
curl http://localhost:4000/health
```

---

## 🔒 For Production

Create `.env` file with secure keys:

```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF

docker compose up -d
```

Docker Compose automatically uses `.env` file!

---

## 📚 Learn More

- [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Complete Docker Compose guide
- [COMMANDS.md](COMMANDS.md) - Copy-paste commands for everything
- [MODELS.md](MODELS.md) - Available models (GPT-5 series)
- [SECURITY_FEATURES_SUMMARY.md](SECURITY_FEATURES_SUMMARY.md) - All 57 security features
- [README.md](README.md) - Complete documentation

---

## 🤔 Why Is This So Simple?

Docker Compose handles everything:
- Auto-configures secure defaults
- Manages all dependencies
- Sets up networking
- Applies security hardening
- No scripts needed!

---

**That's literally it. Just export your key and run `docker compose up -d`** 🎉
