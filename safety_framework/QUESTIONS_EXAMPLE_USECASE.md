# Generative AI Safety Framework — 6 Business-Logic Planning Questions

Use each question to capture: **decision**, **owner**, **evidence/artifact**, **due date**.

## 1) What business outcomes will the AI influence, and what’s the maximum acceptable harm?
- Which workflows will use AI output (advice, triage, approvals, customer-facing, internal ops)?
  Developers will use ai-powered coding tools.
  Users will interact with a RAG question-answering system.
- Define impact tiers and “stop-the-line” thresholds (money, legal, safety, reputational, customer trust).

## 2) What is the AI allowed to know, retrieve, store, and reveal?
- Allowed vs forbidden data classes (PII, credentials, contracts, source code, pricing, health/finance).
  AI-Powered coding tools will be exposed to some IP.
  RAG systems are exposed to some IP.
- Rules for retention/logging, redaction, training opt-out, and cross-tenant/team separation (RAG permissions).
  AI systems cannot be exposed to personal user info.

## 3) What is the AI allowed to *do* (actions), and what guardrails enforce business policy?
- List permitted actions (e.g., issue refund, change account status, send emails, run queries, deploy code).
- For each action: prerequisites, limits, reversibility, and deterministic checks outside the model.

## 4) Where can inputs come from, and how do we treat untrusted content to prevent manipulation?
- Inputs: user prompts, files, emails, web pages, tickets, knowledge base, integrations.
- Rules for isolating/labeling untrusted content, and what decisions/actions are blocked when content is untrusted or ambiguous.

## 5) How do we ensure outputs are safe to use in downstream business systems?
- Required output formats and validation (schemas), safe rendering, safe query generation, safe tool calls.
- What can never be auto-executed, and what must be confirmed or reviewed.

## 6) How will we operate this safely over time (governance, monitoring, cost, vendors, incidents)?
- KPIs/SLOs (quality, groundedness, latency, uptime) + budget/rate limits and abuse detection.
- Model/vendor change control (evaluation, versioning, rollback) and incident playbook (leakage, misinfo, harmful action).
