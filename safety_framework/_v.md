# Generative AI Safety Framework — 6 Business-Logic Planning Questions

Use each question to capture: **decision**, **owner**, **evidence/artifact**, **due date**.

## 1) What business outcomes will the AI influence, and what’s the maximum acceptable harm?
- Which workflows will use AI output (advice, triage, approvals, customer-facing, internal ops)?
  AI systems will have an impact on developer tools as well as question-answering systems that use RAG.
- Define impact tiers and “stop-the-line” thresholds (money, legal, safety, reputational, customer trust).
  Customers may receive less relevant or perhaps inaccurate information from question-answering systems,
  developers who do not check their Codes can produce bugs or malicious software.

## 2) What is the AI allowed to know, retrieve, store, and reveal?
- Allowed vs forbidden data classes (PII, credentials, contracts, source code, pricing, health/finance).
  AI systems have access to company code, which is intellectual property. It cannot be exposed to credentials,
  authentication keys, or passwords. AI systems can never be exposed to customer identifying information.
- Rules for retention/logging, redaction, training opt-out, and cross-tenant/team separation (RAG permissions).

## 3) What is the AI allowed to *do* (actions), and what guardrails enforce business policy?
- List permitted actions (e.g., issue refund, change account status, send emails, run queries, deploy code).
  AI systems are allowed to produce working code and generate answers to customer questions.
- For each action: prerequisites, limits, reversibility, and deterministic checks outside the model.

## 4) Where can inputs come from, and how do we treat untrusted content to prevent manipulation?
- Inputs: user prompts, files, emails, web pages, tickets, knowledge base, integrations.
  Inputs come from employees' prompts when it comes to generating codes. Inputs also come from customer questions.
  Documents when it comes to question answer-answering are limited to trusted content.
- Rules for isolating/labeling untrusted content, and what decisions/actions are blocked when content is untrusted or ambiguous.

## 5) How do we ensure outputs are safe to use in downstream business systems?
- Required output formats and validation (schemas), safe rendering, safe query generation, safe tool calls.
  AI outputs are filtered through a moderation component as well as regex patterns that check for uh invalid outputs.
- What can never be auto-executed, and what must be confirmed or reviewed.

## 6) How will we operate this safely over time (governance, monitoring, cost, vendors, incidents)?
- KPIs/SLOs (quality, groundedness, latency, uptime) + budget/rate limits and abuse detection.
  We will create labels for uh bug reports that are a result of poorly generated AI code.
  We will also document inaccurate answers to customers' questions when possible.
- Model/vendor change control (evaluation, versioning, rollback) and incident playbook (leakage, misinfo, harmful action).
