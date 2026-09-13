---
okf_version: "1.0"
id: "okf-str-aud-r20-openmesh-reuse-review"
title: "R20 — openmesh-Repo-Review: Wiederverwendbares für OpenMesh"
topic: "strategy-audits-and-decisions"
subtopic: "audits-and-handoffs"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - audits-and-handoffs
summary: "> **Status:** ✅ DONE (6.9.2026) — alle 6 Tasks sequenziell/inline erledigt (das 2× gescheiterte"
---

# R20 — openmesh-Repo-Review: Wiederverwendbares for OpenMesh

> **Status:** ✅ DONE (6.9.2026) — alle 6 Tasks sequenziell/inline erledigt (das 2× gescheiterte
> Subagenten-Fan-out, 10/10, wurde ersetzt). Key Findings in §Key Findings + `docs/tasks/`
> (TASK-001 bis TASK-006). Ursprünglich als 5er-Fan-out angelegt.
> **Quelle:** Klone der eigenen GitHub-Org (31 Repos; Org-Name bewusst not im
> Repository dokumentiert — Ermittlung siehe unten), Stand 6.9.2026.

## 1. Kontext

Auftrag: alle Repos der eigenen Org klonen and on Wiederverwendbares for OpenMesh
prüfen — with ausdrücklicher Lupe on das Utility-Ebenen-Mandat (Database-Discovery,
-Management, CDC/Debezium; Roadmap §8, Epic 14) and on die offene
Multi-Tenant-Question E8.

**Mirror:** `~/projects/openmesh-mirror` (flach geklont, depth 1; liegt außerhalb
dieser Repo). Verzeichnisse with Quell-Präfix heißen im Mirror `openmesh-*` — die
Zuordnung zur echten Quelle steht je Klon in `git remote get-url origin`.

Neu klonen (gh authentifiziert, HTTPS; SSH-Key fehlt):

```bash
gh api user/orgs --jq '.[].login'   # eigene Org ermitteln and als $ORG einsetzen
ORG=<org>
mkdir -p ~/projects/openmesh-mirror && cd ~/projects/openmesh-mirror
gh repo list "$ORG" --limit 50 --json name -q '.[].name' \
  | xargs -I{} -P4 git clone --depth 1 "https://github.com/$ORG/{}.git"
# Repos with Quell-Präfix anschließend an das openmesh-*-Layout angleichen
# (Zuordnung je Klon: git remote get-url origin).
```

## 2. Ausführung

Sequenziell/inline, without Subagenten (Fan-out 2× an Runtime-Fehlern gescheitert, 10/10).
Reihenfolge = Priorität. Regeln and Ergebnis-Format: `docs/tasks/README.md`.

| # | Task-Datei | Speist primär |
|---|---|---|
| 1 | `docs/tasks/TASK-001-openmesh-review-security-identity.md` | WP1/WP5/WP8, Roadmap §1/§2, Mandat 9 |
| 2 | `docs/tasks/TASK-002-openmesh-review-plattform-gateway.md` | Access Policy, Credits, API_DOCS-Drift, E8 |
| 3 | `docs/tasks/TASK-003-openmesh-review-ops-observability.md` | WP3/WP4, OTLP, Login-Fund, Epic 13 |
| 4 | `docs/tasks/TASK-004-openmesh-review-ai-rag-skills.md` | Sprint 17/18, E8, Model-Evaluation |
| 5 | `docs/tasks/TASK-005-openmesh-review-trading-agent-infra.md` | Deploy-Engine, Epic 14 |
| 6 | `docs/tasks/TASK-006-openmesh-review-aggregation.md` | R20 §3/§4, BACKLOG/Roadmap |

## 3. Akzeptanzkriterien

- [ ] TASK-001 bis TASK-005 abgearbeitet, Key Findings in §Key Findings eingetragen
- [ ] Jede Fundstelle with Repo/Pfad, jede Empfehlung with Aufwand S/M/L
- [ ] Pro Task eine „Nicht portieren"-Liste with Begründung
- [ ] TASK-006: Top-5-Key Findings in BACKLOG/Roadmap überführt
- [ ] Gesamturteil: k8s-Welt vs. OpenMesh' Docker+SSH-Welt klar getrennt

## 4. Key Findings

### Task 1 — Security & Identity: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-001-openmesh-review-security-identity.md`

