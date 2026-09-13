---
okf_version: "1.0"
id: "okf-skl-doc-creation-guide"
title: "Open Knowledge Format (OKF v1.0) Specification & Creation Guide"
topic: "skills"
subtopic: "documentation-standards"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - okf-spec
  - documentation
  - skill
summary: "Comprehensive guide and specification for creating, formatting, and validating Open Knowledge Format (OKF v1.0) documents across General Knowledge and Gateway Specifications."
---

# Open Knowledge Format (OKF v1.0) Specification & Creation Guide

## Overview

The **Open Knowledge Format (OKF v1.0)** is a standardized Markdown document specification designed for machine-readable indexing, RAG (Retrieval-Augmented Generation) vector ingestion, GraphRAG entity extraction, and clean human consumption.

This skill defines the schema, two-tier repository layout, metadata standards, and validation checklist for creating valid OKF documents.

---

## 1. Two-Tier Taxonomy Architecture

Documents in the OKF Knowledge Base are partitioned into two distinct top-level directories:

1. **`knowledge/general/`**: Pure, domain-agnostic open-source technical research and engineering guides.
2. **`knowledge/gateway-specifications/`**: Product-specific technical specifications, architectural decision records (ADRs), system reviews, and gateway planning documents.

```
knowledge/
├── skills/
│   ├── okf-document-creation.md
│   └── research-slop-to-knowledge-pipeline.md
├── general/                             # Domain-Agnostic Open Knowledge
│   ├── networking/
│   ├── container-runtime-security/
│   ├── llm-orchestration-and-routing/
│   ├── security-and-observability/
│   ├── agent-systems-and-browser-automation/
│   ├── identity-and-access-control/
│   ├── frontend-and-ui-architecture/
│   └── analytics-and-telemetry/
└── gateway-specifications/              # Gateway Technical Specifications & ADRs
    ├── audits-and-handoffs/
    └── positioning-and-plans/
```

---

## 2. YAML Frontmatter Specification

Every OKF Markdown file MUST start with a valid YAML frontmatter block:

```yaml
---
okf_version: "1.0"                   # Required: OKF spec version (e.g. "1.0")
id: "okf-<domain>-<subdomain>-<slug>" # Required: Unique document identifier
title: "Document Title"              # Required: Clear, descriptive title
topic: "general/networking"          # Required: Top-level category path
subtopic: "container-networking"     # Required: Secondary category
status: "published"                  # Required: "draft" | "review" | "published"
visibility: "public"                 # Required: "public" | "internal" | "restricted"
created_at: "YYYY-MM-DD"             # Required: ISO 8601 creation date
tags:                                # Required: List of search/indexing tags
  - networking
  - container-networking
summary: "Concise 1-2 sentence summary of the document for vector embeddings."
---
```

---

## 3. Verification Checklist & Validation Script

Before committing OKF documents, run this validation script:

```python
import glob, re

files = glob.glob('knowledge/**/*.md', recursive=True)
for f in files:
    if f.endswith('README.md'): continue
    with open(f) as fp:
        c = fp.read()
    assert c.startswith('---'), f"Missing YAML frontmatter in {f}"
    assert 'okf_version: "1.0"' in c, f"Invalid okf_version in {f}"
    assert re.search(r'^id:\s*"okf-[a-z0-9-]+"', c, re.MULTILINE), f"Invalid ID schema in {f}"
    assert re.search(r'^title:\s*".+"', c, re.MULTILINE), f"Invalid title schema in {f}"
    assert re.search(r'^summary:\s*".+"', c, re.MULTILINE), f"Invalid summary schema in {f}"
print("All OKF documents validated successfully!")
```

- [ ] Starts with `---` frontmatter block on line 1.
- [ ] Correct top-level folder classification (`general/` vs `gateway-specifications/`).
- [ ] Body contains zero private IPs, secrets, or internal developer home paths.
- [ ] Written entirely in technical English without conversational filler or chat logs.
