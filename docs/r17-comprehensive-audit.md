---
id: "R17"
title: "R17 — Comprehensive Science & Industry Audit (R1-R16)"
type: audit
date: 2026-09-06
status: final
tags: [vault, mcp, docker, ssh, mesh]
license: CC-BY-4.0
---

# R17 — Comprehensive Science & Industry Audit (R1-R16)

## Source
Gemini deep research audit of all 16 JiMesh modules.
Each module evaluated against SOTA 2026, open-source ecosystems, and
mathematical architecture.

---

## Part 1: Visual Core & Runtimes (R1, R2, R7, R9, R11, R16)

### R1 & R9 — Multi-Window Grid, iFrame Runtimes & HTTP/3
- **Status**: Client-side hidden pool (display:none) is SOTA. Server-side
  HTTP/3 cache for SPA state = NOT scientifically viable (can't reconstruct
  JS heap after DOM destroy).
- **Correction**: HTTP/3 (0-RTT) only for initial dashboard asset load, NOT
  iframe state preservation.
- **Critical gap**: Pointer-capture fix: `body[data-dragging="true"] iframe
  { pointer-events: none !important; }`

### R2 — Config Editor
- **Status**: CodeMirror 6 (NOT Monaco) — correct. Monaco kills memory in
  multi-window grids due to heavy web workers.

### R11 & R16 — SSH Tunnel, Port Detection, Sidebar Categories
- **Correction**: Raw TCP-over-SSH causes TCP-over-TCP meltdown. Use chisel
  (HTTP tunnel over SSH) or wireguard-go instead.
- **Terminal**: Use ttyd sidecar (NOT custom xterm.js-to-SSH in Go).

---

## Part 2: Advanced Inferences & Proxy Routing (R4, R8, R10)

### R4 & R8 — Entropy-Based Request Routing
- **Problem**: Two-phase request wastes TTFB when escalating. Shannon
  entropy measures statistical uncertainty, not logical complexity.
- **SOTA correction**: RouteLLM (UC Berkeley, ICLR 2025) — pre-inference
  classifier routes in <11µs. 85% cost reduction.
- **Streaming alternative**: Speculative Elongation — cheap model streams
  immediately, sliding window entropy (10 tokens), mid-flight cancel +
  cascade to reasoning model.
- **Paper**: arXiv:2406.04692 (FrugalGPT) for cascade math.

### R10 — Model Stats Enrichment & Fuzzy Dedup
- **Problem**: Levenshtein fails on multi-provider model IDs.
- **SOTA correction**: Canonical base ID normalization (regex) +
  Jaro-Winkler distance + inheritance principle for aliases.

---

## Part 3: Agent Orchestration & MCP (R3, R5, R6, R12, R14)

### R3, R5 & R6 — Go-Native Multi-Agent Orchestrator
- **Status**: Go goroutines + structured outputs = strategic advantage over
  Python (CrewAI/LangGraph = massive I/O overhead).
- **MoA optimization**: Logprob-based self-scoring (experts score each other)
  before aggregation. Prevents "Lost in the Middle" effect.
- **Paper**: arXiv:2406.04692 (Mixture of Agents).

### R12 — Agent Browser Control
- **Overkill**: chromedp for clicking own dashboard = too fragile.
- **Correction**: Agent controls platform via MCP tools (structured JSON-RPC),
  NOT visual clicking. chromedp only for external deployed apps (Adminer).
- **Token saving**: AOM (Accessibility Tree) mapping instead of raw HTML —
  saves 80% prompt tokens.

### R14 — Docker MCP Toolkit
- **Status**: Excellent architecture. Docker MCP = strongest isolation
  framework for untrusted LLM tools.
- **Zero-polling discovery**: Docker Events API (cli.Events) instead of
  polling. 0ms latency, 0% CPU idle.

---

## Part 4: SecOps, Multi-Tenant Vault & FinOps (R13, R15, R16)

