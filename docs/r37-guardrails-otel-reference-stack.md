---
id: "R37"
title: "R37 — Guardrails, OpenTelemetry & OSS-Referenz-Stack (Lizenz-Fundstellen)"
type: research
date: 2026-09-12
status: final
tags: [guardrail, opa, mcp, llama, mesh]
license: CC-BY-4.0
---

# R37 — Guardrails, OpenTelemetry & OSS-Referenz-Stack (Lizenz-Fundstellen)

**Quelle:** Operator 13.9.2026 („Guardrails + OTel implementieren falls es
sich lohnt, alles auschecken, alles im research folder dokumentieren").
Alle Lizenzen live verifiziert (GitHub-API / raw LICENSE, 13.9.2026).

## 1. Guardrails-Frameworks — alle Python, Enforcement bleibt bei uns in Go

| Framework | Lizenz (verifiziert) | Sprache | Verdict für JiMesh |
|---|---|---|---|
| Guardrails AI (`guardrails-ai/guardrails`) | Apache-2.0, 7.4k★ | **Python** (pip-only) | Referenz für Policy-/RAIL-Spec-Muster. **Nicht einbettbar** (unser Router ist Go). Validators-Konzepte → Übersetzung in unsere egress/OPA-Regeln + Llama-Guard-Pfad. |
| NeMo Guardrails (`NVIDIA/NeMo-Guardrails`) | Apache-2.0 (README-Badge verifiziert; LICENSE-Pfad 404) | **Python** (Colang) | Enterprise-Referenz für „programmierbare Leitplanken". Gleiche Logik: Konzepte übernehmen, Enforcement = unser Go-Router + OPA. |
| Llama Guard (Meta) | Modell (Weights-Lizenz) | via NIM/Self-Host | **Schon entschieden** (K-LAF-ARCHITECTURE.md:211): geroutetes Guard-Modell über den Proxy — „security scanning gets failover for free". Kein neues Research. |

**Fazit:** Kein Python-Sidecar einführen (Mandat 7). Enforcement-Layer:
Go-Regeln (Egress/OPA) + geroutetes Llama Guard. Die Frameworks dienen
nur als Policy-Vokabular-Referenz.

## 2. OpenTelemetry — lohnt, mit einer Nuance

- **`opentelemetry-go`:** Apache-2.0, **pure Go** → Mandat-7-kompatibel. ✅
- **gen_ai semconv:** existiert und ist aktiv — **umgezogen** in
  `open-telemetry/semantic-conventions-genai` (main-Repo verweist dorthin,
  verifiziert). Attribute verifiziert: `gen_ai.operation.name` (chat/
  generate_content/text_completion), `gen_ai.request.model`,
  `gen_ai.prompt.name/version`, `gen_ai.usage.{input,output}_tokens`,
  Cache-Audio-Varianten. **Status „Development"** (Badge je Attribut) —
  Feldnamen ausreichend stabil zum Übernehmen, Version im Schema pinnen
  und Change-Note im SDK.
- **Bestehende Infra:** `internal/tracing` (Sprint 7) exportiert seit langem
  nach **Langfuse** (fire-and-forget, Session-Gruppierung über sessionId).
- **Langfuse v3 akzeptiert OTLP** (verifiziert: Otel-Collector-Beispiel mit
  gRPC :4317) **und** „accepts incomplete or non-standard OTLP spans" mit
  `langfuse.observation.type` inkl. **`guardrail`**, `tool`, `agent`,
  `retriever` — d.h. **Guardrail-Events sind in Langfuse first-class
  observable.** Phoenix-UI-Bedarf sinkt damit weiter.

**Entscheidung (WP5):** Logger-SDK v1 = eigenes kompaktes Schema mit
**gen_ai.*-Feldnamen** (OTel-kompatibel, ohne SDK-Zwang) + optionaler
OTLP-Export-Pfad (`opentelemetry-go`, pure Go) → Langfuse/OTLP-Endpunkt.
Ein Schema, drei Konsumenten (unser Ring, Langfuse, zukünftige
Enterprise-Tools).

## 3. Phoenix (Arize) — Elastic License 2.0, nur Referenz

Verifiziert: LICENSE = **Elastic License 2.0 (ELv2)** — restriktiv
(kein Managed-Service-Anbieten, keine Umgehung der Limits). Für
Kommerzialisierung (PolyForm-NC-Kunden-Deployments) **nicht einbetten**.
Als UI/UX-Referenz für den Agents-Tab ansehen; optionaler Kunden-
selbstinstall-Container ist möglich, aber Langfuse (unsere bestehende
Wahl, MIT) deckt das ab.

## 4. MCP-Go-SDKs — zwei Kandidaten, beide nutzbar

| SDK | Lizenz (verifiziert) | Stars | Hinweis |
|---|---|---|---|
| `modelcontextprotocol/go-sdk` (offiziell) | **MIT → Apache-2.0 Transition** (LICENSE-Header verifiziert; neuer Code Apache-2.0) | 5.1k | Offiziell, Zukunftssicher — **Empfehlung für WP4.** |
| `mark3labs/mcp-go` | MIT, 9.1k★ | Community | Reifer API-Surface, viele Beispiele („Awesome MCP Servers" als Server-Blueprints). |

Fallback-Strategie: Beide sind MIT/Apache-kompatibel — WP4 startet mit
dem offiziellen SDK, weicht bei API-Lücken auf mark3labs aus.

## 5. DB-Router-Referenzen — Referenz-Only (Lizenzen)

- **ProxySQL** (`sysown/proxysql`): **GPL-3.0** ❌ kein Code. L7-Parsing-
  Muster-Referenz (MySQL-fokussiert; für Postgres haben wir pgproto3, s. Sprint 36 §2b).
- **Benthos / Redpanda Connect** (`redpanda-data/connect`): **Dual-Lizenz** —
  `licenses/Apache-2.0.txt` für Core + `licenses/rcl.md` (**Redpanda
  Community License**, verifiziert) für Enterprise-Teile; `internal/license/`
  im Tree. **Verdict:** Muster-Referenz (Inputs/Processors/Outputs-Pipeline
  für die Router-Config), **nicht als Library einbetten** — ein kompletter
  Stream-Prozessor ist Overkill für einen Alias-Router.
- **Heimdall Data:** kommerziell — nur als Architektur-Referenz nennen.

## 6. Debezium-Envelope (vom Operator bestätigt, Fundstelle ergänzt)

Standard-Envelope: `schema` + `payload` mit `before` / `after` /
`source` / `op` / `ts_ms` (docs: debezium-server + connector-docs).
Router-Endpoint `/cdc` liest `payload.after` (+ `op` für
Insert/Update/Delete-Anzeige) — wie im Sprint 36 §WP3 geplant.
