---
id: "R38"
title: "R38 — CDC final: geschichtete Synthese (v1 inline + Enterprise Hub-and-Spoke)"
type: research
date: 2026-09-12
status: final
tags: [cdc, mesh, redis, pglogrepl, mcp]
license: CC-BY-4.0
---

# R38 — CDC final: geschichtete Synthese (v1 inline + Enterprise Hub-and-Spoke)

**Quelle:** Operator 13.9.2026 („ohne Debezium geht uns einiges verloren…
warum kann man Debezium nicht einfach einmal deployen und einen smarten
kleinen Router auf die Worker Nodes?"). Gemini-Final bewertet und
synthetisiert — der Operator-Vorschlag ist architekturrecht, die
Gemini-Schlussfolgerung („strikke pglogrepl") überkorrigiert.

## 1. Die Entscheidung: DREI Schichten, nicht entweder/oder

| Schicht | Was | Läuft wo | Scope |
|---|---|---|---|
| **Stufe 2 — L7-Router (inline)** | pgproto3 (Postgres) + RESP-Parser (Redis) — 100 %-Abdeckung inkl. SELECTs, Query-Auditing | Go-Router auf dem SSH-Target (pure-Go, Mandat-7-klar) | **v1-Kern** (Postgres + Redis) |
| **Stufe 3a — CDC in-process** | pglogrepl (pure-Go) für Postgres-Change-Events (before/after, op-Typen) — null Extra-Infra | gleicher Go-Router, in-process | **v1 optional** — wenn Change-Semantik statt Query-Auditing gebraucht wird |
| **Stufe 3b — Debezium-Hub (Enterprise)** | Zentraler Debezium-Server auf **unserer** Control-Plane als universelles CDC-Gateway für die NoSQL-Zoo (Mongo/Cassandra/Oracle/Spanner) | **SaaS-Infra (Hub)** — NIEMALS auf Kunden-Targets | **Enterprise-Add-on**, pro Bedarf deployed |

**Warum die Synthese und nicht Gemini-Strikte:** Der Hub deckt die
NoSQL-Zoo ab (Gemini-Recht), aber für v1 (Postgres+Redis) braucht man ihn
nicht — L7-Router + optionales pglogrepl decken v1 komplett pure-Go ab.
Der Hub ist die Enterprise-Schicht, nicht der v1-Ersatz.

## 2. KORREKTUR 1 — Router-als-Tunnel (das fehlende Puzzlestück)

Gemini glossed over: Kunden-DBs sind meist **nicht internet-exponiert**.
Der zentrale Debezium-Hub braucht trotzdem den Replikations-/Change-Stream-
Port der Kunden-DB. Lösung: **der Go-Router auf dem SSH-Target wird der
Tunnel** — er forwarded den DB-Port durch das JiMesh-Mesh (Nebula/
Headscale) zum Hub. Vorteile:
- **Outbound-only** vom Router (Firewall-Änderungen beim Kunden minimal —
  exakt das Muster aus WP2 Pull-Entscheidung)
- Hub bleibt zentral, keine JVM vor Ort, Mandat-7-intakt
- Der Router ist ohnehin da (Stufe 2) — der Tunnel ist ein Feature-Flag

## 3. KORREKTUR 2 — Auth-Präzision (standardwebhooks ≠ Debezium-Sink)

Debezium-Server-HTTP-Sink signiert **nicht** mit standardwebhooks-Headern
(native). Auth für Hub → /cdc-ingest: **Mesh + Service-Token** (oder mTLS).
standardwebhooks (HMAC webhook-id/timestamp/signature) gilt für **unsere
OUTBOUND** Webhook-Fanouts (JiMesh → Kunden-Endpoints), nicht für den
Debezium-Sink. Gemischt nur, wenn wir einen Signier-Wrapper an den Ingest
hängen — v1 nicht nötig.

## 4. Randbedingungen (unverändert, beide Wege)

- `wal_level = logical` auf der Kunden-Postgres für JEDE CDC (Hub oder
  inline pglogrepl) — dieselbe Anfrage an den Kunden. Verweigert → Stufe 2
  (L7-Router) deckt trotzdem 100 % inkl. SELECTs ab.
- Mongo-CDC braucht ein Replica Set (Change Streams) — Hub und
  mongo-go-driver gleichermaßen.
- Debezium-Go-Package existiert nicht (nur SMT-Go-PDK via TinyGo/WASM
  **innerhalb** der Java-Engine — verifiziert, 13.9.2026). Pure-Go-Referenz:
  Trendyol/go-pq-cdc-kafka (Postgres-Logical-Replication-Parser).

## 5. MCP-Flip akzeptiert (mark3labs)

Gemini wählte mark3labs/mcp-go (MIT) über das offizielle go-sdk (MIT→
Apache-Transition) — Begründung „offiziell hinkt hinterher" ist heute
faktisch richtig (API-Reife/Spez-Abdeckung). **WP4 startet mit mark3labs,
gepinnt**; offizielles SDK beobachten (Ökosystem driftet dahin). Beide
lizenziert sauber (R37 §4).

## 6. Damit final geschlossen (Research-Phase ENDE)

| Frage | Entscheidung | Quelle |
|---|---|---|
| Vector-Store | **pgvector + HNSW** (Persistenz in Postgres, Redis nur flüchtig) | Gemini-Final + R37 |
| CDC | **3 Schichten** (oben) | R38 (dieses Doc) |
| Agent-ACL | **Rego (in-process, 0 ms) zuerst**, OpenFGA im Hinterkopf bei schmerzhafter Kaskade | Gemini-Final |
| MCP-SDK | **mark3labs/mcp-go**, gepinnt | R38 §5 |
| Config-Push | **Pull** (Router initiiert, Service-Token, langlebiger Stream) | Gemini-Final |
| gen_ai-semconv | **Internes JiMesh-Struct + Mapping-Funktion**, OTel-Version gepinnt | Gemini-Final + R37 §2 |
| NoSQL-Streaming | v1: RESP-L7 + Mongo-via-Hub-später; Enterprise: Debezium-Hub | R38 |
