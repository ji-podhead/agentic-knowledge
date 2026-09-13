---
id: "R10"
title: "R10 — Model Stats Pipeline: Static Facts + Dynamic Parameters + Fuzzy Fallback"
type: research
date: 2026-09-06
status: final
tags: [searxng, llama, mesh, entropy]
license: CC-BY-4.0
---

# R10 — Model Stats Pipeline: Static Facts + Dynamic Parameters + Fuzzy Fallback

## Frage
Wie nutzen wir OpenRouter stats, künstliche analyse, und SearXNG als fallback
für model metadata? Wie kategorisieren wir static vs dynamic facts? Welche
pipeline enrichment brauchen wir?

## Recherche-Aufgaben

### 1. OpenRouter Stats (wir nutzen sie GAR NICHT aktuell)
- [ ] OpenRouter API:
  - `GET https://openrouter.ai/api/v1/models` — kostenlos, curl-able, liefert:
    - `id`, `name`, `context_length`, `pricing` (prompt/completion per token)
    - `top_provider` (name, context_length, max_completion_tokens)
    - `architecture` (modality, input_modalities, output_modalities, tokenizer)
    - `supported_parameters` (tools, temperature, top_p, stream, etc.)
  - Rate limit: 100 requests/minute (kostenlos)
- [ ] Was liefert OpenRouter das wir nicht haben?
  - Pricing data (input/output per token) — aktuell haben wir `input_price_per_m` + `output_price_per_m` aber nicht befüllt
  - Supported parameters (tools, vision, streaming, reasoning)
  - Modality info (text, image, audio input/output)
  - Context length from provider (nicht nur aus model card)
- [ ] Wie enrichten?
  - Periodischer fetch (cron im backend) → update models table
  - Oder on-demand: wenn user ein model im catalog sieht → fetch von openrouter
  - Caching in DB: `model_enrichment` table mit source + last_updated

### 2. Artificial Analysis (künstliche Analyse als Fallback)
- [ ] artificialanalysis.ai API:
  - Hat pricing, quality scores, speed benchmarks für viele models
  - API key nötig? Kostenlos? Rate limit?
  - Was liefert es: MMLU score, HumanEval score, throughput, latency, cost
- [ ] Integration:
  - User trägt API key in settings ein (optional)
  - Backend nutzt key für enrichment queries
  - Fallback: wenn kein key → skip artificial analysis, gehe zu searxng
- [ ] Was tun wenn artificial analysis + openrouter beide nix finden?

### 3. SearXNG als letzter Fallback
- [ ] SearXNG: self-hosted meta search engine
  - User hostet SearXNG instance (oder JiMesh bundled?)
  - `GET http://searxng:8080/search?q=meta-llama-3.1-8b-instruct+benchmark+pricing&format=json`
  - Liefert web results — utility model extrahiert facts daraus
- [ ] Pipeline:
  1. OpenRouter lookup (static facts)
  2. Artificial Analysis lookup (benchmarks, quality scores)
  3. Wenn beides nix: SearXNG search + utility model extraction
  4. Utility model prompt: "Extract model metadata from these search results: {results}"
  5. Output: structured JSON mit context_length, pricing, modality, etc.
- [ ] Fuzzy matching:
  - Wenn "meta/llama-3.1-8b-instruct" nicht gefunden → fuzzy search "llama 3.1 8b instruct"
  - Deduplication: gleiche model klasse (strip provider prefix, strip -free suffix)
  - SearXNG findet benchmarks für "llama 3.1 8b" auch wenn die exakte ID nicht matcht

### 4. Static Facts vs Dynamic Parameters
- [ ] **Static facts** (ändern sich selten):
  - context_length
  - modality (text, vision, audio)
  - tokenizer
  - supported_parameters (tools, stream, reasoning)
  - architecture (MoE, dense, etc.)
  - Pricing (ändert sich aber selten)
  - Sources: OpenRouter, Artificial Analysis, model card, SearXNG