* **Kernfundstück: Vault PKI/AppRole** (Root+Intermediate, Leaf 10m–24h, `agent-runtime` = 10m/1h + read-only `tenant/+/api-keys/llm`, no Wildcard, TTL-Whitelists) — direktes Vorbild for §1 + Mandat 9; idempotenter 6-Schritt-Bootstrap als Skript-Vorlage.
* **Kontrakt ≠ Code:** Der Identitäts-Kontrakt (RS256, DPoP am Ingress, `X-Tenant-Id` nur ingress-deriviert, M2M-tenant_id from Cert-SAN) ist sauber in `openmesh-security-/docs/` festgehalten — aber `openmesh-auth` ist ein Scaffold (HS256, Legacy-Claim, no DPoP-Verifier, Logout-Stub). Kontrakt übernehmen, Code not.
* **Cilium→nftables:** Regelklassen (default-deny + DNS-Ausnahme + Single-Purpose-Allow) übersetzen sich in WP6-FirewallProvider; Label-Selektoren not — OpenMesh mappt Container-IP→Regel.
* **Falco-Baseline** liefert fertige WP8-Tripwire-Ideen (Secret-Read, Credential-Read, Egress-Verstoß) after Feld-Substitution; **Kyverno/OPA: Negativbefund** (no Policies im Repo).
* **Redis-SSoT not portieren** (Postgres-Mandat) — aber Lua-Atomic-Muster (Check+Mutate+Audit in einem EVAL, JTI-Deny-Set) and Quota-Fenster sind S-Aufwand-Gewinne.
* **Negativbefund:** no DB-Discovery/CDC in diesen vier Repos (Epic 14).
### Task 2 — Plattform & Gateway: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-002-openmesh-review-plattform-gateway.md`

* **Gateway-Vertrauenskette als Bauplan for WP1/§2:** sc-gateway fährt eine 3-Stufen-Kette (JWT→`x-tenant-id-verified` via claim_to_headers, DPoP-Verify with `cnf.jkt`/htm/htu/±30s/jti-Replay-Guard, Tenant-Binding: Client-Hint strippen, Mismatch = 403 + Audit, explizite Cross-Tenant-Exemptions). M2M: Bearer-over-mTLS with `cnf.x5t#S256` (RFC 8705) — beantwortet TASK-001-Question 1 (DPoP wird am Envoy-Ingress validiert).
* **JTI-Dedup als kanonisches Lua-Primitiv** (`openmesh-cloud/bootstrap/redis-scripts/dpop-jti-dedup.lua`, EVALSHA, SHA in Vault, fail-closed TTL 1..600) — Muster for WP1-Replay-Guard UND §4-Budget-Deduct; beendet „jeder rollt sein eigenes NX SET".
* **API-Contract-CI direkt kopierbar** (`openmesh-api/.github/workflows/lint.yml`): redocly lint + `openapi-diff --fail-on-incompatible` gegen Base-Ref pro Domain-File — der konkrete S-Fix for OpenMesh' 170-Routen/API_DOCS-Drift.
* **Kyverno/OPA-Policies gefunden** (Korrektur zu TASK-001): sie leben in sc-appconfigs, not in den Security-Repos — deny-privilege-escalation, runAsNonRoot, **Hardcoded-Secret-Deny in Rego** → direkt als WP8-Compose-Scanner-Regeln portierbar.
* **Role-driven Egress-Allowlist** (`tenants/_template/network-policies/sso-roles/05–07`: Rolle → Dienst+Port, Analytics GET-only per L7) = WP5-Modell; L7-Methodenfilter geht in nftables not — ehrlich: L4-only for v1.
* **OPNsense-Terraform** (`terraform/opnsense.tf`: VLANs, Unbound split-horizon, WireGuard, Rules) = Arbeitsreferenz for den optionalen WP6-FirewallProvider; **Fehlziel-Schutz** im Bootstrap (`SAITS_CLOUD_META_CTX`-Context-Guard gegen falsches Cluster) → Muster for OpenMesh-Deploy-Skripte.
* **Provisioning ist Phase-0-Stubs (ehrlich gekennzeichnet):** „render-for-review-then-apply" — Manifeste landen in `/tmp/sc-cp-render/{tenant}/` for Operator-Review, `APPLY=true` erst später; Reconciler-Reihenfolge dokumentiert (Namespace→Policies→Vault→ArgoCD zuletzt) → HITL-Muster for OpenMesh' Deploy-Engine + WP3.
* **Negativbefunde:** no DB-Discovery/CDC; `sc-default` (Tier-Budget-Seed for Roadmap §4) existiert not — 0 Dateien.
### Task 3 — Ops & Observability: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-003-openmesh-review-ops-observability.md`

