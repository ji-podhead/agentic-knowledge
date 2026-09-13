---
id: "R15"
title: "R15 — Advanced Research Audit (Gemini Deep Analysis)"
type: audit
date: 2026-09-06
status: final
tags: [ssh, mcp, docker, entropy, mesh]
license: CC-BY-4.0
---

# R15 — Advanced Research Audit (Gemini Deep Analysis)

## Summary
Full audit of R1-R14. Cuts overkill, recommends open-source shortcuts,
identifies critical gaps. This supersedes earlier plans where noted.

---

## 🔴 CUT (Quatsch / Overkill)

### 1. HTTP/3 Reverse Proxy iFrame Cache (R9) — CUT
- **Why**: Server can't reconstruct SPA JS-heap state after DOM destroy.
  HTTP/3 0-RTT can't preserve websocket connections, event listeners, JS state.
- **Replace with**: Pure client-side hidden pool. `display: none` / `visibility: hidden`.
  DOM stays alive, JS state preserved, switch time = 0ms.
- **HTTP/3 use**: Only for initial dashboard asset load (0-RTT for bundles), NOT iframe state.

### 2. Custom xterm.js-to-SSH Bridge in Go (R11) — CUT
- **Why**: Terminal emulation in Go is months of fragile work.
- **Replace with**: ttyd (or gotty) as sidecar container. Takes any shell/docker exec,
  transforms to WebSocket stream. E2E deployment starts ttyd sidecar, tunnel the port.

### 3. chromedp for clicking own dashboard (R12) — CUT for internal use
- **Why**: Visual clicking of own UI is too fragile. Every frontend update breaks selectors.
- **Replace with**: MCP tools (jimesh.deploy, jimesh.provision via structured JSON-RPC).
- **chromedp kept for**: Testing external deployed apps (Adminer, user frontends).
  Use AOM (Accessibility Tree) mapping, not raw HTML — saves 80% prompt tokens.

### 4. Custom TCP-over-TCP SSH Tunnel (R11) — REPLACE
- **Why**: TCP-over-TCP causes congestion control meltdown on bad connections.
- **Replace with**: chisel (HTTP tunnel over SSH) or wireguard-go.
  For start: chisel pattern is simplest and proven.

---

## 🟡 CHANGE (Easier with existing tools)

### 5. Entropy Routing (R4) — CHANGE approach
- **Problem**: Two-phase Shannon entropy wastes TTFB when escalating (cheap model
  generates fully, then discarded). Measures statistical uncertainty, not logical complexity.
- **Option A (Industry standard)**: RouteLLM (lm-sys/RouteLLM). Pre-inference
  classifier (tiny linear/embedding model) routes in <10ms before any generation.
- **Option B (Streaming-optimal)**: Speculative Elongation. Cheap model streams
  immediately to user. Sliding window entropy (10 tokens). If entropy rises above
  threshold, cancel stream mid-flight (context.Cancel()), switch to reasoning model.
  User sees instant response, cascade only when needed.
- **Paper**: FrugalGPT (arXiv:2406.04692) — mathematical foundation for LLM cascading.
- **DB**: Add `reasoning_tokens` column (cloud providers charge 3x for these).

### 6. Fuzzy Matching (R10) — CHANGE algorithm
- **Problem**: Levenshtein fails on multi-provider model IDs (prefixes corrupt score).
- **Replace with**: Normalize to canonical base ID via regex: `[vendor]-[family]-[size]-[variant]`.
  Then Jaro-Winkler distance (token-based, more robust for short strings).
  Inheritance: metadata loaded for one ID → all aliases in same base-ID group inherit.

### 7. Code Editor (R2) — CHANGE package
- **Problem**: Monaco Editor loads giganting web workers, kills memory in grid.
- **Replace with**: CodeMirror 6 (@uiw/react-codemirror). Modular, lightweight,
  native JSON/YAML/TOML extensions, performs perfectly in grids.

### 8. Graph Auto-Layout (R13) — CHANGE package
- **Problem**: dagre not mathematically sound for nested dependencies.
- **Replace with**: @elkjs/elkjs (Eclipse Layout Kernel). Superior hierarchical
  algorithms, prevents edge crossings. Better for deployment → chain → model graphs.

### 9. Icons (R13) — CHANGE package
- **Problem**: react-icons bloats Next.js build time despite tree-shaking.
- **Replace with**: @iconify/react. Unifies all icon sets (Simple Icons, Lucide,
  FontAwesome) under one syntax. Loads on-demand as slim SVG paths at runtime.
  Near 100% bundle-size savings. Usage: `logos:docker`, `logos:python`, `logos:go`.

### 10. Port Detection (R11/R13) — CHANGE to event-driven
- **Problem**: Polling `ss -tlnp` / `docker ps` via SSH = unnecessary I/O overhead.
- **Replace with**: Docker Events API stream (cli.Events(ctx, ...)). Async,
  0% CPU idle. Container starts → JiMesh catches event → reads labels → registers.
  SSH polling only for initial discovery, events for ongoing updates.