- [ ] **Dynamic parameters** (ändern sich live):
  - TTFB (time to first byte) — gemessen im proxy
  - Throughput (tokens/s) — gemessen im proxy
  - Error rate — aus request_log
  - Quota remaining — aus response headers (x-ratelimit)
  - Latency — aus request_log
  - Availability — health check status
  - Cost today / this month — aus request_log
  - Sources: request_log, health checks, response headers
- [ ] **Semi-static** (ändern sich gelegentlich):
  - Quality scores (MMLU, HumanEval) — aus Artificial Analysis
  - Speed benchmarks — aus Artificial Analysis
  - Provider uptime — aus health checks (rolling window)

### 5. Enrichment Pipeline Architecture
```
Model im Catalog
    ↓
[1] OpenRouter Lookup (static facts: context, pricing, modality, params)
    ↓ found? → update model_enrichment
    ↓ not found?
[2] Artificial Analysis Lookup (benchmarks, quality scores)
    ↓ found? → update model_enrichment
    ↓ not found?
[3] SearXNG Search + Utility Model Extraction
    ↓ search "{model_name} benchmark pricing context length"
    ↓ utility model extracts structured JSON
    ↓ update model_enrichment
    ↓
[4] Dynamic Parameters (live, separate pipeline):
    ↓ TTFB, throughput, error rate from request_log
    ↓ quota from response headers
    ↓ health from periodic checks
    ↓
[5] Combined View:
    static_facts (enrichment) + dynamic_params (live) → model card
```

### 6. Utility Model für SearXNG Extraction
- [ ] Welches model?
  - `utility` role aus model role schemas (Sprint 13 WP0)
  - Schnell, cheap, instruction-tuned
  - Prompt: "Extract model metadata as JSON from these search results.
    Fields: context_length, input_price_per_m, output_price_per_m,
    supports_vision, supports_tools, modality, architecture."
  - Retry on invalid JSON
- [ ] Caching: extracted facts cached für 24h (semi-static)
- [ ] Cost tracking: utility model calls kosten tokens → log in request_log

### 7. Fuzzy Model Deduplication
- [ ] Problem: gleiche model klasse erscheint mehrfach (nvidia/llama-3.1-8b, meta/llama-3.1-8b)
- [ ] Lösung:
  - Group by base ID (strip provider prefix, strip -free suffix) — wie in UI schon gebaut
  - Enrichment: wenn ein provider enrichment hat → alle varianten der gleichen klasse bekommen es
  - SearXNG: sucht nach base name ("llama 3.1 8b") nicht nach full ID
  - Dedup flag: models die identische enrichment haben → als duplicates markieren

---

## Research Results (Operator-Provided)

### Fuzzy Matching Pipeline

```
[Incoming Model ID] ──► [Exact Match Check] ──(Not Found)──► [Fuzzy Match (Levenshtein)]
                                                                     │
                                                                 (No Match)
                                                                     ▼
[Final Clean Metadata] ◄── [Save & Cache] ◄── [Web Scraping] ◄── [Utility Model Search]
```

### Static Facts JSON

```json
{
  "model_id": "deepseek-ai/deepseek-v3",
  "display_name": "DeepSeek V3 (Base)",
  "context_window": 131072,
  "parameters_total": 671000000000,
  "parameters_active": 37000000000,
  "pricing": { "input_per_1k": 0.00014, "output_per_1k": 0.00028 }
}
```

### Dynamic Facts JSON

```json
{
  "model_id": "deepseek-ai/deepseek-v3",
  "provider": "openrouter",
  "live_stats": {
    "ttfb_ms": 142.5,
    "tokens_per_second": 85.2,
    "uptime_24h": 0.9994,
    "current_queue_depth": 3
  }
}
```

### Academic References (see `docs/REFERENCES.md`)
- MoA: arXiv:2406.04692
- Orchestration: arXiv:2601.13671
- Deterministic SLA: arXiv:2511.15755
- Speculative Decoding: arXiv:2211.17192
- Entropy Routing: arXiv:2605.22873
- Hierarchical Planning: arXiv:2604.03208
- NVIDIA Cosmos 3: research.nvidia.com/labs/cosmos-lab/cosmos3/

