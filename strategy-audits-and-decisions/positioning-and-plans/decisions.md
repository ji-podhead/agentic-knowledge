---
okf_version: "1.0"
id: "okf-str-pos-decisions"
title: "Research Decisions — VERIFIED (Live API Tests)"
topic: "strategy-audits-and-decisions"
subtopic: "positioning-and-plans"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - positioning-and-plans
summary: "All 8 research docs reviewed + 4 follow-ups resolved. Live API tests confirm."
---

# Research Decisions — VERIFIED (Live API Tests)

All 8 research docs reviewed + 4 follow-ups resolved. Live API tests confirm.

## R1 — Multi-Window Dashboard
- **Grid Library**: react-grid-layout ✅
- **Iframe fix**: `pointer-events: none` on iframes during drag ✅
- **Sandbox**: `allow-scripts allow-same-origin allow-forms allow-popups` ✅
- **Layout persistence**: PostgreSQL + localStorage ✅
- **Single-Deploy**: Unabhängige Projekte (LeadScraper ↔ OpenMesh) laufen parallel.
  Single-Deploy-Mandat gilt nur for OpenMesh-managed coding deployments. ✅

## R2 — Coding Deployment Config
- **Editor**: CodeMirror 6 ✅
- **Config paths**: DSH (vconfig.json, hot-reload), OpenCode (opencode.json/jsonc, restart),
  OpenMesh (docker-compose env, restart-backend) ✅
- **LeadScraper**: Separate project, not von OpenMesh verwaltet ✅

## R3 — Auto-Provision
- **Virtual models**: New `GET /v1/mesh/models` endpoint ✅
- **Strategy**: Hybrid (auto-provision on deploy + manual drag-drop) ✅
- **JSONC Patcher**: Surgical string insertion for JSONC files (preserves comments).
  Regex-basierte targeted insertion — parse nur wenn pure JSON, sonst string-manipulation. ✅

## R4 — Entropy-Based Routing (VERIFIED LIVE)
- **Approach**: Full-Response + avg entropy (R8) ✅
- **VERIFIED**: Logprobs work through OpenMesh proxy on NVIDIA cloud API
  - `logprobs: true, top_logprobs: 5` → returns top-5 logprobs per token ✅
  - Full response (20 tokens) → avg normalized entropy = 0.14 for simple question ("What is 2+2?") ✅
  - Threshold 0.45 correctly classifies this as "simple" (no escalation) ✅
- **Planner Model**: `nvidia/nemotron-nano-3-30b-a3b` (3B active, free, NVIDIA cloud) ✅
  - In catalog, free (is_paid_model=0), always available on NVIDIA ✅
  - 30B total / 3B active (MoE) → fast inference, matches user's "nemotron" request ✅
- **Entropy Formula**: H_norm = H / log2(k), k=5, range 0..1 ✅
- **Config**: `entropy_routing: { enabled, threshold: 0.45, planner_model, cache_ttl: 300 }` ✅

## R5 — Framework Comparison
- **Entscheidung**: Go core + Python sidecar ✅
- **Sidecar Scope**:
  - Optional process, started only when enabled
  - Provides CrewAI-compatible role-based agent execution
  - Pydantic structured output validation
  - Speaks to OpenMesh via HTTP (OpenAI-compatible API)
  - Go core handles: native orchestration, goroutines, SSE, direct mesh route access
  - Sidecar handles: Python-framework-specific features (CrewAI crews, LangGraph graphs) ✅

## R6 — MoE Agents
- **Seed**: 3 Seed-Experten (coder-nemotron, reviewer-r1, researcher-phi) ✅
- **Gating agent**: small model, strict JSON output ✅
- **Parallel mode**: MoA principle, LLM synthesis aggregation ✅
- **Sequential mode**: pipeline, max depth 4 ✅
- **DB**: experts table, expert_runs table ✅

## R7 — DSH Plugin (VERIFIED AGAINST ACTUAL CODEBASE)
- **REALITY**: DSH plugin system is YAML-patch-based, NOT `registerPlugin()` API.
  The research described a hypothetical API that does NOT exist.
