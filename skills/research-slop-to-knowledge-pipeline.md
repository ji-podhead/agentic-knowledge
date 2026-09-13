---
okf_version: "1.0"
id: "okf-skl-slop-to-knowledge-pipeline"
title: "Research Slop Deconstruction & GraphRAG Structuring Pipeline"
topic: "skills"
subtopic: "knowledge-engineering"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - knowledge-engineering
  - graphrag
  - semantic-extraction
  - okf
  - slop-deconstruction
summary: "Comprehensive operational skill defining the multi-stage transformation process for converting unstructured LLM research dumps, chat transcripts, and internal project notes into publication-grade, two-tier OKF knowledge documents."
---

# Research Slop Deconstruction & GraphRAG Structuring Pipeline

## Overview

In modern software development and AI engineering, research materials frequently begin as unstructured LLM chat transcripts, ad-hoc prompt dumps, internal audit notes, or raw developer logs ("research slop"). These raw outputs are noisy, unformatted, context-bound, and riddled with conversational filler, hallucinated code fragments, sensitive internal details, and product-specific ticket numbers.

This skill documents the **8-Stage Iterative Pipeline** for systematically decomposing, filtering, sanitizing, translating, and structuring chaotic research slop into standalone, high-value **Open Knowledge Format (OKF v1.0)** documents partitioned across two primary tiers:
1. **`knowledge/general/`**: Pure, domain-agnostic open-source technical research.
2. **`knowledge/gateway-specifications/`**: Product-specific technical planning, architectural decision records (ADRs), and gateway specifications.

---

## Two-Tier Knowledge Separation

When processing research slop, triage content into two distinct branches:

```
                          [ RAW RESEARCH SLOP ]
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
    [ GENERAL TECHNICAL KNOWLEDGE ]    [ GATEWAY SPECIFICATIONS & ADRs ]
    - Domain algorithms & protocols     - Gateway architectural decisions
    - Container sandboxing benchmarks   - Platform positioning & reviews
    - RAG & GraphRAG pipelines          - System design specifications
                  │                                   │
                  ▼                                   ▼
    `knowledge/general/<domain>/`      `knowledge/gateway-specifications/`
```

---

## The 8-Stage Transformation Architecture

### Stage 1: Ingestion & Taxonomy Partitioning
Catalog all raw markdown files and research drafts. Determine whether the content represents domain-agnostic technical knowledge (`knowledge/general/`) or gateway-specific specifications and architectural decisions (`knowledge/gateway-specifications/`).

### Stage 2: Conversational Slop & Fluff Removal
Remove LLM greetings (*"Here is a proposal..."*), conversational transcript blocks (*"User: ... AI: ..."*), and transient UI layout proposals.

### Stage 3: Internal Project Artifact Purging
Strip ticket IDs (`TASK-xxx`), sprint milestones (`Sprint xx`), work package tags (`WPx`), and specific internal source file paths. Rephrase specific code references into conceptual architectural layers.

### Stage 4: Sensitive Data Redaction
Sanitize IPv4/v6 addresses (`88.198.67.200` -> `[REDACTED_IP]`), Tailscale IPs (`100.x.y.z`), passwords, secret keys, and developer home paths (`${HOME}`).

### Stage 5: Branding Abstraction & Generalization
Convert product-specific codenames in general research files into universal architectural terms (*the multi-provider gateway*, *the L7 reverse proxy*, *the control plane*). Retain exact gateway context only inside `knowledge/gateway-specifications/`.

### Stage 6: Audit-to-Guide Transformations
Rewrite internal post-mortems, salvage reviews, and handoff notes into standalone technical architecture guidebooks.

### Stage 7: Technical English Translation & Standardization
Translate 100% of body copy, headings, table contents, and code comments into technical English.

### Stage 8: OKF Synthesis & GraphRAG / RAG Optimization
Prepend standard OKF v1.0 YAML frontmatter (`id`, `topic`, `subtopic`, `tags`, `summary`) and ensure section blocks (300-800 tokens) are optimized for vector embeddings, GraphRAG entity extraction, and cross-encoder rerankers.

---

## Quality Audit Checklist

- [ ] Partitioned correctly into `general/` or `gateway-specifications/`.
- [ ] Zero chat log transcripts, LLM fluff, or conversational greetings.
- [ ] Zero internal ticket numbers (`TASK-xxx`), sprint tags (`Sprint xx`), or work packages (`WPx`).
- [ ] Zero private IPs (`88.198.67.200`), passwords, or developer paths (`/home/...`).
- [ ] 100% written in technical English.
- [ ] Valid OKF v1.0 YAML frontmatter header present on line 1.