---

# R10 — Model Stats Pipeline: Static Facts + Dynamic Parameters + Fuzzy Fallback

## Frage
Wie nutzen wir OpenRouter stats, künstliche analyse, und SearXNG als fallback
für model metadata? Wie kategorisieren wir static vs dynamic facts? Welche
pipeline enrichment brauchen wir?

## Recherche-Aufgaben

### 1. OpenRouter Stats (wir nutzen sie GAR NICHT aktuell)
- [ ] OpenRouter API:
  - `GET https://openrouter.ai/api/v1/models` — kostenlos, curl-able, liefert:
    - `id`, `name`, `context_length`, `pricing` (prompt/completion per token)
    - `top_provider` (name, context_length, max_completion_tokens)
    - `architecture` (modality, input_modalities, output_modalities, tokenizer)
    - `supported_parameters` (tools, temperature, top_p, stream, etc.)
  - Rate limit: 100 requests/minute (kostenlos)
- [ ] Was liefert OpenRouter das wir nicht haben?
  - Pricing data (input/output per token) — aktuell haben wir `input_price_per_m` + `output_price_per_m` aber nicht befüllt
  - Supported parameters (tools, vision, streaming, reasoning)
  - Modality info (text, image, audio input/output)
  - Context length from provider (nicht nur aus model card)
- [ ] Wie enrichten?
  - Periodischer fetch (cron im backend) → update models table
  - Oder on-demand: wenn user ein model im catalog sieht → fetch von openrouter
  - Caching in DB: `model_enrichment` table mit source + last_updated

### 2. Artificial Analysis (künstliche Analyse als Fallback)
- [ ] artificialanalysis.ai API:
  - Hat pricing, quality scores, speed benchmarks für viele models
  - API key nötig? Kostenlos? Rate limit?
  - Was liefert es: MMLU score, HumanEval score, throughput, latency, cost
- [ ] Integration:
  - User trägt API key in settings ein (optional)
  - Backend nutzt key für enrichment queries
  - Fallback: wenn kein key → skip artificial analysis, gehe zu searxng
- [ ] Was tun wenn artificial analysis + openrouter beide nix finden?

### 3. SearXNG als letzter Fallback
- [ ] SearXNG: self-hosted meta search engine
  - User hostet SearXNG instance (oder JiMesh bundled?)
  - `GET http://searxng:8080/search?q=meta-llama-3.1-8b-instruct+benchmark+pricing&format=json`
  - Liefert web results — utility model extrahiert facts daraus
- [ ] Pipeline:
  1. OpenRouter lookup (static facts)
  2. Artificial Analysis lookup (benchmarks, quality scores)
  3. Wenn beides nix: SearXNG search + utility model extraction
  4. Utility model prompt: "Extract model metadata from these search results: {results}"
  5. Output: structured JSON mit context_length, pricing, modality, etc.
- [ ] Fuzzy matching:
  - Wenn "meta/llama-3.1-8b-instruct" nicht gefunden → fuzzy search "llama 3.1 8b instruct"
  - Deduplication: gleiche model klasse (strip provider prefix, strip -free suffix)
  - SearXNG findet benchmarks für "llama 3.1 8b" auch wenn die exakte ID nicht matcht

### 4. Static Facts vs Dynamic Parameters
- [ ] **Static facts** (ändern sich selten):
  - context_length
  - modality (text, vision, audio)
  - tokenizer
  - supported_parameters (tools, stream, reasoning)
  - architecture (MoE, dense, etc.)
  - Pricing (ändert sich aber selten)
  - Sources: OpenRouter, Artificial Analysis, model card, SearXNG
- [ ] **Dynamic parameters** (ändern sich live):
  - TTFB (time to first byte) — gemessen im proxy
  - Throughput (tokens/s) — gemessen im proxy
  - Error rate — aus request_log
  - Quota remaining — aus response headers (x-ratelimit)
  - Latency — aus request_log
  - Availability — health check status
  - Cost today / this month — aus request_log
  - Sources: request_log, health checks, response headers