* **SSE-Komplettpaket for Epic 13:** Cookie-Handshake (`aud=saits-sse`, 60s, `?token=` wegen Log-Leak entfernt), pro Verbindung eigener blocking-XREAD-Client, Last-Event-ID-Resume, Heartbeat/Idle-Disconnect, Tenant-Connection-Cap → 429, Drain at SIGTERM + fertiger `useLogStream`-Hook (Ring-Buffer + begrenztes Dedup-Set).
* **OTel-Tenant-Router als WP8-OTLP-Vorlage:** OIDC-Auth am OTLP-Receiver, Caller-Tenant-Attribute strippen, `tenant.id` from signiertem Token injizieren, Tenant-lose Payloads verwerfen (Aufwand M).
* **WP3-Fund:** Inbox löst Notifications + Escalations (Ack/Resolve with `resolved_by/resolved_at`) about einen State + pluggable Sinks (Telegram/SSE/webhook-signed) — das Freeze-Review-Gate als Escalation-Inbox.
* **Alert-Vorlagen:** QuotaSaturation, BillingInsufficientFundsSpike, AuditStream-Lag/Stuck — PromQL-Fertigvorlagen for §4/WP4.
* **Negativbefunde:** RBAC not implementiert (`packages/rbac` = `.gitkeep`, Clerk/OPA extern) → WP0-Login wird hier not gelöst; Dashboards-as-Code fehlt in diesem Repo; no DB-Discovery/CDC; openmesh-logs ist Phase-0-Scaffold (Nur-Design).
* **Nicht portieren:** Kafka-Two-Bus-Layer, K8s-Charts, Grafana-multi-org, WebSocket-Pfad (through dokumentierte SSE-Entscheidung ersetzt — bestätigt OpenMesh' R11-Wahl).
### Task 4 — AI, RAG & Skills: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-004-openmesh-review-ai-rag-skills.md`

* **sc-ai ist die RAG-Referenz (kompakt!):** Redis-Stack HNSW with Index+Key-Präfix **pro Tenant** (Isolation by construction), ~90-Zeilen-RAG-Kette with Grounding-Prompt; Eval-Spec with Fixtures + Schwellen (precision@5 ≥ 0.80, faithfulness ≥ 0.85) → Vorlage for `SCHEMA-model-evaluation.md`.
* **altfins-ai-skills = Skills-Blaupause for Sprint 17/18:** SKILL.md-Contract with „Do Not Use This Skill When", validated-surfaces-Snapshots (MCP-Surface als JSON, `runtime_tool_names_confirmed: false` — „nie Tool-Namen erfinden"), Contract-Lint-CI (Broken-Links), Multi-Plattform-Installer.
* **openmesh-ai = Phase-0-Kopie with Einzelsteinen:** Token-Budget with Stufen-Enforcement (80/95/100 %) + 1-Zeilen-Injektion, Two-Tier-Memory (Skill-Doc + Session-Log), Docker-native Inference-Erkennung via `/proc/net/tcp` (umgeht Go-eBPF-Lücke!), Agent-Mandate-Schema. Als Ganzes not portierbar (lcore-Imports, `.bak`-Trümmer).
* **ragas: nur LICENSE-Stub** — die Metriken-Spec in sc-ai ist der Wert; no Prompt-Registry (Prompts hardcoded, Versionierung = Git).
* **Negativbefunde:** no DB-Discovery/CDC (5. Gruppe in Folge); `skill-docs` leer.
* **DPoP-Replay-Guard jetzt dreifach implementiert** (dict in sc-ai, Sidecar-Muster in sc-gateway, kanonisches Lua) — TASK-002-Drift bestätigt.
* **Nachtrag (Operator-Hinweis 6.9.):** `claude/statemachine/rbac.py` — arbeitsfähige RBAC (Rollen-Hierarchie, auditiertes SuperAdmin-Force-Override, Capability-Flags, Engine-integriert) war in der Selektivlese untergegangen; dazu `roles.py` (Discord-Kanal-ACL) and `RolesWidget.jsx` (UI). Korrigiert in TASK-004.
### Task 5 — Trading & Agent-Infra: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-005-openmesh-review-trading-agent-infra.md`

