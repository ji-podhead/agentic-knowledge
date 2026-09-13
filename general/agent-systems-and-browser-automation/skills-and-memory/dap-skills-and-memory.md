---
okf_version: "1.0"
id: "okf-age-ski-dap-skills-and-memory"
title: "R21 — DAP-Vorlage: Skills-Hub, Skill-Security & Memory"
topic: "general/agent-systems-and-browser-automation"
subtopic: "skills-and-memory"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - agent-systems-and-browser-automation
  - skills-and-memory
summary: "> **Status:** ✅ erledigt (6.9.2026) — Quell-Repo geklont and gelesen (48 Dateien, ~2.800 Zeilen Kernspezifikation)"
---

# R21 — DAP-Vorlage: Skills-Hub, Skill-Security & Memory

> **Status:** ✅ erledigt (6.9.2026) — Quell-Repo geklont and gelesen (48 Dateien, ~2.800 Zeilen Kernspezifikation)
<<<<<<< HEAD:knowledge/agent-skills-and-browser-control/skills-and-memory/r21-dap-skills-memory.md
> **Quelle:** https://github.com/ji-workstation/dap-docs (lokaler Klon: `${HOME}/projects/dap-docs`) — **DAP = Dynamic Agent Protocol**, Operator-eigene Spec

> **Source:** https://github.com/ji-podhead/dap-docs (lokaler Klon: `${HOME}/projects/dap-docs`) — **DAP = Dynamic Agent Protocol**, System Administrator-own Spec
> **Wichtig (Ehrlichkeit):** Die DAP-Docs sind explizit **eine PRD / Design-Spec, no Implementierungsstatus** („Nothing in this reference implies production readiness unless explicitly noted"). Alles unten ist Vorlagen-Material, not lauffähiger Code.
> **Anlass:** System Administrator-Lücke benannt (6.9.2026): The Multi-Provider Gateway fehlt ein **Skills-Hub**, **Security for Skills** and **Memory** — DAP deckt alle drei als Spec ab.

## 1. Was DAP ist (3 Layer, sauber getrennt)

| Layer | Name | Rolle |
|---|---|---|
| **Protocol** | DAP | Offener Standard: Tool-Discovery + -Invocation (gRPC `DiscoverTools`/`InvokeTool`/`SearchTools`), Skill-System (Score 0–100, Gates, Artifacts), Proof-Familie (PoT/PoS/PoD), Workflows (`llm`/`rag`/`script`/`crew`/`subagent`/`guardrail`), `tool_call_log` |
| **Network** | DAPNet | Infrastruktur: MQTT (EMQX, QoS, Last Will), SurrealDB, Qdrant |
| **System Administrator** | DAPCom | Backbone-Betreiber (per-message fees) |

Apps darauf: SurrealLife (Game-Layer!), DAP IDE. **Achtung:** Game-Mechaniken (Careers, SurrealCoin, Boss-Endorsements, Contraband, Company-Inheritance) sind SurrealLife-only — `dap-games.md` trennt das sauber and ist for The Multi-Provider Gateway die Ignore-Liste.

## 2. Kernbefunde je Lücke

### 2.1 Skills-Hub — `skills.md`, `tool-skill-binding.md`

* Skill = **public/** (Score 0–100 **abgeleitet, nie direkt geschrieben**, Level, Certifications) + **private/** (Artifacts, Memories, Performance-Log, Strategien — nur Agent + aktueller Arbeitgeber)
* Score-Derivation from Proof-of-Thought-Qualität: `new = old + (quality − 0.5) × learning_rate`, Decay pro Idle-Tag
* Adaptive Mechanismen statt Score-Override: konfigurierbare Learning-Rate pro Dimension, **Regime-Shift-Signal** (Agent meldet selbst, wenn Artifacts not mehr greifen → alte werden `stale` gerankt, Rate temporär erhöht), System Administrator-Override nur audit-logged (`skill_audit_log`)
* **Tool–Skill-Binding (geschlossener Loop):** Tools hinter Skill-Schwellen (`skill_min` — darunter **unsichtbar**, not nur gesperrt), erfolgreiche Calls geben `skill_gain` zurück; Multi-Skill-Bindings with Gewichten; `produces_artifact` → Artifacts werden selbst RAG-Kollektion
* Bloat-Score wird at Registrierung automatisch berechnet (description/schema/artifact tokens) — passt zu The Multi-Provider Gateway' Lean-Doktrin

### 2.2 Skill-Security — `acl.md`, `store-permissions.md`

> **Update 7.9.2026:** Die "eine Engine, not zwei"-Decision (§6 Punkt
> 4 unten) ist gefallen — **OPA**, not Casbin, siehe `DECISIONS.md`
> ("E-Policy — Policy-Engine: OPA"). Layer 1 unten bleibt als historisches
> Research Findings stehen (zeigt den DAP-Vorbild-Stand), jede Implementation
> nutzt aber OPA/Rego statt Casbin for die Protocol/App-ACL.

* **3-Layer-ACL-Stack** (jeder Layer deckt eine andere Enforcement-Fläche, „keiner ersetzt den anderen"):
  1. **Casbin** — Protocol/App-ACL (keyMatch2), ein Policy-Store for gRPC-Tool-Calls + MQTT-Topics + Daten-Namespaces; globale `deny`-Liste for Forbidden-Tools (z. B. `audit_log_delete`, `agent_identity_transfer`) — Checks **before** Handler-Ausführung
  2. **SurrealDB-RBAC** — Row-Level via `PERMISSIONS FOR select WHERE $auth...` + Record-Users als Agent-Identität
  3. **Capabilities-Härtung** — `--deny-arbitrary-query=record` (Agents senden no freies SurrealQL, nur `DEFINE API`-Endpoints), `--allow-net` on interne Dienste limitiert, `--deny-scripting`
* **5 Store-Access-Levels** for autonome Skill-Installation: NONE (unsichtbar) / READ_ONLY (browsen) / **GUARDED (jede Installation in menschliche Approval-Queue — Agent hängt eine Reason an, User bewertet Intention)** / **SCOPED (autonom innerhalb YAML-Grenzen: max_cost_per_day, allowed/blocked skill domains, vendor_tier_minimum, require_review_for ab Skill-Score, notify_on_install)** / FULL
* Skill-only-Installs als own Granularität (Artifacts ja, Tool-Code nein)
* Passgenau zur saits-cloud-RBAC-Kette from Requirement (Claim → Middleware → OPA → Labels → Egress): Casbin ≈ OPA on der Protocol-Ebene

### 2.3 Memory — `crew-memory.md`, `rag.md`

* CrewAI-Mitglieder backed by echte Agent-Records: Init lädt Memories (HNSW-Cosine) + Top-Skill-Artifacts + baut **dynamische Backstory** (Jinja-Template from realen Erfahrungen); after dem Kickoff schreiben alle Members Memories with `quality_score` + Embedding zurück
* `SurrealMemoryBackend` implementiert CrewAIs Memory-Interface (save/search direkt on die Agent-Collection)
* **RAG als Workflow-Phase (`type: rag`), not als Tool-Call:** hartes Token-Budget (`max_tokens: 400` vs. ~1.500 beim rohen MCP-Chunk-Dump), `summarize: true`, `access_filter: auto`, `persist_links: true` (Graph-Links → „was habe ich dazu schon gefunden" without Re-Search)
* **Skill-Artifacts als RAG-Kollektion:** High-Skill-Agent bekommt own bewährte Strategien with-injiziert, Low-Skill-Agent nur Web-Chunks
* 4-Layer-Access-Control „zero extra code": Capabilities → PERMISSIONS → HNSW-Filter → Casbin
* Storage-Inkonsistenz ehrlich notiert: DAPNet-Liste nennt Qdrant, `rag.md` sagt „SurrealDB HNSW — no separates Qdrant nötig" (zwei Antworten in der Spec)

### 2.4 Bonus: Tool-Registry — `tool-registration.md` (Milestone/18 direkt)

* YAML-Tool-Definition with `acl_path`/`acl_action`/`allowed_roles`/`skill_required`/`skill_min`/`skill_gain`/`bloat_score` (auto)/`a2a`
* 8 Handler-Types: `workflow` (versioniertes YAML) / `builtin` / `surreal_query` (file-drop, read-only) / `notebook` (sandboxed subprocess) / `proof` (Z3-verifizierte PoS-Pipeline) / `a2a` / `subagent` / `crew`

## 3. Verwertung for The Multi-Provider Gateway (Mapping)

| DAP-Konzept | The Multi-Provider Gateway-Anwendung | Wo (Epic) | Aufwand |
|---|---|---|---|
| Skill-Modell (public/private, Score from Qualitäts-Feedback, Decay, Regime-Shift) | Agenten-Qualitätsscore pro Dimension statt flachem Rating; DECISIONS-Regel: Score nie direkt schreiben | Architecture Pillar / Milestone/18 | M |
| Tool–Skill-Binding (`skill_min` unsichtbar, `skill_gain`-Loop) | Agent-Tool-Registry: Tools after Agent-Qualität freischalten | Milestone/18 Work Package | S |
| 5 Store-Levels (GUARDED-Approval-Queue with Agent-Reason) | Work Package Freeze/Release + Tool-Install-Genehmigung als HITL-Gate | Architecture Pillar + Work Package | S–M |
| SCOPED-Constraints-YAML (Kosten/Tag, Domain-Allow/Deny, Vendor-Tier) | Agent-Policy-Format (ergänzt Access Policy §2) | Architecture Pillar/17 | S |
| 3-Layer-ACL (Policy-Engine + Row-Level + Endpoint-Härtung) | Saits-Kette (Requirement) um die Capabilities-Härtung ergänzen | Architecture Pillar, Work Package | M |
| SurrealMemoryBackend / dynamische Backstory / Write-back with quality_score | Multi-Agent-Orchestrierung with persistentem Memory (The Multi-Provider Gateway: Postgres+pgvector statt SurrealDB?) | Architecture Pillar / Milestone | M |
| RAG als Workflow-Phase (Budget 400, summarize, persist_links, access_filter) | The Multi-Provider Gateway-RAG: Budget-Cap statt Chunk-Dump, Skill-Artifacts als Kollektion | Architecture Pillar | M |
| Bloat-Score at Registrierung | Tool-/Skill-Registry: automatische Schlankheits-Metrik | Milestone/18 | S |
| Proof-Familie PoT/PoS/PoD | PoT = quality_score-Quelle fürs Skill-Modell; PoS = Claim-Check | Architecture Pillar / SCHEMA-model-evaluation | M |

## 4. Nicht übernehmen / ehrliche Grenzen

* SurrealLife-Game-Layer (Endorsements, SurrealCoin, Contraband, Careers) — laut dap-games.md bewusst getrennt
* DAPCom-Abrechnungsmodell — The Multi-Provider Gateway-Credits bleiben Darstellungsschicht (Roadmap §4)
* **Implementierungsstatus = PRD.** Vor jeder Übernahme: Vector-Store-Decision (The Multi-Provider Gateway-Stack hat Redis without Stack-Module; pgvector wäre der pgx-Weg; DAP schwankt Qdrant vs. SurrealDB-HNSW)

## 5. Querverweise

* Requirement/003/004 (saits-Review): DPoP-Replay-Guard, RBAC-Kette, Tool-Schemas, RolesWidget
* `docs/SCHEMA-model-evaluation.md` — PoT-quality_score als Eval-Quelle
* `docs/PRODUCT-ROADMAP.md` §8 (Utility-Layer), Milestone/18 (MCP/Registry), Architecture Pillar (Admin-Layer)
* DAP-Vision im Bestand: `st-2/docs/DAP_VISION.md` (selbes Konzept from der Trading-Welt)

## 6. Offene Punkte

1. Vector-Store-Decision for Skills/Memory: pgvector (pgx-Weg) vs. Redis-Stack (sc-ai-Muster) vs. Qdrant (DAPNet) — blockiert Architecture Pillar Work Package
2. Skill-Dimensionen for The Multi-Provider Gateway definieren (coding, deploy, security, research?) + Score-Quelle (Work Package-Scanner-Verdict? PoT-Qualität? USER-Ratings?)
3. GUARDED-Approval-Queue: UI on der Admin-Seite (Architecture Pillar) or als Escalation-Inbox (Requirement)?
4. ~~Casbin vs. OPA~~ — **entschieden 7.9.2026: OPA** (`DECISIONS.md`
   "E-Policy — Policy-Engine: OPA"), gilt for diesen Layer 1 UND das
   Admin/RBAC-UI (Milestone Work Package) — eine Engine, not zwei.
5. Nimmt The Multi-Provider Gateway DAP als Protokoll-Basis (nur Spec-Teile, sauber getrennt vom Game-Layer) or nur als Muster-Referenz?
