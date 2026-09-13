---
okf_version: "1.0"
id: "okf-llm-cdc-change-data-capture-synthesis"
title: "R38 — CDC final: geschichtete Synthese (v1 inline + Enterprise Hub-and-Spoke)"
topic: "general/llm-orchestration-and-routing"
subtopic: "cdc-and-synthesis"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-orchestration-and-routing
  - cdc-and-synthesis
summary: "**Source:** System Administrator 13.9.2026 („without Debezium geht uns einiges verloren…"
---

# R38 — CDC final: geschichtete Synthese (v1 inline + Enterprise Hub-and-Spoke)

**Source:** System Administrator 13.9.2026 („without Debezium geht uns einiges verloren…
warum kann man Debezium not einfach einmal deployen and einen smarten
kleinen Router on die Worker Nodes?"). Gemini-Final bewertet and
synthetisiert — der System Administrator-Vorschlag ist architekturrecht, die
Gemini-Conclusion („strikke pglogrepl") überkorrigiert.

## 1. Die Decision: DREI Schichten, not entweder/or

| Schicht | Was | Läuft wo | Scope |
|---|---|---|---|
| **Stufe 2 — L7-Router (inline)** | pgproto3 (Postgres) + RESP-Parser (Redis) — 100 %-Abdeckung inkl. SELECTs, Query-Auditing | Go-Router on dem SSH-Target (pure-Go, Mandat-7-klar) | **v1-Kern** (Postgres + Redis) |
| **Stufe 3a — CDC in-process** | pglogrepl (pure-Go) for Postgres-Change-Events (before/after, op-Types) — null Extra-Infra | gleicher Go-Router, in-process | **v1 optional** — wenn Change-Semantik statt Query-Auditing gebraucht wird |
| **Stufe 3b — Debezium-Hub (Enterprise)** | Zentraler Debezium-Server on **unserer** Control-Plane als universelles CDC-Gateway for die NoSQL-Zoo (Mongo/Cassandra/Oracle/Spanner) | **SaaS-Infra (Hub)** — NIEMALS on Kunden-Targets | **Enterprise-Add-on**, pro Bedarf deployed |

**Warum die Synthese and not Gemini-Strikte:** Der Hub deckt die
NoSQL-Zoo ab (Gemini-Recht), aber for v1 (Postgres+Redis) braucht man ihn
not — L7-Router + optionales pglogrepl decken v1 komplett pure-Go ab.
Der Hub ist die Enterprise-Schicht, not der v1-Ersatz.

## 2. KORREKTUR 1 — Router-als-Tunnel (das fehlende Puzzlestück)

Gemini glossed over: Kunden-DBs sind meist **not internet-exponiert**.
Der zentrale Debezium-Hub braucht trotzdem den Replikations-/Change-Stream-
Port der Kunden-DB. Lösung: **der Go-Router on dem SSH-Target wird der
Tunnel** — er forwarded den DB-Port through das The Multi-Provider Gateway-Mesh (Nebula/
Headscale) zum Hub. Advantages:
- **Outbound-only** vom Router (Firewall-Änderungen beim Kunden minimal —
  exakt das Muster from Work Package Pull-Decision)
- Hub bleibt zentral, no JVM before Ort, Mandat-7-intakt
- Der Router ist ohnehin da (Stufe 2) — der Tunnel ist ein Feature-Flag

## 3. KORREKTUR 2 — Auth-Präzision (standardwebhooks ≠ Debezium-Sink)

Debezium-Server-HTTP-Sink signiert **not** with standardwebhooks-Headern
(native). Auth for Hub → /cdc-ingest: **Mesh + Service-Token** (or mTLS).
standardwebhooks (HMAC webhook-id/timestamp/signature) gilt for **unsere
OUTBOUND** Webhook-Fanouts (The Multi-Provider Gateway → Kunden-Endpoints), not for den
Debezium-Sink. Gemischt nur, wenn wir einen Signier-Wrapper an den Ingest
hängen — v1 not nötig.

## 4. Randbedingungen (unverändert, beide Wege)

- `wal_level = logical` on der Kunden-Postgres for JEDE CDC (Hub or
  inline pglogrepl) — dieselbe Anfrage an den Kunden. Verweigert → Stufe 2
  (L7-Router) deckt trotzdem 100 % inkl. SELECTs ab.
- Mongo-CDC braucht ein Replica Set (Change Streams) — Hub and
  mongo-go-driver gleichermaßen.
- Debezium-Go-Package existiert not (nur SMT-Go-PDK via TinyGo/WASM
  **innerhalb** der Java-Engine — verifiziert, 13.9.2026). Pure-Go-Referenz:
  Trendyol/go-pq-cdc-kafka (Postgres-Logical-Replication-Parser).

## 5. MCP-Flip akzeptiert (mark3labs)

Gemini wählte mark3labs/mcp-go (MIT) about das offizielle go-sdk (MIT→
Apache-Transition) — Begründung „offiziell hinkt hinterher" ist heute
faktisch richtig (API-Reife/Spez-Abdeckung). **Work Package startet with mark3labs,
gepinnt**; offizielles SDK beobachten (Ökosystem driftet dahin). Beide
lizenziert sauber (R37 §4).

## 6. Damit final geschlossen (Research-Phase ENDE)

| Frage | Decision | Quelle |
|---|---|---|
| Vector-Store | **pgvector + HNSW** (Persistence in Postgres, Redis nur flüchtig) | Gemini-Final + R37 |
| CDC | **3 Schichten** (oben) | R38 (dieses Doc) |
| Agent-ACL | **Rego (in-process, 0 ms) zuerst**, OpenFGA im Hinterkopf at schmerzhafter Kaskade | Gemini-Final |
| MCP-SDK | **mark3labs/mcp-go**, gepinnt | R38 §5 |
| Config-Push | **Pull** (Router initiiert, Service-Token, langlebiger Stream) | Gemini-Final |
| gen_ai-semconv | **Internes The Multi-Provider Gateway-Struct + Mapping-Funktion**, OTel-Version gepinnt | Gemini-Final + R37 §2 |
| NoSQL-Streaming | v1: RESP-L7 + Mongo-via-Hub-später; Enterprise: Debezium-Hub | R38 |