- **Actual mechanism**:
  1. Create npm package with `"dsh": {"bundle": {"patch": "./cordis.patch.yml"}}` in package.json
  2. Install via `dsh plugin --profile <name> add <package-name>` (forwards to pnpm)
  3. Patch file uses YAML `insert`/`update` operations on row IDs
  4. Each row maps to a Cordis plugin (by npm package name in `name` field)
  5. Cordis plugins register services, UI components, tools, model routes
- **Model discovery**: `ctx.llm.registerModelDiscovery()` in the LLM plugin
- **Client UI**: Separate packages (dsh-client-ui-*) render React components
- **To build OpenMesh orchestration plugin**:
  1. Create `@openmesh/dsh-plugin` npm package
  2. `cordis.patch.yml` inserts rows for: orchestration service, UI mode, model discovery
  3. Cordis plugins: server-side orchestration handler + client-side React panel
  4. Register OpenMesh mesh routes as model discovery provider ✅

## R8 — Speculative Decoding
- **Skip**: Nur NVIDIA cloud API → speculative decoding not relevant ✅
- **Logprobs matrix verified**: NVIDIA ✅ (live tested), Anthropic ❌, Gemini ❌ ✅

## Live Test Evidence
1. Logprobs via OpenMesh proxy → NVIDIA cloud: `logprobs: true` returns top-5 logprobs ✅
2. Full-response entropy: 20 tokens, avg entropy 0.14 for simple question ✅
3. Nemotron-nano in catalog: free, NVIDIA, 3B active params ✅
4. DSH plugin system: YAML patches + Cordis plugins (not registerPlugin) ✅

## Epic 17 — Access Policy Consolidation (Operator-approved, 6.9.2026)

Quelle: `docs/tasks/TASK-016-epic17-policy-konsolidierung.md` (Entscheidungsvorlage).
Entlastender Befund vorab, unabhängig verifiziert (not nur übernommen):
`handleBudgetCheck` (`rbac.go:70`, echte 402/403-Semantik) existiert, ist aber nur
als eigenständige Route registriert (`gateway.go:264`) — **no Aufruf from dem
Proxy-Pfad**. Budgets werden angezeigt, nie erzwungen. Zusätzlich verifiziert:
`gateway.go:1967` addiert hartcodiert `totalUsed += 250000 // Simulate ... for
visual representation` — echter Mandat-2-Verstoß.

**Freigegeben:**
1. **Enforcement-Punkt:** ein Aufruf `s.resolvePolicy(sessionID)` im Proxy-Pfad
   (`handleChatCompletionsProxy`), direkt after der Session-Auflösung from WP1
   (`resolveSessionID`), **before** Modell-Auswahl and Budget-Check.
2. **Kein Casbin/OPA for v1.** Der Budget-Block existiert bereits; die Rollen-Achse
   ist ein Aggregat from drei bestehenden Tabellen. P-R1 (Casbin-Go vs. OPA) bleibt
   offen, aber vom kritischen Pfad entkoppelt — DAP `acl.md` 3-Layer bleibt
   Referenz for eine spätere Stufe, wenn die Achsenzahl das rechtfertigt.
3. **Kaskade:** Team → Projekt → User/Agent, jeder Layer verengt nur
   (Intersektion, nie Erweiterung).
4. **Kein neues Schema** — Policy = Aggregat from `teams`/`team_members` +
   `project_user_budgets` + `model_scope` + WP1-`sessions`.
5. **Datenresidenz-Achse** (Roadmap §2, DSGVO/Real-Estate-Zielmarkt) als
   Provider-Constraint-Feld im Policy-Struct — eigener Teilschritt NACH dem
   Grund-Wire-in, not in derselben Änderung.

**Beantwortete offene Questions from der Vorlage:**
- Wire-in-Zeitpunkt: **after dem Merge von TASK-011** (der Session-Anker
  `resolveSessionID` muss on `main` liegen, bevor `resolvePolicy` daneben
  andockt).
- Simulate-Entfernung: **eigener Commit**, getrennt vom Wire-in — anderes Anliegen,
  eigene Nachvollziehbarkeit.

## E1–E5 — KLAF Foundation Follow-ups (Operator-approved, 6.9.2026)

Quelle: `docs/sprints/E1-E5-ENTSCHEIDUNGSVORLAGE.md` (Entscheidungsvorlage,
bereinigt — Original enthielt Copy-Paste-Reste einer fremden KI-Session).
WP2–4 sind ab jetzt entblockt.

