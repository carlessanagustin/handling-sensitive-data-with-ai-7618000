# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is the companion code for the LinkedIn Learning course *Handling Sensitive Data with Cloud and Local AI* (instructor: Ronnie Sheer). It is a teaching repository: each top-level directory is a **self-contained example** illustrating one pattern for handling sensitive data with AI. The examples do not share code, dependencies, or a build system — treat each directory as its own mini-project.

**The README warns explicitly: this code is for education only and must not be used in production.** Keep that framing when reviewing or extending examples — favor clarity over hardening beyond what the example is teaching.

## Layout of the examples

Each subdir demonstrates a distinct technique. When the user asks about a topic, work inside the matching directory:

- `simple_anonymize/` — PII redaction with Microsoft Presidio (`presidio-analyzer` + `presidio-anonymizer`, spaCy `en_core_web_lg`). `anonymize.py` is the minimal example, `anonymize_v2.py` the expanded one. Plain `pip install -r requirements.txt` then `python anonymize.py`.
- `bedrock_example/` — Single-file demo (`bedrock_mistral.py`) calling AWS Bedrock's Mistral model **through the OpenAI SDK** using `AWS_BEARER_TOKEN_BEDROCK` as a bearer token against the Bedrock OpenAI-compatible endpoint. No requirements file; expects `openai` installed and the env var set.
- `proxy_pattern/` — LiteLLM proxy as a security gateway in front of cloud LLMs. Docker Compose stack (LiteLLM + Postgres + Redis). Configure via `.env` (`OPENAI_API_KEY`, `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`) and `litellm_config.yaml`. Run with `docker compose up -d`; test via `docker compose run --rm test`. Proxy listens on `:4000`, admin UI at `/ui`. The README files (`START_HERE.md`, `QUICKSTART.md`, `COMPLETE_WORKFLOW.md`, `SECURITY_FEATURES.md`) are the source of truth — prefer editing `litellm_config.yaml` over the compose file for model/security changes.
- `simple_safe_agent/` — Reference implementation of the **Dual LLM pattern** as three Docker services:
  - `controller/` (port 5050, only host-exposed) orchestrates the flow and owns variable storage (`$VAR1`, `$VAR2`, …).
  - `privileged/` (internal :5001) has tool access and the mock email store (`mock_emails.csv`) but **must never see untrusted content directly** — it only sees variable names.
  - `quarantined/` (internal :5002) processes untrusted content but has **no tools**.
  The Controller substitutes variables only when dispatching to the Quarantined LLM or to the final display step. Preserving this isolation is the whole point of the example — do not let the Privileged LLM be handed raw email bodies or `$VAR` values resolved into its prompt. Run with `OPENAI_API_KEY=… docker-compose up --build`; tests via `docker-compose run --rm test`.
- `open_webui/` — Self-hosted local-inference stack: Open WebUI (`:3000`) + SearXNG (`:4000`) + a custom Edge-TTS sidecar (`edge-tts-server.py`, `:5000`). `manage.sh` wraps common compose operations; `RESET.md` documents teardown.
- `local_vibe_code/` — Standalone `index.html` marketing/demo page; no build step.
- `safety_framework/` — Markdown only (`QUESTIONS.md`, `QUESTIONS_ANSWERS.md`); the 6-question AI safety planning framework referenced by the course. No code.

## Cross-cutting conventions

- **Secrets via environment variables only.** Examples expect `OPENAI_API_KEY`, `AWS_BEARER_TOKEN_BEDROCK`, `LITELLM_MASTER_KEY`, etc. to come from the shell or `.env`. Never hardcode them when extending examples.
- **No monorepo tooling.** There is no top-level `package.json`, `pyproject.toml`, lint, or test runner. Each Python example has its own `requirements.txt`; each Docker example has its own `docker-compose.yml`. Run commands from within the example's directory.
- **The Dual LLM invariant** (`simple_safe_agent`): if you touch that code, the rule "Privileged LLM never sees untrusted content" must hold. Untrusted data lives behind `$VARn` placeholders that only the Controller resolves, and only when calling the Quarantined LLM or rendering final display output.
