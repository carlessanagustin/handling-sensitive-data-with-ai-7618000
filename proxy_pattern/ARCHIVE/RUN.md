# 🚀 How to Run - Super Simple

## One-Command Setup

```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env && docker compose up -d
```

## Step by Step

### 1. Create .env file
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 2. Start with Docker Compose
```bash
docker compose up -d
```

**That's it!** 🎉

Docker Compose automatically reads `.env` file.

---

## What Models Are Available?

Pre-configured OpenAI models (2026 - ready to use):
- ✅ `gpt-5.2` - Best model for coding & agentic tasks
- ✅ `gpt-5-mini` - Fast & cost-efficient version
- ✅ `gpt-5-nano` - Fastest & most cost-efficient
- ✅ `gpt-4.1` - Smartest non-reasoning model

**Note**: GPT-4o and earlier models are being phased out in favor of GPT-5 series.

---

## Quick Test

**Pure Docker Compose (easiest):**
```bash
docker compose run --rm test
```

This automatically reads `.env` and runs complete tests!

**Or manual test:**
```bash
curl http://localhost:4000/health
```

---

## Access Admin UI

Open your browser: **http://localhost:4000/ui**

Login with your master key (find it with):
```bash
grep LITELLM_MASTER_KEY .env
```

---

## Useful Commands

```bash
# Check if it's running
docker compose ps

# View logs
docker compose logs -f

# Check health
curl http://localhost:4000/health

# Stop everything
docker compose down

# Start again
docker compose up -d

# Restart after changes
docker compose restart litellm
```

---

## Troubleshooting

### "OPENAI_API_KEY not found"
```bash
# Make sure you exported it in the same terminal session
export OPENAI_API_KEY=sk-your-key
# Then run setup again
bash setup.sh
```

### "Port 4000 already in use"
```bash
# Edit .env and change the port
nano .env
# Change: LITELLM_PORT=4001
docker compose up -d
```

### "Can't connect to proxy"
```bash
# Wait a bit longer (first start takes ~30 seconds)
sleep 10
curl http://localhost:4000/health

# Check logs
docker compose logs litellm
```

### "Docker command not found"
```bash
# Make sure Docker Desktop is running
open -a Docker
# Wait for it to start, then try again
```

---

## What Happens During Setup?

1. ✅ Checks for your OPENAI_API_KEY
2. ✅ Creates secure `.env` file with random passwords
3. ✅ Generates master key and salt key
4. ✅ Starts PostgreSQL database (encrypted)
5. ✅ Starts Redis cache (password-protected)
6. ✅ Starts LiteLLM proxy with security hardening
7. ✅ Configures 4 OpenAI models automatically
8. ✅ Runs health checks

---

## Clean Start (if needed)

```bash
# Stop and remove everything (including data)
docker compose down -v

# Run setup again
bash setup.sh
```

---

## Next Steps

- ✅ **Test the API** - See "Quick Test" above
- ✅ **Use the Admin UI** - http://localhost:4000/ui
- ✅ **Read the docs** - See README.md
- ✅ **Check security** - See SECURITY_FEATURES_SUMMARY.md
- ✅ **Set up backups** - Run `bash scripts/backup.sh`

---

## Support

Need help? Check:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Detailed quick start
- [SECURITY_FEATURES.md](SECURITY_FEATURES.md) - Security details
- [LiteLLM Docs](https://docs.litellm.ai/)

---

**Remember**: Your master key is auto-generated and saved in `.env`. Keep it safe! 🔐
