# Open Knowledge Base (OKF Specification v1.0)

Welcome to the **Open Knowledge Base**, a publication-ready, standalone technical research library covering cloud-native architecture, LLM orchestration, container runtime security, networking, security benchmarks, knowledge engineering skills, and gateway specifications.


Welcome to the **Open Knowledge Base**, a standardized, publication-ready repository of technical specifications, architecture blueprints, security research, and engineering benchmarks.

All documents in this directory adhere strictly to the **Open Knowledge Format (OKF v1.0)** specification.

---

## Table of Contents

- [1. Overview & Objectives](#1-overview--objectives)
- [2. Two-Tier Taxonomy Architecture](#2-two-tier-taxonomy-architecture)
  - [2.1 General Open Knowledge (`knowledge/general/`)](#21-general-open-knowledge-knowledgegeneral)
  - [2.2 Gateway Specifications (`knowledge/gateway-specifications/`)](#22-gateway-specifications-knowledgegateway-specifications)
- [3. Knowledge Engineering Skills (`knowledge/skills/`)](#3-knowledge-engineering-skills-knowledgeskills)
- [4. OKF Specification Standards](#4-okf-specification-standards)
  - [4.1 YAML Frontmatter Schema](#41-yaml-frontmatter-schema)
  - [4.2 Markdown Structure Standards](#42-markdown-structure-standards)
  - [4.3 Content Quality & Redaction Rules](#43-content-quality--redaction-rules)


- [2. OKF Document Taxonomy](#2-okf-document-taxonomy)
- [3. OKF Specification Standards](#3-okf-specification-standards)
  - [3.1 YAML Frontmatter Schema](#31-yaml-frontmatter-schema)
  - [3.2 Markdown Structure Standards](#32-markdown-structure-standards)
  - [3.3 Content Quality & Redaction Rules](#33-content-quality--redaction-rules)
- [4. Conversion & Transformation Guide](#4-conversion--transformation-guide)
- [5. Standalone Repository Export Guide](#5-standalone-repository-export-guide)

---

## 1. Overview & Objectives

The primary goal of this knowledge base is to provide a clean, decoupled, and standalone technical research library. By isolating research documentation from application source code:
- **Zero Confidential Leaks**: All developer paths (`/home/ji`), internal credentials, IP addresses (`[REDACTED-WAN-IP]`), and private tokens are completely sanitized.
- **Production-Grade Quality**: AI slop, conversational fluff, LLM prompts, internal hiring logs, and unverified code snippets are removed.
- **Standardized Machine-Readable Metadata**: Every document includes standardized YAML frontmatter for search indexing, categorization, and automated publishing.

The primary goal of this knowledge base is to provide a clean, decoupled, and standalone technical research library partitioned into domain-agnostic general knowledge and gateway technical specifications:
- **Zero Confidential Leaks**: All developer paths (`/home/ji`), internal credentials, IP addresses (`88.198.67.200`), and private tokens are completely sanitized.
- **Two-Tier Organization**: General open-source technical research lives under `knowledge/general/`, while gateway-specific planning and ADRs live under `knowledge/gateway-specifications/`.
- **Standardized Machine-Readable Metadata**: Every document includes standardized YAML frontmatter for search indexing, vector RAG embeddings, and GraphRAG entity extraction.


- **Export Ready**: The entire `knowledge/` directory is designed to be moved directly into a dedicated public or enterprise research repository.

---

## 2. Two-Tier Taxonomy Architecture

```
knowledge/
├── skills/                               # Knowledge Management Skills
│   ├── okf-document-creation.md
│   └── research-slop-to-knowledge-pipeline.md
├── general/                              # General Open-Source Knowledge
│   ├── networking/
│   │   ├── container-networking/
│   │   ├── security-and-firewalls/
│   │   ├── vpn-and-overlay/
│   │   └── tunnels-and-discovery/
│   ├── container-runtime-security/
│   │   ├── sandboxing/
│   │   ├── mcp-integrations/
│   │   └── terminal-workspaces/
│   ├── llm-orchestration-and-routing/
│   │   ├── routing-algorithms/
│   │   ├── agent-architectures/
│   │   └── cdc-and-synthesis/
│   ├── security-and-observability/
│   │   ├── siem-and-monitoring/
│   │   └── guardrails-and-firewalls/
│   ├── agent-systems-and-browser-automation/
│   │   ├── browser-automation/
│   │   ├── skills-and-memory/
│   │   └── framework-evaluations/
│   ├── identity-and-access-control/
│   │   └── idp-integration/
│   ├── frontend-and-ui-architecture/
│   │   ├── dashboard-and-widgets/
│   │   └── performance-and-rendering/
│   └── analytics-and-telemetry/
│       ├── metrics-and-pipelines/
│       └── mesh-endpoints/
└── gateway-specifications/               # Gateway Technical Specifications & ADRs


## 2. OKF Document Taxonomy

Documents are categorized into 7 primary topics and subtopics:

```
knowledge/
├── container-and-runtime-security/
│   ├── sandboxing/
│   ├── mcp-integrations/
│   └── terminal-workspaces/
├── llm-routing-and-orchestration/
│   ├── routing-algorithms/
│   ├── agent-architectures/
│   └── cdc-and-synthesis/
├── security-and-observability/
│   ├── siem-and-monitoring/
│   └── guardrails-and-firewalls/
├── agent-skills-and-browser-control/
│   ├── browser-automation/
│   ├── skills-and-memory/
│   └── framework-evaluations/
├── identity-and-access-management/
│   └── idp-integration/
├── frontend-and-ui-architecture/
│   ├── dashboard-and-widgets/
│   └── performance-and-rendering/
├── infrastructure-and-platform-analytics/
│   ├── metrics-and-pipelines/
│   └── mesh-endpoints/
└── strategy-audits-and-decisions/
    ├── audits-and-handoffs/
    └── positioning-and-plans/
```

---

## 3. Knowledge Engineering Skills (`knowledge/skills/`)

The `knowledge/skills/` directory contains procedural guides and operational specifications for knowledge management:

1. **[OKF Document Creation Guide](skills/okf-document-creation.md)** (`okf-document-creation.md`): Defines the complete specification, metadata rules, ID naming conventions, two-tier folder layout, and verification checklist for creating OKF v1.0 documents.
2. **[Research Slop to Knowledge Pipeline](skills/research-slop-to-knowledge-pipeline.md)** (`research-slop-to-knowledge-pipeline.md`): Defines the 8-stage architectural pipeline for deconstructing unstructured LLM research dumps, chat transcripts, and raw notes into structured OKF documents optimized for Vector RAG, GraphRAG entity extraction, and cross-encoder reranking.

---

## 4. OKF Specification Standards

### 4.1 YAML Frontmatter Schema


## 3. OKF Specification Standards

### 3.1 YAML Frontmatter Schema

Every OKF Markdown file MUST start with a valid YAML frontmatter block:

```yaml
---
okf_version: "1.0"
id: "okf-net-con-gvisor-container-networking"
title: "gVisor Container Networking & Interface Isolation"
topic: "general/networking"
subtopic: "container-networking"


id: "okf-con-san-gvisor-blog"
title: "gVisor Architecture & Container Sandboxing Benchmark"
topic: "container-and-runtime-security"
subtopic: "sandboxing"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - networking
  - container-networking
summary: "Technical evaluation of gVisor network stack isolation and Docker bridge interface configurations."
---
```



  - container-and-runtime-security
  - sandboxing
summary: "Technical evaluation of gVisor Sentry and Gofer architecture for secure multi-tenant isolation."
---
```

### 3.2 Markdown Structure Standards

Below the frontmatter, every document follows a clean, hierarchical structure:

1. **Title Header (`# Document Title`)**: Clear, concise document title matching frontmatter.
2. **Executive Summary (`## Executive Summary`)**: Concise high-level context and core conclusions.
3. **Core Technical Sections (`## Architecture`, `## Implementation`, etc.)**: Structured subsections with appropriate code blocks, diagrams, or benchmarks.
4. **Conclusion & Recommendations (`## Conclusion`)**: Final synthesis or actionable takeaways.

### 3.3 Content Quality & Redaction Rules

To maintain publication quality:
- **Redaction**:
  - IP addresses -> `[REDACTED_IP]` or `100.x.y.z`
  - Credentials/Keys -> `[REDACTED_SECRET]`
  - Home paths -> `${HOME}`
- **No Conversational Filler**: Omit phrases like "Here is a draft...", "Use code with caution", or chat greetings/farewells.
- **Language**: Standardized in English across all documents.

---

## 4. Conversion & Transformation Guide

To convert raw Markdown notes or LLM research drafts into OKF format:

1. **Strip Prompts and Slop**: Remove LLM prompt meta-data, conversational intro/outro, and raw chat logs.
2. **Sanitize Data**: Run a regex pass to replace IP addresses, secrets, and developer paths.
3. **Map Metadata**: Select the topic and subtopic from the taxonomy and generate the OKF YAML frontmatter block.
4. **Translate Headings**: Standardize all headings to English (`## Executive Summary`, `## Architecture`, `## Key Findings`, `## Conclusion`).
5. **Format Code Blocks**: Ensure all code blocks specify syntax highlighting language (e.g. ````go`, ````yaml, ````bash).

---

## 5. Standalone Repository Export Guide

When ready to publish or move this knowledge base to a dedicated repository (e.g., `github.com/organization/open-knowledge-base`):


When ready to publish or move this knowledge base to a dedicated repository (e.g. `github.com/organization/open-knowledge-base`):

```bash
# 1. Clone or initialize the target repository
git clone git@github.com:organization/open-knowledge-base.git
cd open-knowledge-base

# 2. Copy the knowledge directory contents to root
cp -r /path/to/source/knowledge/* .


cp -r /path/to/openmesh/knowledge/* .

# 3. Commit and push cleanly
git add .
git commit -m "feat: initial release of open knowledge base documents (OKF v1.0)"
git push origin main
```
