---
okf_version: "1.0"
id: "okf-sec-guard-rag-poisoning-killchain"
title: "RAG Poisoning and the Agentic Kill Chain: From Open Port to Agent Takeover"
topic: "general/security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - rag-poisoning
  - prompt-injection
  - indirect-prompt-injection
  - agentic-security
  - kill-chain
  - vector-database
summary: "RAG/vector-database poisoning mechanism (PoisonedRAG), how it differs structurally from token glitches and malicious skill execution, and the 4-phase kill chain that combines an infrastructure misconfiguration with data poisoning into full agent compromise."
---

# RAG Poisoning and the Agentic Kill Chain: From Open Port to Agent Takeover

## Mechanism (RAG poisoning / indirect prompt injection via retrieval)

1. **Injection** — attacker plants text with a hidden instruction somewhere an ingestion pipeline will read it (wiki page, PDF, support ticket, code comment).
2. **Embedding** — ingestion job vectorizes and stores it, indistinguishable from any legitimate document at write time.
3. **Retrieval** — an ordinary, unrelated user query triggers a genuine semantic match; the retriever correctly returns the poisoned chunk.
4. **Execution** — the model receives the retrieved text as context. Most RAG pipelines don't structurally separate "retrieved data" from "instructions," so the model treats the injected text as an instruction.

Documented, actively researched: **PoisonedRAG** (Zou, Geng, Wang, Jia — arXiv:2402.07867) shows a small number of injected malicious texts is sufficient to reliably control targeted-query output. Survey: "Adversarial Threat Vectors and Risk Mitigation for RAG Systems" (arXiv:2506.00281) catalogs poisoning as a primary RAG-specific attack surface, distinct from ordinary prompt injection.

## Three distinct failure modes (frequently conflated)

| | RAG Poisoning | Token Glitches | Malicious Skills |
|---|---|---|---|
| Fault location | Stored data | Tokenizer/vocabulary | Agent's granted permissions |
| Trigger | Planted text later retrieved | Rare/anomalous token sequence | Model induced to call an available tool |
| Effect | Model follows injected instructions as "knowledge" | Model degrades/loops/produces bizarre output | Model performs a real external action |
| Attacker control | High, targeted, repeatable | Low — training artifact, not a reliable delivery mechanism | High, but only once something else delivers the instruction |

Token glitches (`SolidGoldMagikarp` class) are a training-data artifact — not a controllable delivery mechanism for a specific attacker goal. Malicious skill execution is a permissions-layer problem independent of how the instruction reached the model. They compound only when chained.

## The 4-phase kill chain

1. **Infrastructure compromise** — exposed unauthenticated service (see [[okf-sec-asm-cyberspace-search-engines]]) gives code execution or filesystem access.
2. **Secret harvesting** — `.env`/config files read; LLM provider keys and internal service tokens extracted. Converts "access to one container" into "ability to act as the AI application."
3. **Workflow/skill injection** — attacker (via Phase 1 foothold, or via RAG poisoning of a trusted data source) adds/modifies a tool definition to perform a malicious action under an innocuous name.
4. **Trigger** — one ordinary user interaction causes retrieval of the poisoned content or invocation of the modified skill; the agent executes with its existing privileges.

Key property: each phase patched in isolation leaves the others intact (closing the port doesn't rotate already-read keys; rotating keys doesn't undo an already-poisoned vector store).

## Defense-in-depth, mapped to phase

- **Phase 1**: see [[okf-sec-asm-hardening-exposed-services]] — bind/authenticate/isolate.
- **Phase 2**: secrets manager, not `.env` readable post-startup; least-privilege container identity, not one API key that does everything.
- **Phase 3**: structurally separate retrieved-data from instructions in prompt construction (not just convention); review tool/skill definition changes as code changes; never load tools from a writable/external/shared location dynamically.
- **Phase 4**: sandbox the agent's code-execution/tool-invocation surface with an explicit minimal capability set (gVisor or equivalent) — the point is bounding blast radius when a bypass succeeds, not preventing every injection attempt.

## Source article

- articles repo: `rag-poisoning-killchain/2026-09-16-rag-poisoning-killchain-blogpost.md` ("From an Open Port to Agent Takeover").

## Sources

- PoisonedRAG (Zou et al.) — https://arxiv.org/abs/2402.07867
- Adversarial Threat Vectors for RAG Systems — https://arxiv.org/html/2506.00281v1
- OWASP Top 10 for LLM Applications — https://owasp.org/www-project-top-10-for-large-language-model-applications/
- gVisor — https://gvisor.dev
