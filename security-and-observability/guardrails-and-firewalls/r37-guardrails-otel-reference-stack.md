---
okf_version: "1.0"
id: "okf-sec-gua-r37-guardrails-otel-reference-stack"
title: "R37 — Guardrails, OpenTelemetry & OSS-Referenz-Stack (Lizenz-Fundstellen)"
topic: "security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - security-and-observability
  - guardrails-and-firewalls
summary: "**Quelle:** Operator 13.9.2026 („Guardrails + OTel implementieren falls es"
---

# R37 — Guardrails, OpenTelemetry & OSS-Referenz-Stack (Lizenz-Fundstellen)

**Quelle:** Operator 13.9.2026 („Guardrails + OTel implementieren falls es
sich lohnt, alles auschecken, alles im research folder dokumentieren").
Alle Lizenzen live verifiziert (GitHub-API / raw LICENSE, 13.9.2026).

## 1. Guardrails-Frameworks — alle Python, Enforcement bleibt at uns in Go

| Framework | Lizenz (verifiziert) | Sprache | Verdict for OpenMesh |
|---|---|---|---|
| Guardrails AI (`guardrails-ai/guardrails`) | Apache-2.0, 7.4k★ | **Python** (pip-only) | Referenz for Policy-/RAIL-Spec-Muster. **Nicht einbettbar** (unser Router ist Go). Validators-Konzepte → Übersetzung in unsere egress/OPA-Regeln + Llama-Guard-Pfad. |
| NeMo Guardrails (`NVIDIA/NeMo-Guardrails`) | Apache-2.0 (README-Badge verifiziert; LICENSE-Pfad 404) | **Python** (Colang) | Enterprise-Referenz for „programmierbare Leitplanken". Gleiche Logik: Konzepte übernehmen, Enforcement = unser Go-Router + OPA. |
| Llama Guard (Meta) | Modell (Weights-Lizenz) | via NIM/Self-Host | **Schon entschieden** (K-LAF-ARCHITECTURE.md:211): geroutetes Guard-Modell about den Proxy — „security scanning gets failover for free". Kein neues Research. |

**Conclusion:** Kein Python-Sidecar einführen (Mandat 7). Enforcement-Layer:
Go-Regeln (Egress/OPA) + geroutetes Llama Guard. Die Frameworks dienen
nur als Policy-Vokabular-Referenz.

## 2. OpenTelemetry — lohnt, with einer Nuance

- **`opentelemetry-go`:** Apache-2.0, **pure Go** → Mandat-7-kompatibel. ✅
- **gen_ai semconv:** existiert and ist aktiv — **umgezogen** in
  `open-telemetry/semantic-conventions-genai` (main-Repo verweist dorthin,
  verifiziert). Attribute verifiziert: `gen_ai.operation.name` (chat/
  generate_content/text_completion), `gen_ai.request.model`,
  `gen_ai.prompt.name/version`, `gen_ai.usage.{input,output}_tokens`,
  Cache-Audio-Varianten. **Status „Development"** (Badge je Attribut) —
  Feldnamen ausreichend stabil zum Übernehmen, Version im Schema pinnen
  and Change-Note im SDK.
- **Bestehende Infra:** `internal/tracing` (Sprint 7) exportiert seit langem
  after **Langfuse** (fire-and-forget, Session-Gruppierung about sessionId).
- **Langfuse v3 akzeptiert OTLP** (verifiziert: Otel-Collector-Beispiel with
  gRPC :4317) **and** „accepts incomplete or non-standard OTLP spans" with
  `langfuse.observation.type` inkl. **`guardrail`**, `tool`, `agent`,
  `retriever` — d.h. **Guardrail-Events sind in Langfuse first-class
  observable.** Phoenix-UI-Bedarf sinkt damit weiter.

**Entscheidung (WP5):** Logger-SDK v1 = eigenes kompaktes Schema with
**gen_ai.*-Feldnamen** (OTel-kompatibel, without SDK-Zwang) + optionaler
OTLP-Export-Pfad (`opentelemetry-go`, pure Go) → Langfuse/OTLP-Endpunkt.
Ein Schema, drei Konsumenten (unser Ring, Langfuse, zukünftige
Enterprise-Tools).

## 3. Phoenix (Arize) — Elastic License 2.0, nur Referenz

Verifiziert: LICENSE = **Elastic License 2.0 (ELv2)** — restriktiv
(no Managed-Service-Anbieten, no Umgehung der Limits). Für
Kommerzialisierung (PolyForm-NC-Kunden-Deployments) **not einbetten**.
Als UI/UX-Referenz for den Agents-Tab ansehen; optionaler Kunden-
selbstinstall-Container ist möglich, aber Langfuse (unsere bestehende
Wahl, MIT) deckt das ab.

## 4. MCP-Go-SDKs — zwei Kandidaten, beide nutzbar

| SDK | Lizenz (verifiziert) | Stars | Hinweis |
|---|---|---|---|
| `modelcontextprotocol/go-sdk` (offiziell) | **MIT → Apache-2.0 Transition** (LICENSE-Header verifiziert; neuer Code Apache-2.0) | 5.1k | Offiziell, Zukunftssicher — **Empfehlung for WP4.** |
| `mark3labs/mcp-go` | MIT, 9.1k★ | Community | Reifer API-Surface, viele Beispiele („Awesome MCP Servers" als Server-Blueprints). |

Fallback-Strategie: Beide sind MIT/Apache-kompatibel — WP4 startet with
dem offiziellen SDK, weicht at API-Lücken on mark3labs from.

## 5. DB-Router-Referenzen — Referenz-Only (Lizenzen)

- **ProxySQL** (`sysown/proxysql`): **GPL-3.0** ❌ no Code. L7-Parsing-
  Muster-Referenz (MySQL-fokussiert; for Postgres haben wir pgproto3, s. Sprint 36 §2b).
- **Benthos / Redpanda Connect** (`redpanda-data/connect`): **Dual-Lizenz** —
  `licenses/Apache-2.0.txt` for Core + `licenses/rcl.md` (**Redpanda
  Community License**, verifiziert) for Enterprise-Teile; `internal/license/`
  im Tree. **Verdict:** Muster-Referenz (Inputs/Processors/Outputs-Pipeline
  for die Router-Config), **not als Library einbetten** — ein kompletter
  Stream-Prozessor ist Overkill for einen Alias-Router.
- **Heimdall Data:** kommerziell — nur als Architecture-Referenz nennen.

## 6. Debezium-Envelope (vom Operator bestätigt, Fundstelle ergänzt)

Standard-Envelope: `schema` + `payload` with `before` / `after` /
`source` / `op` / `ts_ms` (docs: debezium-server + connector-docs).
Router-Endpoint `/cdc` liest `payload.after` (+ `op` for
Insert/Update/Delete-Anzeige) — wie im Sprint 36 §WP3 geplant.
