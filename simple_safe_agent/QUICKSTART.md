# Usage

## 1. Build images

```bash
docker compose build
```

## 2. Select provider and set environment variables

```bash
# Claude (default)
export PROVIDER=claude
export ANTHROPIC_API_KEY=sk-ant-...

# Ollama (requires local Ollama with llama3.2 pulled)
export PROVIDER=ollama
export OLLAMA_BASE_URL=http://ollama:11434

# Mistral
export PROVIDER=mistral
export MISTRAL_API_KEY=<your-key>
```

## 3. Start with Docker Compose

```bash
docker compose up -d
docker compose logs -f
```

## 4. Test It

```bash
docker compose run --rm test
```

## 5. Stop It

```bash
docker compose down --rmi all
```