* **Agent-Registry als deklaratives YAML** (st-2 `agent_definitions.yml`: Rollen/Eskalationsketten ra→rm→supervisor/KB-Tab; openmesh-crew `_definitions.yml`: Meta-Schema with status/semver/owner/depends_on) — Sprint 17/18 WP4-Blupause.
* **Trigger-Engine deklarativ** (cron + condition + message_agent-Templates) — ersetzt die 8 handgepflegten Server-Crons (Aufwand S).
* **Dashboard-Secret-Gate als WP0-Login-Muster:** `middleware.ts` — without Secret offen, with Secret Session-Cookie + `/login`; `bootstrap.sh` generiert Secrets automatisch. OpenMesh: Secret-**Pflicht** erwägen (Optional war die WP0-Wurzel).
* **Docker-Socket-Proxy** (restricted allowlist: nur CONTAINERS/EXEC/POST) statt docker.sock direkt.
* **Dual-Stack-Isolation + READ_ONLY-Analytics** (Demo/Mainnet voll getrennt, Analytics via HTTP-API, nie direkte DuckDB) — dem Epic-14-Gedanke am nächsten.
* **Negativbefund:** no DB-Discovery/CDC in st-2/openmesh-crew. Legacy: Root-Wildwuchs (copy-Dateien, .claude/ im Repo), echte Infra-IPs in Docs.
### Task 6 — Aggregation: ✅ ERLEDIGT (6.9.2026) — Details: `docs/tasks/TASK-006-openmesh-review-aggregation.md`

* **Konsolidierung:** 5 Tasks, 31 Repos, ~100 gelesene Dateien; 5 Cross-cutting-Themes (Identität/Gates, deklarative Config, Agenten-Security, Deployment-Trennung, ehrliche Phase-0-Kennzeichnung).
* **Top-5 (gesamt):** 1) RBAC-Kette (M, Epic 17 WP5), 2) Agent-Registry + Meta-Schema (S, Sprint 17/18), 3) Trigger-Engine (S, Automation), 4) Dashboard-Secret-Gate (S, WP0), 5) Docker-Socket-Proxy (S, WP-Security) — je with Task-Quelle.
* **Gesamturteil:** saits-Welt = Pattern-Quelle ersten Grades for Docker+SSH — bewusst draußen: k8s-Enforcement-Layer, SurrealDB/Qdrant (→ pgvector-Entscheid), Trading-Domänen-Code, Discord-first, VNC-unauth, DAPCom-Abrechnung. Portiert werden Muster, nie Domänen-Code.
* **Offene Questions konsolidiert (6)** + 3 neue Research-Prompts (P-R1 Policy-Engine, P-R2 Agent-Memory, P-R3 DPoP-Guard) in `RESEARCH-PROMPTS.md`.
* **Externes Research:** R21 (DAP) deckt die Operator-Lücken Skills-Hub / Skill-Security / Memory — BACKLOG Epic 18.

## 5. Operator-Feedback: Dashboard-IA (6.9.2026)

Direkt from dem Task-2/3/4-Material vom Operator entschieden:

* **Eine Hauptseite with Tabs — bewusst schlank:** Proxy (LLM-Gateway: Keys, Scopes, Quotas, Routing) · Projects (Deployments/Sandbox/Apps) · Security (K-LAF, Threats, Firewall) · DBs (Discovery, Debezium/CDC, Backups). Nicht überladen.
* **Admin/RBAC als EIGENE Seite** (Tenants, OPA, Rollen): der Cloud-Layer ist modular and muss **komplett separat benutzbar** sein; er darf Components with der Hauptseite teilen, aber no Navigation/UX verscherzen.
* **Zuordnungsregel for die saits-cloud-Funde:** RBAC/OPA/Tenant-Verwaltung → Admin-Seite. Scopes + Quotas → Proxy-Kern (Bedienung dort, Verwaltung on Admin). Der Proxy bleibt bewusst einfach — „for einen einfachen LLM-Proxy ist saits-cloud zu viel".
* Präzisierung (Operator, 6.9.): RBAC existiert in saits-cloud **Ende-zu-Ende** (Claim → Middleware → OPA → K8s-Labels → Egress-Policies) **plus App-Level `claude/statemachine/rbac.py`** (Rollen-Hierarchie + auditiertem Force-Override + Capability-Flags) — die Admin-Seite bekommt also eine fertige Kette als Vorlage, not nur Konzepte; neu zu bauen ist nur die Verwaltungs-UI.
* Konsequenz for TASK-006 (Verwertung): Mehr-Tenancy-/Admin-Muster nur als **optionaler, abtrennbarer Layer** bewerten, not als OpenMesh-Kern. RAG (falls gebaut) → Utility/Agent-Layer, ebenfalls not on der Proxy-Hauptseite.