### 11. SearXNG Scraping — ADD colly
- **Replace with**: github.com/gocolly/colly for structured SearXNG scraping.
  Utility model extraction with strict system prompt + JSON schema enforcement.

---

## 🟢 ADD (Critical gaps)

### 12. iFrame Pointer Capture Fix (R1) — ADD
- **Problem**: During grid resize/drag, mouse over iframe → iframe swallows events,
  drag breaks/stutters.
- **Fix**: Global CSS during dragging. Body attribute `data-dragging="true"`.
  CSS: `body[data-dragging="true"] iframe { pointer-events: none !important; }`

### 13. Secret Management — ADD AES-GCM-256
- **Problem**: API keys, SSH keys, DB passwords in plaintext PostgreSQL = security risk.
- **Fix**: AES-GCM-256 encryption layer in Go DB layer (pgx).
  Encrypt secrets at rest. Decrypt on read with server-side key.

### 14. Cost Circuit Breaker — ADD (CRITICAL)
- **Problem**: Infinite agent loop (failed JSON validation retry) = hundreds of dollars
  in minutes via API keys.
- **Fix**: Track cumulative token cost per WorkflowState in RAM.
  When limit exceeded (e.g. $0.50/run), emit context.Cancel() to all goroutines,
  break MCP connections, send SSE event: `cost_limit_exceeded`.

### 15. MoA Candidate Ranking — ADD
- **Paper**: arXiv:2406.04692 (Mixture of Agents). Pure synthesis → "Lost in the Middle".
- **Fix**: Before aggregation, experts score each other's outputs via logprob self-scoring.
  Only mathematically best snippets flow into final synthesis prompt.

### 16. Structured Output Validation — ADD
- **Fix**: Go struct → JSON type definitions at runtime. Unmarshal fails →
  self-correction loop (max 3 retries) with error stacktrace to LLM.

---

## 📦 UPDATED PACKAGE LIST

| Area | Old | New | Why |
|---|---|---|---|
| iFrame cache | HTTP/3 reverse proxy (quic-go) | Client-side hidden pool (CSS display:none) | Server can't reconstruct SPA state |
| Terminal | Custom xterm.js + Go SSH | ttyd sidecar container | Proven, stable, saves months |
| Browser automation | chromedp for everything | MCP tools for internal + chromedp for external | API > visual clicking |
| SSH tunnel | Custom golang.org/x/crypto/ssh dialer | chisel or wireguard-go | Avoid TCP-over-TCP meltdown |
| Entropy routing | Two-phase Shannon | RouteLLM classifier or speculative streaming | 10ms vs full generation waste |
| Fuzzy matching | Levenshtein | Jaro-Winkler + canonical ID normalization | Handles multi-provider prefixes |
| Code editor | Monaco | CodeMirror 6 (@uiw/react-codemirror) | Lightweight, grid-friendly |
| Graph layout | dagre (@dagrejs/dagre) | ELK (@elkjs/elkjs) | Mathematically superior for hierarchies |
| Icons | react-icons | @iconify/react | On-demand SVG, near-zero bundle size |
| Port discovery | SSH polling (ss -tlnp) | Docker Events API (cli.Events) | 0% CPU idle, event-driven |
| SearXNG | Raw HTTP | colly (gocolly/colly) | Structured scraping |
| MCP connectors | Custom | modelcontextprotocol/servers official repo | Pre-built Docker images, don't reinvent |
| Routing reference | Custom entropy | lm-sys/RouteLLM | Industry standard |
| Structured output | Manual JSON parse | Go struct → JSON schema + self-correction | Type-safe, auto-retry |

---

## NEW: Papers to Reference

| Paper | arXiv | Topic |
|---|---|---|
| FrugalGPT | 2406.04692 | LLM cascading math foundation |
| Mixture of Agents | 2406.04692 | MoA candidate ranking |
| RouteLLM | (lm-sys/RouteLLM) | Pre-inference routing classifiers |
| Speculative Decoding | 2211.17192 | Mid-flight stream cancellation |
| Orchestration | 2601.13671 | MCP protocol foundation |
| Pointer Capture | 2604.03208 | iFrame drag problem |

---

## BUILD PRIORITY (Updated)

1. **Cost Circuit Breaker** — CRITICAL safety, protects API keys
2. **Docker Event Stream Listener** — async auto-discovery, no polling
3. **Client-side iFrame Hidden Pool** — replace HTTP/3 cache (simpler, better)
4. **AES-GCM-256 Secret Management** — encrypt secrets at rest
5. **iFrame Pointer Capture Fix** — CSS fix for drag/resize
6. **MCP Server (mcp-go)** — expose JiMesh API as structured tools
7. **Docker MCP Connectors** — use modelcontextprotocol/servers
8. **CodeMirror 6 Editor** — replace Monaco plans
9. **ELK Auto-Layout** — replace dagre
10. **Iconify Icons** — replace react-icons
11. **Jaro-Winkler Matching** — replace Levenshtein
12. **ttyd Sidecar** — replace custom terminal
13. **chisel Tunnel** — replace custom SSH dialer
14. **RouteLLM/Speculative Streaming** — replace two-phase entropy
