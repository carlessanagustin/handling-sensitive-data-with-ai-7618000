# 🐳 Docker Compose Guide

Complete guide to using this proxy with Docker Compose.

## 📋 Table of Contents

1. [Environment Variables (.env file)](#environment-variables)
2. [Starting Services](#starting-services)
3. [Testing](#testing)
4. [Monitoring](#monitoring)
5. [Managing Services](#managing-services)
6. [Advanced Usage](#advanced-usage)

---

## Environment Variables

Docker Compose **automatically loads** the `.env` file from the project directory.

### Quick Setup

**For Development:**
```bash
# Create .env with just your OpenAI key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**For Production:**
```bash
# Generate all secure keys
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF
```

### Default Values

If you don't set these, Docker Compose uses secure defaults:

| Variable | Default | Can Override? |
|----------|---------|---------------|
| `OPENAI_API_KEY` | ❌ Required | N/A |
| `LITELLM_MASTER_KEY` | `sk-1234567890abcdef` | ✅ Yes |
| `LITELLM_SALT_KEY` | `default-salt-key...` | ✅ Yes |
| `POSTGRES_PASSWORD` | Auto-generated | ✅ Yes |
| `REDIS_PASSWORD` | Auto-generated | ✅ Yes |

---

## Starting Services

### Basic Start

```bash
# Start all services in background
docker compose up -d

# View logs
docker compose logs -f
```

### Start with Specific .env File

```bash
# Use a different env file
docker compose --env-file .env.production up -d
```

### Start Specific Services

```bash
# Start only database
docker compose up -d postgres

# Start database and cache
docker compose up -d postgres redis

# Start everything
docker compose up -d
```

### View Startup Logs

```bash
# Show logs for all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Show last 100 lines
docker compose logs --tail=100

# Logs for specific service
docker compose logs litellm
```

---

## Testing

### Run Tests (Pure Docker Compose)

```bash
# Run complete test suite
docker compose run --rm test
```

This automatically:
- Waits for services to be healthy
- Reads `LITELLM_MASTER_KEY` from `.env`
- Creates a virtual key
- Makes a test request
- Shows results

### Test Individual Components

```bash
# Check health
docker compose exec litellm curl -s http://localhost:4000/health

# Check database
docker compose exec postgres pg_isready

# Check Redis
docker compose exec redis redis-cli ping
```

---

## Monitoring

### Service Status

```bash
# Show all running services
docker compose ps

# Show resource usage
docker compose stats

# Show detailed service info
docker compose ps -a
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f litellm
docker compose logs -f postgres
docker compose logs -f redis

# With timestamps
docker compose logs -f -t litellm

# Last N lines
docker compose logs --tail=50 litellm
```

### Health Checks

```bash
# Check proxy health
curl http://localhost:4000/health

# Check metrics
curl http://localhost:4000/metrics

# Inside containers
docker compose exec litellm wget -qO- http://localhost:4000/health
docker compose exec postgres pg_isready
docker compose exec redis redis-cli ping
```

---

## Managing Services

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart litellm

# Restart after config changes
docker compose restart litellm
```

### Stop Services

```bash
# Stop all services (keeps data)
docker compose stop

# Stop specific service
docker compose stop litellm

# Stop and remove containers (keeps data)
docker compose down

# Stop and remove everything including data (⚠️ destructive)
docker compose down -v
```

### Update Services

```bash
# Pull latest images
docker compose pull

# Recreate services with new images
docker compose up -d --force-recreate

# Rebuild if using custom Dockerfile
docker compose build
docker compose up -d
```

### Scale Services

```bash
# Run multiple proxy instances (requires load balancer)
docker compose up -d --scale litellm=3
```

---

## Advanced Usage

### Using Profiles

The test service uses a profile to keep it separate:

```bash
# Start main services (without test)
docker compose up -d

# Run test service (on-demand)
docker compose run --rm test

# Or include test profile
docker compose --profile tools up -d
```

### Override Configuration

Create `docker-compose.override.yml`:

```yaml
services:
  litellm:
    environment:
      LITELLM_LOG: DEBUG
    ports:
      - "4001:4000"  # Use different port
```

Docker Compose automatically merges this with `docker-compose.yml`.

### Multiple Environments

```bash
# Development
docker compose --env-file .env.dev up -d

# Staging  
docker compose --env-file .env.staging up -d

# Production
docker compose --env-file .env.prod up -d
```

### Execute Commands in Containers

```bash
# Shell access
docker compose exec litellm sh
docker compose exec postgres psql -U litellm_user litellm

# One-off commands
docker compose exec litellm env
docker compose exec postgres pg_dump -U litellm_user litellm
```

### Backup & Restore

```bash
# Backup database
docker compose exec postgres pg_dump -U litellm_user litellm | gzip > backup.sql.gz

# Restore database
gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U litellm_user litellm

# Backup Redis
docker compose exec redis redis-cli SAVE
docker compose cp redis:/data/dump.rdb ./redis-backup.rdb

# Backup volumes
docker run --rm -v proxy_pattern_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .
```

---

## Environment Variable Reference

### Required

```bash
OPENAI_API_KEY=sk-...           # Your OpenAI API key
```

### Security (Optional)

```bash
LITELLM_MASTER_KEY=sk-...       # Admin key (default: sk-1234567890abcdef)
LITELLM_SALT_KEY=...            # Encryption key (default: generated)
POSTGRES_PASSWORD=...           # DB password (default: generated)
REDIS_PASSWORD=...              # Cache password (default: generated)
```

### Server Configuration (Optional)

```bash
LITELLM_PORT=4000               # Proxy port
WORKER_COUNT=4                  # Number of workers
LITELLM_LOG=INFO                # Log level
TZ=UTC                          # Timezone
```

### Security Settings (Optional)

```bash
SSL_VERIFY=true                 # Verify SSL certificates
ALLOWED_ORIGINS=...             # CORS origins
LITELLM_TELEMETRY=False         # Disable telemetry
LITELLM_REQUEST_LOGS=True       # Enable request logs
```

---

## Common Workflows

### Complete Fresh Start

```bash
# Stop everything and remove all data
docker compose down -v

# Create .env
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start fresh
docker compose up -d

# Test
docker compose run --rm test
```

### Quick Restart After Config Change

```bash
# Edit config
nano litellm_config.yaml

# Restart just the proxy
docker compose restart litellm

# Check logs
docker compose logs -f litellm
```

### Production Deployment

```bash
# Generate secure keys
cat > .env << EOF
OPENAI_API_KEY=sk-your-key
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 32)
LITELLM_SALT_KEY=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF

# Start services
docker compose up -d

# Verify health
docker compose ps
curl http://localhost:4000/health

# Run tests
docker compose run --rm test

# Setup backups (cron job)
echo "0 2 * * * docker compose -f /path/to/docker-compose.yml exec postgres pg_dump -U litellm_user litellm | gzip > /backups/litellm-\$(date +\%Y\%m\%d).sql.gz" | crontab -
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs litellm

# Restart everything
docker compose down
docker compose up -d
```

### Can't Connect to Proxy

```bash
# Check if running
docker compose ps

# Check health
docker compose exec litellm curl http://localhost:4000/health

# Check logs
docker compose logs litellm
```

### Database Connection Issues

```bash
# Check database is ready
docker compose exec postgres pg_isready

# Check connection string
docker compose exec litellm env | grep DATABASE_URL

# Restart database
docker compose restart postgres
```

### Out of Memory/Resources

```bash
# Check resource usage
docker compose stats

# Reduce worker count
echo "WORKER_COUNT=2" >> .env
docker compose restart litellm
```

---

## Best Practices

1. **Always use .env file** - Don't expose secrets in command line
2. **Use profiles** - Keep optional services separate
3. **Regular backups** - Backup database and volumes
4. **Monitor logs** - Use `docker compose logs -f`
5. **Health checks** - Verify services after changes
6. **Version control** - Commit `docker-compose.yml`, not `.env`
7. **Resource limits** - Set appropriate CPU/memory limits
8. **Network isolation** - Use custom networks
9. **Update regularly** - Pull latest images

---

## Quick Reference

```bash
# Start
docker compose up -d

# Test  
docker compose run --rm test

# Logs
docker compose logs -f

# Status
docker compose ps

# Restart
docker compose restart litellm

# Stop
docker compose down

# Health
curl http://localhost:4000/health

# Shell
docker compose exec litellm sh
```

---

For more information, see:
- [START_HERE.md](START_HERE.md) - Quick setup
- [COMMANDS.md](COMMANDS.md) - All commands
- [README.md](README.md) - Full documentation