- [ ] **Semi-static** (ändern sich gelegentlich):
  - Quality scores (MMLU, HumanEval) — aus Artificial Analysis
  - Speed benchmarks — aus Artificial Analysis
  - Provider uptime — aus health checks (rolling window)

### 5. Enrichment Pipeline Architecture
```
Model im Catalog
    ↓
[1] OpenRouter Lookup (static facts: context, pricing, modality, params)
    ↓ found? → update model_enrichment
    ↓ not found?
[2] Artificial Analysis Lookup (benchmarks, quality scores)
    ↓ found? → update model_enrichment
    ↓ not found?
[3] SearXNG Search + Utility Model Extraction
    ↓ search "{model_name} benchmark pricing context length"
    ↓ utility model extracts structured JSON
    ↓ update model_enrichment
    ↓
[4] Dynamic Parameters (live, separate pipeline):
    ↓ TTFB, throughput, error rate from request_log
    ↓ quota from response headers
    ↓ health from periodic checks
    ↓
[5] Combined View:
    static_facts (enrichment) + dynamic_params (live) → model card
```

### 6. Utility Model für SearXNG Extraction
- [ ] Welches model?
  - `utility` role aus model role schemas (Sprint 13 WP0)
  - Schnell, cheap, instruction-tuned
  - Prompt: "Extract model metadata as JSON from these search results.
    Fields: context_length, input_price_per_m, output_price_per_m,
    supports_vision, supports_tools, modality, architecture."
  - Retry on invalid JSON
- [ ] Caching: extracted facts cached für 24h (semi-static)
- [ ] Cost tracking: utility model calls kosten tokens → log in request_log

### 7. Fuzzy Model Deduplication
- [ ] Problem: gleiche model klasse erscheint mehrfach (nvidia/llama-3.1-8b, meta/llama-3.1-8b)
- [ ] Lösung:
  - Group by base ID (strip provider prefix, strip -free suffix) — wie in UI schon gebaut
  - Enrichment: wenn ein provider enrichment hat → alle varianten der gleichen klasse bekommen es
  - SearXNG: sucht nach base name ("llama 3.1 8b") nicht nach full ID
  - Dedup flag: models die identische enrichment haben → als duplicates markieren

---

## Research Results (Operator-Provided)

### Fuzzy Matching Pipeline

```
[Incoming Model ID] ──► [Exact Match Check] ──(Not Found)──► [Fuzzy Match (Levenshtein)]
                                                                     │
                                                                 (No Match)
                                                                     ▼
[Final Clean Metadata] ◄── [Save & Cache] ◄── [Web Scraping] ◄── [Utility Model Search]
```

### Static Facts JSON

```json
{
  "model_id": "deepseek-ai/deepseek-v3",
  "display_name": "DeepSeek V3 (Base)",
  "context_window": 131072,
  "parameters_total": 671000000000,
  "parameters_active": 37000000000,
  "pricing": { "input_per_1k": 0.00014, "output_per_1k": 0.00028 }
}
```

### Dynamic Facts JSON

```json
{
  "model_id": "deepseek-ai/deepseek-v3",
  "provider": "openrouter",
  "live_stats": {
    "ttfb_ms": 142.5,
    "tokens_per_second": 85.2,
    "uptime_24h": 0.9994,
    "current_queue_depth": 3
  }
}
```

### Academic References (see `docs/REFERENCES.md`)
- MoA: arXiv:2406.04692
- Orchestration: arXiv:2601.13671
- Deterministic SLA: arXiv:2511.15755
- Speculative Decoding: arXiv:2211.17192
- Entropy Routing: arXiv:2605.22873
- Hierarchical Planning: arXiv:2604.03208
- NVIDIA Cosmos 3: research.nvidia.com/labs/cosmos-lab/cosmos3/
