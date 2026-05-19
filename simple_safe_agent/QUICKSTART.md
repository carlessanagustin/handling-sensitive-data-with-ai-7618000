# Quick Start Guide

## Two Commands to Run

### 1. Build images

```bash
docker compose build
```

### 2. Export your OpenAI API key

```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Start with Docker Compose

```bash
docker compose up -d
```

## Test It

```bash
# Run all tests
docker compose run --rm test
```

## Stop It

```bash
docker compose down --rmi all
```

That's it!