### R16 — Multi-Tenant HashiCorp Vault
- **Status**: Industry standard. Logical tenant isolation via KV-v2 paths
  (secret/data/projects/{project_id}/*). Agents never see plaintext keys.
- **JIT injection**: Gateway extracts credentials at execution time, returns
  only structured result rows to agent.

### R15 & R16 — Cascading RBAC Budget & Circuit Breaker
- **Status**: Critical safety shield. Team → Project → User/Agent cascading
  limits. In-memory circuit breaker: context.Cancel() when limit hit.
- **Paper reference**: Deterministic SLA enforcement (arXiv:2511.15755).

---

## Part 5: Tech Ontology & Knowledge Base

### Status
- 40+ technologies mapped deterministically (0ms, no LLM)
- Port → Iconify icon → Category → Sidecar suggestions
- Cascading: ontology → OpenRouter API → SearXNG + utility model (cached 7 days)
- Scientific foundation: OBDA, arXiv:2305.04055

---

## Part 6: Implementation Status (HONEST)

### ✅ Written (code exists in repo)
| File | Feature | Build Verified |
|---|---|---|
| store/vault.go | Vault tables + methods | ❌ NOT VERIFIED |
| store/rbac.go | RBAC budgets, teams, app categories | ❌ NOT VERIFIED |
| store/secrets.go | AES-GCM-256 encrypt/decrypt | ❌ NOT VERIFIED |
| store/model_enrichment.go | Enrichment pipeline | ❌ NOT VERIFIED |
| store/model_roles.go | Model role schemas | ✅ (earlier session) |
| store/deployments.go | Deployment CRUD | ✅ (earlier session) |
| store/experts.go | Expert registry + runs | ❌ NOT VERIFIED |
| gateway/vault.go | Vault API handlers | ❌ NOT VERIFIED |
| gateway/vault_client.go | HashiCorp Vault client | ❌ NOT VERIFIED |
| gateway/rbac.go | Budget/Team/Category handlers | ❌ NOT VERIFIED |
| gateway/cost_breaker.go | Cost circuit breaker | ❌ NOT VERIFIED |
| gateway/traffic_inspector.go | RAM traffic metrics | ❌ NOT VERIFIED |
| gateway/discovery.go | Docker event discovery | ❌ NOT VERIFIED |
| gateway/tunnel.go | SSH tunnel bridge | ❌ NOT VERIFIED |
| gateway/ontology.go | Tech ontology API | ❌ NOT VERIFIED |
| gateway/orchestration.go | Orchestration SSE | ✅ (earlier session) |
| gateway/experts.go | MoE expert pipeline | ✅ (earlier session) |
| gateway/model_enrichment.go | Enrichment pipeline | ✅ (earlier session) |
| gateway/mesh_models.go | /v1/mesh/models | ✅ (earlier session) |
| network/tunnel.go | TunnelPool | ❌ NOT VERIFIED |
| network/port_detection.go | Port scanning | ❌ NOT VERIFIED |
| metadata/ontology.go | Static tech ontology | ❌ NOT VERIFIED |
| docker-compose.yml | Vault service added | ❌ NOT VERIFIED |

### ⚠️ Build Status: UNVERIFIED
Go and Docker are NOT available in the current execution environment.
All code was written but could NOT be compiled. There may be compile errors
that need fixing on the target box.

### Required verification on target box:
```bash
cd ~/leo/JiMesh && git pull
cd src/backend && go build -o /tmp/jimesh-server ./cmd/server
# Fix any compile errors, then:
make restart-backend
```

---

## Papers Referenced
| Paper | arXiv | Topic |
|---|---|---|
| FrugalGPT | 2406.04692 | LLM cascading math |
| Mixture of Agents | 2406.04692 | MoA candidate ranking |
| Speculative Decoding | 2211.17192 | Mid-flight stream cancel |
| Orchestration | 2601.13671 | MCP protocol |
| Deterministic SLA | 2511.15755 | Budget enforcement |
| Science & Tech Ontology | 2305.04055 | Ontology construction |
| RouteLLM | ICLR 2025 | Pre-inference routing |

## Industry References
| System | What |
|---|---|
| RouteLLM (lm-sys) | Pre-inference LLM routing classifier |
| Docker MCP Gateway | Isolated MCP server orchestration |
| modelcontextprotocol/servers | Pre-built MCP connectors |
| ttyd | Web terminal (sidecar, not custom) |
| chisel | HTTP tunnel over SSH (avoids TCP meltdown) |
| Iconify (@iconify/react) | On-demand icon loading (not react-icons) |
| CodeMirror 6 | Lightweight code editor (not Monaco) |
| ELK (@elkjs/elkjs) | Graph auto-layout (not dagre) |
| Jaro-Winkler | Fuzzy matching (not Levenshtein) |
