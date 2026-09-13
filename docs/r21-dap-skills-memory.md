---
id: "R21"
title: "R21 — DAP-Vorlage: Skills-Hub, Skill-Security & Memory"
type: research
date: 2026-09-07
status: final
tags: [mesh, opa, rbac, redis, mcp]
license: CC-BY-4.0
---

# R21 — DAP-Vorlage: Skills-Hub, Skill-Security & Memory

> **Status:** ✅ erledigt (6.9.2026) — Quell-Repo geklont und gelesen (48 Dateien, ~2.800 Zeilen Kernspezifikation)
> **Quelle:** https://github.com/ji-workstation/dap-docs (lokaler Klon: `/home/ji/projects/dap-docs`) — **DAP = Dynamic Agent Protocol**, Operator-eigene Spec
> **Wichtig (Ehrlichkeit):** Die DAP-Docs sind explizit **eine PRD / Design-Spec, kein Implementierungsstatus** („Nothing in this reference implies production readiness unless explicitly noted"). Alles unten ist Vorlagen-Material, nicht lauffähiger Code.
> **Anlass:** Operator-Lücke benannt (6.9.2026): JiMesh fehlt ein **Skills-Hub**, **Security für Skills** und **Memory** — DAP deckt alle drei als Spec ab.

## 1. Was DAP ist (3 Layer, sauber getrennt)

| Layer | Name | Rolle |
|---|---|---|
| **Protocol** | DAP | Offener Standard: Tool-Discovery + -Invocation (gRPC `DiscoverTools`/`InvokeTool`/`SearchTools`), Skill-System (Score 0–100, Gates, Artifacts), Proof-Familie (PoT/PoS/PoD), Workflows (`llm`/`rag`/`script`/`crew`/`subagent`/`guardrail`), `tool_call_log` |
| **Network** | DAPNet | Infrastruktur: MQTT (EMQX, QoS, Last Will), SurrealDB, Qdrant |
| **Operator** | DAPCom | Backbone-Betreiber (per-message fees) |

Apps darauf: SurrealLife (Game-Layer!), DAP IDE. **Achtung:** Game-Mechaniken (Careers, SurrealCoin, Boss-Endorsements, Contraband, Company-Inheritance) sind SurrealLife-only — `dap-games.md` trennt das sauber und ist für JiMesh die Ignore-Liste.

## 2. Kernbefunde je Lücke

### 2.1 Skills-Hub — `skills.md`, `tool-skill-binding.md`

* Skill = **public/** (Score 0–100 **abgeleitet, nie direkt geschrieben**, Level, Certifications) + **private/** (Artifacts, Memories, Performance-Log, Strategien — nur Agent + aktueller Arbeitgeber)
* Score-Derivation aus Proof-of-Thought-Qualität: `new = old + (quality − 0.5) × learning_rate`, Decay pro Idle-Tag
* Adaptive Mechanismen statt Score-Override: konfigurierbare Learning-Rate pro Dimension, **Regime-Shift-Signal** (Agent meldet selbst, wenn Artifacts nicht mehr greifen → alte werden `stale` gerankt, Rate temporär erhöht), Operator-Override nur audit-logged (`skill_audit_log`)
* **Tool–Skill-Binding (geschlossener Loop):** Tools hinter Skill-Schwellen (`skill_min` — darunter **unsichtbar**, nicht nur gesperrt), erfolgreiche Calls geben `skill_gain` zurück; Multi-Skill-Bindings mit Gewichten; `produces_artifact` → Artifacts werden selbst RAG-Kollektion
* Bloat-Score wird bei Registrierung automatisch berechnet (description/schema/artifact tokens) — passt zu JiMesh' Lean-Doktrin

### 2.2 Skill-Security — `acl.md`, `store-permissions.md`

> **Update 7.9.2026:** Die "eine Engine, nicht zwei"-Entscheidung (§6 Punkt
> 4 unten) ist gefallen — **OPA**, nicht Casbin, siehe `DECISIONS.md`
> ("E-Policy — Policy-Engine: OPA"). Layer 1 unten bleibt als historisches
> Rechercheergebnis stehen (zeigt den DAP-Vorbild-Stand), jede Umsetzung
> nutzt aber OPA/Rego statt Casbin für die Protocol/App-ACL.

* **3-Layer-ACL-Stack** (jeder Layer deckt eine andere Enforcement-Fläche, „keiner ersetzt den anderen"):
  1. **Casbin** — Protocol/App-ACL (keyMatch2), ein Policy-Store für gRPC-Tool-Calls + MQTT-Topics + Daten-Namespaces; globale `deny`-Liste für Forbidden-Tools (z. B. `audit_log_delete`, `agent_identity_transfer`) — Checks **vor** Handler-Ausführung
  2. **SurrealDB-RBAC** — Row-Level via `PERMISSIONS FOR select WHERE $auth...` + Record-Users als Agent-Identität
  3. **Capabilities-Härtung** — `--deny-arbitrary-query=record` (Agents senden kein freies SurrealQL, nur `DEFINE API`-Endpoints), `--allow-net` auf interne Dienste limitiert, `--deny-scripting`
* **5 Store-Access-Levels** für autonome Skill-Installation: NONE (unsichtbar) / READ_ONLY (browsen) / **GUARDED (jede Installation in menschliche Approval-Queue — Agent hängt eine Reason an, User bewertet Intention)** / **SCOPED (autonom innerhalb YAML-Grenzen: max_cost_per_day, allowed/blocked skill domains, vendor_tier_minimum, require_review_for ab Skill-Score, notify_on_install)** / FULL
* Skill-only-Installs als eigene Granularität (Artifacts ja, Tool-Code nein)
* Passgenau zur saits-cloud-RBAC-Kette aus TASK-003 (Claim → Middleware → OPA → Labels → Egress): Casbin ≈ OPA auf der Protocol-Ebene

### 2.3 Memory — `crew-memory.md`, `rag.md`

* CrewAI-Mitglieder backed by echte Agent-Records: Init lädt Memories (HNSW-Cosine) + Top-Skill-Artifacts + baut **dynamische Backstory** (Jinja-Template aus realen Erfahrungen); nach dem Kickoff schreiben alle Members Memories mit `quality_score` + Embedding zurück
* `SurrealMemoryBackend` implementiert CrewAIs Memory-Interface (save/search direkt auf die Agent-Collection)
* **RAG als Workflow-Phase (`type: rag`), nicht als Tool-Call:** hartes Token-Budget (`max_tokens: 400` vs. ~1.500 beim rohen MCP-Chunk-Dump), `summarize: true`, `access_filter: auto`, `persist_links: true` (Graph-Links → „was habe ich dazu schon gefunden" ohne Re-Search)
* **Skill-Artifacts als RAG-Kollektion:** High-Skill-Agent bekommt eigene bewährte Strategien mit-injiziert, Low-Skill-Agent nur Web-Chunks
* 4-Layer-Access-Control „zero extra code": Capabilities → PERMISSIONS → HNSW-Filter → Casbin
* Storage-Inkonsistenz ehrlich notiert: DAPNet-Liste nennt Qdrant, `rag.md` sagt „SurrealDB HNSW — kein separates Qdrant nötig" (zwei Antworten in der Spec)

### 2.4 Bonus: Tool-Registry — `tool-registration.md` (Sprint 17/18 direkt)

* YAML-Tool-Definition mit `acl_path`/`acl_action`/`allowed_roles`/`skill_required`/`skill_min`/`skill_gain`/`bloat_score` (auto)/`a2a`
* 8 Handler-Typen: `workflow` (versioniertes YAML) / `builtin` / `surreal_query` (file-drop, read-only) / `notebook` (sandboxed subprocess) / `proof` (Z3-verifizierte PoS-Pipeline) / `a2a` / `subagent` / `crew`

## 3. Verwertung für JiMesh (Mapping)

| DAP-Konzept | JiMesh-Anwendung | Wo (Epic) | Aufwand |
|---|---|---|---|
| Skill-Modell (public/private, Score aus Qualitäts-Feedback, Decay, Regime-Shift) | Agenten-Qualitätsscore pro Dimension statt flachem Rating; DECISIONS-Regel: Score nie direkt schreiben | Epic 18 / Sprint 17/18 | M |
| Tool–Skill-Binding (`skill_min` unsichtbar, `skill_gain`-Loop) | Agent-Tool-Registry: Tools nach Agent-Qualität freischalten | Sprint 17/18 WP4 | S |
| 5 Store-Levels (GUARDED-Approval-Queue mit Agent-Reason) | WP3 Freeze/Release + Tool-Install-Genehmigung als HITL-Gate | Epic 18 + WP3 | S–M |
| SCOPED-Constraints-YAML (Kosten/Tag, Domain-Allow/Deny, Vendor-Tier) | Agent-Policy-Format (ergänzt Access Policy §2) | Epic 12/17 | S |
| 3-Layer-ACL (Policy-Engine + Row-Level + Endpoint-Härtung) | Saits-Kette (TASK-003) um die Capabilities-Härtung ergänzen | Epic 17, WP5 | M |
| SurrealMemoryBackend / dynamische Backstory / Write-back mit quality_score | Multi-Agent-Orchestrierung mit persistentem Memory (JiMesh: Postgres+pgvector statt SurrealDB?) | Epic 18 / Sprint 14 | M |
| RAG als Workflow-Phase (Budget 400, summarize, persist_links, access_filter) | JiMesh-RAG: Budget-Cap statt Chunk-Dump, Skill-Artifacts als Kollektion | Epic 18 | M |
| Bloat-Score bei Registrierung | Tool-/Skill-Registry: automatische Schlankheits-Metrik | Sprint 17/18 | S |
| Proof-Familie PoT/PoS/PoD | PoT = quality_score-Quelle fürs Skill-Modell; PoS = Claim-Check | Epic 18 / SCHEMA-model-evaluation | M |

## 4. Nicht übernehmen / ehrliche Grenzen

* SurrealLife-Game-Layer (Endorsements, SurrealCoin, Contraband, Careers) — laut dap-games.md bewusst getrennt
* DAPCom-Abrechnungsmodell — JiMesh-Credits bleiben Darstellungsschicht (Roadmap §4)
* **Implementierungsstatus = PRD.** Vor jeder Übernahme: Vector-Store-Entscheidung (JiMesh-Stack hat Redis ohne Stack-Module; pgvector wäre der pgx-Weg; DAP schwankt Qdrant vs. SurrealDB-HNSW)

## 5. Querverweise

* TASK-002/003/004 (saits-Review): DPoP-Replay-Guard, RBAC-Kette, Tool-Schemas, RolesWidget
* `docs/SCHEMA-model-evaluation.md` — PoT-quality_score als Eval-Quelle
* `docs/PRODUCT-ROADMAP.md` §8 (Utility-Layer), Sprint 17/18 (MCP/Registry), Epic 17 (Admin-Layer)
* DAP-Vision im Bestand: `st-2/docs/DAP_VISION.md` (selbes Konzept aus der Trading-Welt)

## 6. Offene Punkte

1. Vector-Store-Entscheidung für Skills/Memory: pgvector (pgx-Weg) vs. Redis-Stack (sc-ai-Muster) vs. Qdrant (DAPNet) — blockiert Epic 18 WP1
2. Skill-Dimensionen für JiMesh definieren (coding, deploy, security, research?) + Score-Quelle (WP2-Scanner-Verdict? PoT-Qualität? USER-Ratings?)
3. GUARDED-Approval-Queue: UI auf der Admin-Seite (Epic 17) oder als Escalation-Inbox (TASK-003-Muster)?
4. ~~Casbin vs. OPA~~ — **entschieden 7.9.2026: OPA** (`DECISIONS.md`
   "E-Policy — Policy-Engine: OPA"), gilt für diesen Layer 1 UND das
   Admin/RBAC-UI (SPRINT-22 WP4) — eine Engine, nicht zwei.
5. Nimmt JiMesh DAP als Protokoll-Basis (nur Spec-Teile, sauber getrennt vom Game-Layer) oder nur als Muster-Referenz?
