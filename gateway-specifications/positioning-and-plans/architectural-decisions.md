---
okf_version: "1.0"
id: "okf-arc-pos-architectural-decisions"
title: "Architectural Decision Register for Multi-Provider Gateways"
topic: "gateway-specifications/positioning-and-plans"
subtopic: "positioning-and-plans"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - architecture-and-design-decisions
  - positioning-and-plans
summary: "Universal technical specification and architecture guide covering Architectural Decision Register for Multi-Provider Gateways."
---

# Architectural Decision Register for Multi-Provider Gateways


## Architectural Decision Register (ADR) Overview

This document records universal architectural decision records for building scalable, secure multi-provider LLM gateways and container execution platforms.

### Decision 1: Pure-Go Core with Postgres Persistence
- **Context**: A routing gateway must deliver sub-millisecond proxy latencies while supporting complex state management and dynamic routing tables.
- **Decision**: Implement the core gateway proxy, routing logic, and API surface in pure Go (`CGO_ENABLED=0`) backed by PostgreSQL (`pgx v5`). Avoid embedded SQLite or local file-based state for production deployments.

### Decision 2: Zero-Trust Secret Vault Integration
- **Context**: Autonomous AI agents must execute tools requiring third-party API keys without exposing plaintext credentials to agent memory or prompts.
- **Decision**: Store all sensitive keys in HashiCorp Vault (or AES-256-GCM encrypted persistence). Inject credentials at the proxy boundary just-in-time during HTTP/gRPC egress execution.

### Decision 3: Pre-Call Cascading RBAC Budgeting
- **Context**: Multi-tenant LLM gateways are exposed to runaway API costs from recursive agent loops.
- **Decision**: Enforce pre-call cost authorization across Team -> Project -> User hierarchies before dispatching requests to upstream LLM providers.
