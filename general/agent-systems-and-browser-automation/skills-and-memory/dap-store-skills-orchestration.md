---
okf_version: "1.0"
id: "okf-age-ski-dap-store-skills-orchestration"
title: "Dynamic Agent Protocol (DAP) Agent Store Permissions, Tool-Skill Binding & DAP University"
topic: "general/agent-systems-and-browser-automation"
subtopic: "skills-and-memory"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - dap-protocol
  - agent-store
  - tool-skill-binding
  - qdrant
  - surrealdb
  - dap-university
summary: "Technical architectural reference for DAP Agent Store permissions, Qdrant/SurrealDB hybrid tool-skill binding, and DAP University automated skill verification."
---

# Dynamic Agent Protocol (DAP) Agent Store Permissions, Tool-Skill Binding & DAP University

## Executive Summary

Autonomous agent ecosystems require fine-grained access control, semantic tool discovery, and automated verification before newly acquired skills are executed in production.

This document details the **DAP Agent Store 5-tier permission model**, the **Qdrant vector / SurrealDB graph hybrid tool-skill binding engine**, and **DAP University** (a formal verification bootcamp harness for agent skill acquisition).

---

## 1. DAP Agent Store 5-Tier Permission Model

```
+-------------------------------------------------------------------+
| Tier 4: Root Admin Control (Schema Mutation & Permission Grants)  |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Tier 3: Tool Registration (Register New Vectors & Signatures)     |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Tier 2: Skill Acquisition (Download & Execute Signed Artifacts)  |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Tier 1: Executable Tool Calling (Invoke Whitelisted Standard Tools)|
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Tier 0: Public Discovery (Read-Only Tool & Skill Schema Browsing) |
+-------------------------------------------------------------------+
```

---

## 2. Hybrid Qdrant / SurrealDB Tool-Skill Binding

DAP decouples tool declarations using a two-tier database strategy:
1. **Qdrant Vector Index**: Enables fast semantic tool search based on embeddings of tool descriptions and arguments.
2. **SurrealDB Relational/Graph Store**: Stores cryptographic signatures, execution permissions, and event triggers (`tool_registered`, `skill_bound`).

### 2.1 SurrealDB Schema Definition Example

```surrealql
-- Define tool registration record
DEFINE TABLE tool SCHEMAFULL;
DEFINE FIELD name ON TABLE tool TYPE string;
DEFINE FIELD signature ON TABLE tool TYPE string;
DEFINE FIELD permission_tier ON TABLE tool TYPE int;

-- Define event trigger for audit logging
DEFINE EVENT tool_registered ON TABLE tool WHEN $event = "CREATE" THEN (
    CREATE audit_log SET
        action = "TOOL_REGISTERED",
        tool_name = $after.name,
        timestamp = time::now()
);
```

---

## 3. DAP University: Automated Verification Harness

DAP University is a structured skill acquisition pipeline where agents complete automated evaluation suites before a newly synthesized skill artifact is published to Tier 2 execution access.

```
Agent Skill Candidate
          |
          v
+---------------------------------------+
| 1. Curriculum Assessment              |
| (Executes Unit & Edge-Case Test Suites)|
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
| 2. Execution Sandbox Logging          |
| (Captures Memory & Syscall Audit)     |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
| 3. Formal Verification                |
| (Cryptographic Signature & Signing)   |
+-------------------+-------------------+
                    |
                    v
Published DAP Tier 2 Skill Artifact
```

---

## Sources & References

- [https://github.com/ji-podhead/dap-docs](https://github.com/ji-podhead/dap-docs)
- [https://ji-podhead.github.io/dap-docs/](https://ji-podhead.github.io/dap-docs/)