1. **E1 — Injection-Klassifikator (WP2):** Option D — Pure-Go via `purego`/
   ONNX-Runtime-FFI, dynamisches Laden von `libonnxruntime.so`, no Sidecar,
   Mandat 7 (`CGO_ENABLED=0`) bleibt erfüllt. Fallback at Instabilität:
   Option A (Rust-Sidecar, Unix-Socket).
2. **E2 — Scanner-Fail-Verhalten (WP2):** Fail-open, pro Scanner
   konfigurierbar, Default fail-open. `scanners_bypassed=true` im Log +
   High-Priority-Alert at Fail-open-Wechsel (no stilles Fenster wie beim
   Incident vom 5.9.).
3. **E3 — Payload-Aufbewahrung/DSGVO (WP4):** Redigiert speichern, 30-Tage-
   Löschfrist, nur Operator-Rolle, jeder Zugriff auditiert. AVV-Klärung
   (Art. 28 DSGVO) verbindlich klären, sobald OpenMesh als Produkt an Dritte
   geht.
4. **E4 — Operator-Modell (WP3):** **Mehrbenutzer ab Sprint 20** (weicht von
   der Empfehlung „Ein-Operator + `frozen_by`/`released_by`" ab). Vier-Augen-
   Prinzip, Rollenmodell, Selbst-Freigabe-Verbot — Komplexität in WP3 bewusst
   in Kauf genommen.
5. **E5 — Freeze-Scope (WP3):** **Alle Container, inklusive fremde/per
   Discovery gefundene** (weicht von der Empfehlung „nur provisionierte" ab).
   Akzeptiertes Risiko: eine Fehlzuordnung kann einen fremden Produktivdienst
   einfrieren.

## E-Policy — Policy-Engine: OPA (Operator-approved, 7.9.2026)

Quelle: `docs/sprints/SPRINT-22-DASHBOARD-IA-ADMIN-RBAC.md` (E-Policy),
`docs/research/R21-dap-skills-memory.md` §6.4 ("eine Engine, not zwei").

**Korrektur zur ursprünglichen Empfehlung:** Erste Fassung empfahl Casbin
with der Begründung "no Sidecar" — das war falsch. Der native
**OPA Go SDK** (`github.com/open-policy-agent/opa/sdk`) embedded den
Rego-Evaluator direkt im Go-Binary, exakt wie Casbin — no Sidecar-Prozess
nötig. Der Embedded-vs-Sidecar-Unterschied entfällt damit als Argument.

**Entschieden: OPA**, from zwei vom Operator genannten Gründen:
1. **Mächtiger als Casbins RBAC/ABAC-Modelle** — Rego kann die
   Datenresidenz-Achse (Roadmap §2, DSGVO) als generische Attribut-
   Constraint ausdrücken, not nur Rollen-Checks.
2. **Bundle-API = zentrale Policy-Verteilung about Cloud-Grenzen hinweg** —
   OPA-Bundles können von einem zentralen Bundle-Server gezogen and about
   mehrere Deployments synchron gehalten werden. Das passt direkt on
   R22s B2B-Szenario (Kunde hostet OpenMesh in eigenem AWS-Account): Eine
   Policy-Änderung zieht in alle Kunden-Deployments ein, without Redeploy —
   Casbin hat dafür keinen eingebauten Mechanismus.

**Gilt for beide Layer, "eine Engine, not zwei":**
- Admin/RBAC-UI (SPRINT-22 WP4) — Autorisierungs-Entscheidungen for
  menschliche Operator-Aktionen.
- Agent-/Skill-Capability-ACL (R21 §6, ursprünglich Casbin vorgeschlagen)
  — Protocol-Ebene (Tool-Calls, Daten-Namespaces, `deny`-Liste for
  gefährliche Tools) läuft jetzt ebenfalls about OPA/Rego, not Casbin.
  R21 selbst bleibt unverändert als historisches Rechercheergebnis stehen
  (zeigt den Stand before dieser Entscheidung), aber jede Umsetzung folgt
  dieser Entscheidung, not dem Casbin-Vorschlag darin.

**Noch offen (Umsetzungsdetail, no Blockierung mehr):** wo die
Rego-Bundles herkommen (Datei/Verzeichnis im MVP, echter Bundle-Server erst
with dem ersten B2B-Kunden) — siehe `SPRINT-22` WP4 for den Umsetzungsstand.

**Umsetzungsstand (8.9.2026, WP4):** Engine ist live — embedded via
`github.com/open-policy-agent/opa/rego` (dieselbe Engine, no Sidecar;
das `sdk`-Bundle-Server-Paket folgt with dem ersten B2B-Kunden, ehrlich
notiert). Default-Policy + Datei-Override (`MESH_RBAC_POLICY`), Admin-
Mutationen on `/api/*` gatet, live verifiziert — Umfang: SPRINT-22 WP4,
Kontrakt: `docs/reference/AUTH-CONTRACT.md` §3b.

## E-IdP — Identity Broker: Keycloak, jetzt deployt (Operator-approved, 7.9.2026)

Quelle: `docs/research/R22-identity-broker-external-idp.md` (Gemini-
Recherche + eigene Prüfung), `docs/sprints/SPRINT-27-IDENTITY-BROKER-KEYCLOAK.md`.

**Ursprüngliche Empfehlung war "Kontrakt jetzt fixieren, Broker erst at
echtem B2B-Kundenbedarf deployen"** — vom Operator explizit abgelehnt.
Begründung: Es geht not nur um einen hypothetischen künftigen Kunden —
der Operator will jetzt schon ordentliches Auth, auch for sich selbst, with
Blick on ein späteres Public-Release des Projekts, and ein Package, das
wirklich skaliert statt später neu gebaut werden zu müssen.

**Entschieden: Keycloak** (not Zitadel), from einer Reihe von Nachfragen
zum Comparison mehrerer Options (Casbin/OPA/Cerbos/OpenFGA/Permit.io+OPAL
for Autorisierung — separat unter E-Policy behandelt; Zitadel/Ory/Keycloak/
Auth0 for Identität/Föderation):

1. **Zitadel vs. Keycloak:** beide sind eigene Services with eigenem
   Datenbestand (no Embedding wie at OPA/Casbin) — der
   Betriebsaufwand-Unterschied zwischen beiden ist gering. Zitadel ist Go
   (passt zu Mandat 7), leichter, aber jünger/kleinere Community. Keycloak
   ist Java/Quarkus (erstes JVM-Bauteil im sonst reinen Go-Stack), aber
   extrem ausgereift, seit about einem Jahrzehnt in Produktion, riesige
   Community, breiter Enterprise-Wiedererkennungswert. **Operator wählt
   Keycloak** — bewusst gegen die Stack-Reinheit, for Reife/Skalennachweis.
2. **`hugocortes/go-keycloak` geprüft and verworfen:** ist ein REST-Client
   for Keycloaks Admin-API (Token-Fetch, User-Management, UMA), no
   eingebetteter Server-Ersatz — ändert nichts an Keycloaks JVM-Betriebskosten.
   Zusätzlich: unmaintained seit 2018, no `go.mod`. Falls ein Go-Client
   for Keycloaks Admin-API gebraucht wird: `Nerzal/gocloak` ist die
   gepflegte Alternative.
3. **Scope:** Keycloak ersetzt die menschliche Dashboard-Anmeldung (WP0s
   Passwort-Login), NICHT die Agent-/M2M-Session-Tokens
   (`store.MintSessionToken` from Sprint 20 WP1) — die bleiben ein eigener,
   interner Mechanismus for spawnte Container, no Login-Fall.
4. **Getrennt von E-Policy:** Keycloak liefert Identität (RS256-JWT,
   Rollen-Claims möglich), OPA (E-Policy) entscheidet anhand dessen about
   Zugriff. Zwei Schritte einer Kette, not eine Engine.

Umsetzung: `docs/sprints/SPRINT-27-IDENTITY-BROKER-KEYCLOAK.md` (Docker-
Compose-Service, eigene Postgres-Datenbank `keycloak` on dem bestehenden
Server, Realm/Client-Bootstrap, Ingress-RS256-Verify in `internal/auth`,
Migration des bestehenden Operator-Logins, mindestens ein externer IdP —
GitHub — als Föderations-Nachweis).

## E-Editions — Produkt-Tiering & Edge-Control-Plane (Operator-approved, 13.9.2026)

**Quelle:** Operator-Diskussion 13.9. („das kann OpenMesh Enterprise sein;
überlegen ob man OpenMesh DB Pro with installiert" + „beim SSH-Target-Deploy
auswählen können, ob man die OpenMesh Control Plane dort deployt — wegen
Logs and DB-Services in Production: der Router routet direkt an die
Control-Plane-Node on dem Remote-Target").

### Tier-Modell

| Tier | Enthält | Lizenz |
|---|---|---|
| **Core** | LLM-Gateway (/v1, Routing, Keypool, Budgets, Consumer-/Service-Keys), K-LAF-Security (Egress, Socket-Guard, Freeze), Workspace-Provisioning (Zero-Port, gVisor opt-in), Logger-SDK + Per-App-Attribution, Headscale-Mesh (opt-in), Keycloak, MCP-Provider, Key-Mgmt | PolyForm-NC (Hauptrepo) |
| **DB Pro** | Router-Node L7 (pgproto3+RESP, Alias-Registry), CDC in-process (pglogrepl), DB-Discovery/-Management, Provisioning-Kopplung | Commercial-License-File (LICENSE-COMMERCIAL.md — Dual-Lizenz) |
| **Enterprise** | Debezium-Hub (NoSQL-Zoo), Router-als-Tunnel zum Hub, SIEM-Integrationen, OPA-Bundle-Distribution | Commercial-License-File |

### Edge-Control-Plane-Node (verteilte Datenfläche — Operator-Anforderung)

Beim SSH-Target-Deploy wird **optional (Checkbox)** ein **OpenMesh Edge
Node** on dem Target installiert — EIN Go-Binary (Evolution des
TASK-033-Router), localhost-only (Zero-Port):

```
[Apps/Agents on dem Target]
    → localhost (fixer Port) → [Edge Node: L7-Router + Log-Ingest + CDC-Forward]
                                     │  outbound-only Sync (Mesh/Service-Token)
                                     ▼
                      [Zentrale Control Plane (Verwaltung, UI, Langfuse, Hub)]
```

**Warum (Operator-Begründung):** Production-DB-Traffic and Logs dürfen
KEINEN WAN-Roundtrip pro Query machen. Der Edge Node bedient lokal
(Alias-Routing, Log-Buffer), synct asynchron zur Zentrale (Config-Pull
and Event-Forward sind bereits im Router-WIP angelegt: pull.go +
gateway/router_config.go). Zentrale bleibt Verwaltungs-/Observability-
Fläche, Edge ist die Datenfläche.

**Verbindungssemantik:** WAN-down → Edge arbeitet weiter (Buffer +
Forward), Verwaltung eingefrort bis Sync zurückkommt — dokumentiert im
UI (Edge-Status im Networks-Tab).

**Packaging:** Edge-Node-Binary ist eins; Editionen schalten FEATURES
frei (Core: Log-Ingest/Forward; DB Pro: L7-Router/CDC lokal; Enterprise:
Hub-Tunnel). Ein Build, Runtime-Entitlement — no separaten Downloads.

## E-Firewall — Firewall-Scope: Environment-scoped, NICHT Host-Level (Operator-approved, 13.9.2026)

**Operator-Entscheidung:** „Firewall muss nur for unsere Environments gelten.
OpenMesh stellt sichere Environments bereit — die Firewall läuft NICHT on dem
Host, sondern als Container (die NAT-Node) or in der Control-Plane pro
Environment/Projekt, das Apps hat."

**Konsequenzen:**
1. **Host-Firewall bleibt unberührt** — UFW/iptables des Hosts sind not
   OpenMeshs Geschäft (no `nft` on dem Backend-Host nötig — erklärt den
   Fund: firewall_provider.go lief `nft` LOKAL and fand nichts).
2. **Firewall = Container/Control-Plane-Komponente:** die nftables-Regeln
   leben (a) im Network-Namespace des Workspace-Containers (bereits so:
   `openmesh_egress_eth0`-Tabelle, projects_ssh.go:366) or (b) am Edge-Node/
   NAT-Container des Environments (Sprint-36-WP6-Richtung).
3. **firewall_provider.go Ziel-Fix:** Provider-Interface bekommt ein
   Target (SSH-Target-Exec statt lokal-exec) — Capabilities/EffectiveRule
   kommen vom Environment, not vom Backend-Host.

---

## E-Projects — Project = Repo/Folder, Apps darin, Network-Editing (Operator, 13.9.2026)

**Operator:** „Es fehlt noch: ein Git-Repo or ein Folder IST ein Project,
wo Apps wie DBs drinlaufen and discovered werden. Und der Network-Editing-
Tab: Networking einstellen, Bridges deployen, Container neu starten at
Netzwerk-Änderung. Obwohl das im Compose-File geht — beides soll gehen."

**Drei fehlende Bausteine (→ BACKLOG TASK-049):**
1. **Project = Repo/Folder:** Git-Repo ODER Folder ist das Project; Apps
   (DBs, Services) laufen DARIN and werden gediscovered (Project-scoped
   Discovery statt globaler Container-Discovery).
2. **Network-Editing-Tab:** Networking pro Projekt konfigurieren
   (Bridges/Netze deployen, Alias→Netz-Zuordnung), Container-Neustart
   at Netzwerk-Änderung (Migration-Flow: Netz ändern → betroffene
   Container reschedulen).
3. **Beide Pfade:** Compose-File UND UI-Tab führen zum selben Zustand
   (Compose-Edit bleibt Source-of-Truth-fähig, UI schreibt dieselben
   Compose-/DB-Zustände — no zweites Schema).

## E-Priority — Managed-Ports-First: Wir verwalten Ports/Firewall for den User (BYOF später) (Operator, 13.9.2026)

**Operator:** „Was unsere App machen soll: wir verwalten die Ports and
Firewall-Rules DIREKT for den User. Er kann seine eigene Firewall mitbringen
— das kommt SPÄTER. Erstmal ist wichtig: in unseren Safe-Environments haben
wir die SIEM and werden PERMANENT gescannt. Networks aber auch Code — wir
sichern den User ab, dass er KEINE Ports offen hat for seinen DSG-Container."

**Entscheidung (Priorität):**
1. **Managed-Model jetzt:** OpenMesh verwaltet Ports/Firewall-Rules direkt
   for den User (er sieht seine Rules, ändert sie not selbst) —
   BYOF (eigene Firewall mitbringen) = SPÄTER.
2. **Safe-Environments = SIEM + Permanent-Scan:** SIEM lebt in den
   Safe-Environments (TASK-032-Approach A OpenMesh-native light) and
   scannt PERMANENT (continuous, not einmalig — E-SIEM greift).
3. **Zero-Open-Ports-Enforcement (DSG):** User-Container (DSG-konform)
   haben KEINE offenen Ports außer den explizit vergebenen —
   Inbound-Closure greift per Network-Namespace (nftables-Tabelle im
   Container-NS, wie Egress bereits) + NAT-Node am Edge (E-Firewall).
4. **Networks and Code:** die Absicherung gilt for Netzwerke UND den
   Code darin (beides wird gescannt — SIEM-Attribution Deployment/App/
   Project via K-LAF-Identitätskette, TASK-032).

**Consequence:** TASK-050 (Inbound-Enforcement + Permanent-Scan) wird
PRIORITY before BYOF-Tasks; TASK-048/049-Reihenfolge bleibt.

---

## E-BYOL — Bring-Your-Own-License/Scanner-Integration (Operator, 14.9.2026)

**Operator-Quelle:** Aikido-Research (Bing, 14.9.): Aikido Zen (in-app
firewall, MIT-lizenzierte OS-Komponente), Local Scanner (on-premise,
Premium ~$700/Monat), BYOL-Prinzip (User bringt eigenes Konto, OpenMesh
baut nur die technische Brücke).

**Entscheidung: BYOL als Integrationsmuster for ALLE optionalen
Drittanbieter-Security-Tools** (Aikido, CrowdSec, eigener Firewall-Provider):

1. **OpenMesh integriert, User lizenziert:** Der Kunde meldet sich selbst
   beim Drittanbieter an (BYOL) — OpenMesh liefert nur die Brücke:
   Settings-Feld for den Token/API-Key + Runner der die CLI/API aufruft.
   Kein Reselling, no White-Labeling → no Partner-Zwang.
2. **Zen (MIT) darf EINGEBETTET werden** — als Alternative zum
   handgerollten Inbound-Regelwerk am Router (TASK-050): Zen ist eine
   embedded runtime firewall die File-Access + outbound HTTP instrumentiert.
   Kann als Utility-Container pro Deployment laufen (Sprint-31-Muster).
   Vorsicht: OS-Variante without Dashboard; Dashboard = Aikido-SaaS.
3. **Local-Scanner (SAST/Dependency):** OpenMesh stößt die Aikido-CLI im
   Kunden-Deployment an (Token des Kunden, on-premise Code bleibt beim
   Kunden, nur Metadaten-Upload). HINWEIS for Doku: Local-Scanner =
   Premium-Feature beim Kunden (~$700/Monat) — als klaren Hinweis in
   die Einstellungen dokumentieren.
4. **BYOF-Firewall-Provider:** gleiches Muster (E-Priority: Managed-First
   bleibt default, BYOF-Stub in firewall.go:26-29 ist der Ankerpunkt);
   OVS/OPNsense-Anbindung (Operator hat ovs-bridge-collection +
   opnsense-helper) = dedizierte-Box-Szenario, NICHT „any existing VPS" —
   slot in TASK-049 (Network-Editing-Tab) for Home-Lab/Bare-Metal-Targets.

---

## E-IA — Frontend-IA: 5 Haupt-Tabs + separates Admin (Operator, 14.9.2026)

**Quelle:** Claude's SPRINT-22-Drift-Analyse (4-Tab-Disziplin vom 6.9. war still
erodiert: /vault-dashboard + /control-planes landeten per Convenience in
PROJECT_BASES; Security wuchs on 5+ Sub-Seiten without Sub-Nav) + Operator-
Entscheidung 14.9. („ok go go go" on die 3 Recommendations).

**Die 3 Entscheidungen:**
1. **Networks/Headscale → Platform-Tab** (not Workspaces): die headplane-geforkte
   NetworksPage ist eine Plattform-Admin-Fläche (Mesh-User/Nodes/Keys), no
   Workspace-Concept. SSH-Endpoints bleiben in Workspaces (Deploy-Targets).
2. **NEUER 5. Haupt-Tab „Platform"**: Control-Planes + Vault + Networks —
   Registries about „wo läuft was, was erreicht was, welche Engines". Die
   SPRINT-22-4-Tab-Disziplin wird bewusst zu 5 Tabs + separatem Admin erweitert.
3. **VaultDashboardPage gewinnt „Vault" → Platform-Tab; /security/vault wird
   „Project Secrets" → Security-Tab** (per-Project K-LAF-Laufzeit-Secrets).
   TASK-066: NICHT blind mergen — VaultPage's einzigartige Features inventarisieren,
   Secret-Listen-UX after Security/Project-Secrets, Redirect der alten Route.

**Die Ziel-Struktur:**

| Tab | Konzept | Inhalt |
|---|---|---|
| Proxy | LLM-Kern | Config, Keys, Analytics, Logs, Models, Fallback |
| Workspaces | Was du baust | Workspaces, Apps, SSH-Endpoints, Deployments, Playground/Agents/Chat |
| Platform (NEU) | Wo es läuft & was es erreicht | Control-Planes, Vault (Engine-Registry), Networks/Mesh |
| Security | Ist es sicher | Overview, Events, Scans, Testing, Exposure, Project-Secrets |
| DBs | Daten-Layer | Backups, Discovery |
| Admin (separat, SHOW_ADMIN_NAV) | Multi-Tenancy | Users, Teams, Consumer-Keys, Budgets |

**Runtime-Presets** (dsh/python/go/node/docker/base) = App-Ebene, not
Workspace-Root (bereits via TASK-063 umgesetzt).

**Enforcement-Regel for alle zukünftigen Agents:** Neue Routen/Seiten landen
NIE per Convenience in der nächstgelegenen Nav-Gruppe — gegen diese Tabelle
prüfen; ein neues Konzept braucht eine bewusste Platzierungs-Entscheidung im
Sprint-File BEVOR es gebaut wird. (Lessen from dem SPRINT-22-Drift.)
