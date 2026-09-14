---
okf_version: "1.0"
id: "okf-rag-age-agentic-rag-pipelines"
title: "Agentic RAG Pipelines: Budgets, Gates and Trust Boundaries"
topic: "general/retrieval-augmented-generation"
subtopic: "agentic-rag"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - agentic-rag
  - agents
  - quality-gates
  - access-control
  - okf
  - evaluation
summary: "RAG as a governed workflow phase: token budgets, layered access control, graph persistence, quality gates before memory writes and metadata-first agent reading."
---

# Agentic RAG Pipelines: Budgets, Gates and Trust Boundaries

## Executive Summary

For agents, RAG should not be a tool that dumps raw chunks into the context window. The working pattern is a governed workflow phase: a grounding step with a hard token budget, layered access control, graph persistence of what was used, and quality gates that decide what enters long-term memory. On the reading side, agents should consume structured knowledge metadata before bodies at all.

## RAG as a Workflow Phase

Declare grounding as a first-class phase with a configuration, not an ad-hoc tool call: source collections (public content, agent memory, skill artifacts), the query source, top_k, a hard max_tokens budget with summarization enabled, and persist_links. Unbounded chunk dumps cost roughly four times more tokens than a budgeted, summarized grounding step — and they bypass access control.

## Four Layers of Access Control

    Layer 1: capabilities      restrict the agent to defined query endpoints
    Layer 2: DB permissions    row-level rules (access_level in allowed set)
    Layer 3: index filter      the same constraint as a payload filter at query time
    Layer 4: RBAC              specific classified collections need explicit roles

The result: an agent receives exactly the chunks it is allowed to see — no post-hoc filtering, no leakage through the retrieval path.

## Persistence Turns Search into Memory

When a grounding phase finishes, link what was used into the graph: agent to fetched chunk with session, score and timestamp, and chunk to the claims it supports. Future sessions traverse these links instead of re-searching — one graph query answers "what did I find before on this topic". Skill artifacts become retrievable collections themselves: an agent with a high skill level gets its own proven strategies injected alongside external chunks; a novice gets only generic content.

## Quality Gates Before Memory Writes

Retrieval corpora degrade when agents write unverified output back. The fix is a gate: score every candidate memory (reasoning coherence, evidence quality) and persist only above threshold; verified search paths that score high become reusable artifacts. This keeps compound agents from poisoning their own knowledge base — the failure mode where early mistakes keep getting retrieved as facts.

## Metadata-First Reading for Agents

For curated knowledge bases, agents should not embed everything; they should read structure first. Scan frontmatter only (id, topic, tags, status, summary — a few hundred bytes per document), filter deterministically on those fields, then fetch bodies or single heading sections for the filtered subset only. Two tools cover the whole loop: one that searches the metadata index, one that fetches a validated document or section by id. This avoids embedding cost and reranking noise entirely for well-formed corpora and saves the large majority of tokens versus full-text search.

## Evaluation as a Pipeline Stage

Measure the loop, not just the answer: retrieval metrics (recall at k, fused-rank quality), answer metrics (faithfulness, relevance — RAGAS-style), and verification metrics (proof status distribution, score progression on a fixed QA set such as StrategyQA). Run the evaluation suite as a regression test on every pipeline change; a retrieval or chunking change that lowers proof rates is a regression even when answers still look plausible.

## Conclusion

Agentic RAG is governance: budgets on input, permissions on access, links on usage, gates on memory, metadata-first reading on curated corpora, and evaluation as a regression gate. Each control is simple; together they make an agent's knowledge loop auditable end to end.
