# Usage

## 1. Build images

```bash
docker compose build
```

## 2. Configure provider

Copy `.env.example` to `.env` and fill in your provider and API key:

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
PROVIDER=mistral          # claude | ollama | mistral
MISTRAL_API_KEY=<your-key>
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
