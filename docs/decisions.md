---
id: "DECISIONS"
title: "Research Decisions — VERIFIED (Live API Tests)"
type: decision
date: 2026-09-13
status: final
tags: [mesh, keycloak, opa, logprobs, vault]
license: CC-BY-4.0
---

# Research Decisions — VERIFIED (Live API Tests)

All 8 research docs reviewed + 4 follow-ups resolved. Live API tests confirm.

## R1 — Multi-Window Dashboard
- **Grid Library**: react-grid-layout ✅
- **Iframe fix**: `pointer-events: none` on iframes during drag ✅
- **Sandbox**: `allow-scripts allow-same-origin allow-forms allow-popups` ✅
- **Layout persistence**: PostgreSQL + localStorage ✅
- **Single-Deploy**: Unabhängige Projekte (LeadScraper ↔ JiMesh) laufen parallel.
  Single-Deploy-Mandat gilt nur für JiMesh-managed coding deployments. ✅

## R2 — Coding Deployment Config
- **Editor**: CodeMirror 6 ✅
- **Config paths**: DSH (vconfig.json, hot-reload), OpenCode (opencode.json/jsonc, restart),
  JiMesh (docker-compose env, restart-backend) ✅
- **LeadScraper**: Separate project, nicht von JiMesh verwaltet ✅

## R3 — Auto-Provision
- **Virtual models**: New `GET /v1/mesh/models` endpoint ✅
- **Strategy**: Hybrid (auto-provision on deploy + manual drag-drop) ✅
- **JSONC Patcher**: Surgical string insertion für JSONC files (preserves comments).
  Regex-basierte targeted insertion — parse nur wenn pure JSON, sonst string-manipulation. ✅

## R4 — Entropy-Based Routing (VERIFIED LIVE)
- **Approach**: Full-Response + avg entropy (R8) ✅
- **VERIFIED**: Logprobs work through JiMesh proxy on NVIDIA cloud API
  - `logprobs: true, top_logprobs: 5` → returns top-5 logprobs per token ✅
  - Full response (20 tokens) → avg normalized entropy = 0.14 für simple question ("What is 2+2?") ✅
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
  - Speaks to JiMesh via HTTP (OpenAI-compatible API)
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
- **To build JiMesh orchestration plugin**:
  1. Create `@jimesh/dsh-plugin` npm package
  2. `cordis.patch.yml` inserts rows for: orchestration service, UI mode, model discovery
  3. Cordis plugins: server-side orchestration handler + client-side React panel
  4. Register JiMesh mesh routes as model discovery provider ✅

## R8 — Speculative Decoding
- **Skip**: Nur NVIDIA cloud API → speculative decoding nicht relevant ✅
- **Logprobs matrix verified**: NVIDIA ✅ (live tested), Anthropic ❌, Gemini ❌ ✅

## Live Test Evidence
1. Logprobs via JiMesh proxy → NVIDIA cloud: `logprobs: true` returns top-5 logprobs ✅
2. Full-response entropy: 20 tokens, avg entropy 0.14 for simple question ✅
3. Nemotron-nano in catalog: free, NVIDIA, 3B active params ✅
4. DSH plugin system: YAML patches + Cordis plugins (not registerPlugin) ✅

## Epic 17 — Access Policy Consolidation (Operator-approved, 6.9.2026)

Quelle: `task docs (internal)` (Entscheidungsvorlage).
Entlastender Befund vorab, unabhängig verifiziert (nicht nur übernommen):
`handleBudgetCheck` (`rbac.go:70`, echte 402/403-Semantik) existiert, ist aber nur
als eigenständige Route registriert (`gateway.go:264`) — **kein Aufruf aus dem
Proxy-Pfad**. Budgets werden angezeigt, nie erzwungen. Zusätzlich verifiziert:
`gateway.go:1967` addiert hartcodiert `totalUsed += 250000 // Simulate ... for
visual representation` — echter Mandat-2-Verstoß.

**Freigegeben:**
1. **Enforcement-Punkt:** ein Aufruf `s.resolvePolicy(sessionID)` im Proxy-Pfad
   (`handleChatCompletionsProxy`), direkt nach der Session-Auflösung aus WP1
   (`resolveSessionID`), **vor** Modell-Auswahl und Budget-Check.
2. **Kein Casbin/OPA für v1.** Der Budget-Block existiert bereits; die Rollen-Achse
   ist ein Aggregat aus drei bestehenden Tabellen. P-R1 (Casbin-Go vs. OPA) bleibt
   offen, aber vom kritischen Pfad entkoppelt — DAP `acl.md` 3-Layer bleibt
   Referenz für eine spätere Stufe, wenn die Achsenzahl das rechtfertigt.
3. **Kaskade:** Team → Projekt → User/Agent, jeder Layer verengt nur
   (Intersektion, nie Erweiterung).
4. **Kein neues Schema** — Policy = Aggregat aus `teams`/`team_members` +
   `project_user_budgets` + `model_scope` + WP1-`sessions`.
5. **Datenresidenz-Achse** (Roadmap §2, DSGVO/Real-Estate-Zielmarkt) als
   Provider-Constraint-Feld im Policy-Struct — eigener Teilschritt NACH dem
   Grund-Wire-in, nicht in derselben Änderung.

**Beantwortete offene Fragen aus der Vorlage:**
- Wire-in-Zeitpunkt: **nach dem Merge von TASK-011** (der Session-Anker
  `resolveSessionID` muss auf `main` liegen, bevor `resolvePolicy` daneben
  andockt).
- Simulate-Entfernung: **eigener Commit**, getrennt vom Wire-in — anderes Anliegen,
  eigene Nachvollziehbarkeit.

## E1–E5 — KLAF Foundation Follow-ups (Operator-approved, 6.9.2026)

Quelle: `sprint docs (internal)` (Entscheidungsvorlage,
bereinigt — Original enthielt Copy-Paste-Reste einer fremden KI-Session).
WP2–4 sind ab jetzt entblockt.

1. **E1 — Injection-Klassifikator (WP2):** Option D — Pure-Go via `purego`/
   ONNX-Runtime-FFI, dynamisches Laden von `libonnxruntime.so`, kein Sidecar,
   Mandat 7 (`CGO_ENABLED=0`) bleibt erfüllt. Fallback bei Instabilität:
   Option A (Rust-Sidecar, Unix-Socket).
2. **E2 — Scanner-Fail-Verhalten (WP2):** Fail-open, pro Scanner
   konfigurierbar, Default fail-open. `scanners_bypassed=true` im Log +
   High-Priority-Alert bei Fail-open-Wechsel (kein stilles Fenster wie beim
   Incident vom 5.9.).
3. **E3 — Payload-Aufbewahrung/DSGVO (WP4):** Redigiert speichern, 30-Tage-
   Löschfrist, nur Operator-Rolle, jeder Zugriff auditiert. AVV-Klärung
   (Art. 28 DSGVO) verbindlich klären, sobald JiMesh als Produkt an Dritte
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

Quelle: `sprint docs (internal)` (E-Policy),
`docs/research/R21-dap-skills-memory.md` §6.4 ("eine Engine, nicht zwei").

**Korrektur zur ursprünglichen Empfehlung:** Erste Fassung empfahl Casbin
mit der Begründung "kein Sidecar" — das war falsch. Der native
**OPA Go SDK** (`github.com/open-policy-agent/opa/sdk`) embedded den
Rego-Evaluator direkt im Go-Binary, exakt wie Casbin — kein Sidecar-Prozess
nötig. Der Embedded-vs-Sidecar-Unterschied entfällt damit als Argument.

**Entschieden: OPA**, aus zwei vom Operator genannten Gründen:
1. **Mächtiger als Casbins RBAC/ABAC-Modelle** — Rego kann die
   Datenresidenz-Achse (Roadmap §2, DSGVO) als generische Attribut-
   Constraint ausdrücken, nicht nur Rollen-Checks.
2. **Bundle-API = zentrale Policy-Verteilung über Cloud-Grenzen hinweg** —
   OPA-Bundles können von einem zentralen Bundle-Server gezogen und über
   mehrere Deployments synchron gehalten werden. Das passt direkt auf
   R22s B2B-Szenario (Kunde hostet JiMesh in eigenem AWS-Account): Eine
   Policy-Änderung zieht in alle Kunden-Deployments ein, ohne Redeploy —
   Casbin hat dafür keinen eingebauten Mechanismus.

**Gilt für beide Layer, "eine Engine, nicht zwei":**
- Admin/RBAC-UI (SPRINT-22 WP4) — Autorisierungs-Entscheidungen für
  menschliche Operator-Aktionen.
- Agent-/Skill-Capability-ACL (R21 §6, ursprünglich Casbin vorgeschlagen)
  — Protocol-Ebene (Tool-Calls, Daten-Namespaces, `deny`-Liste für
  gefährliche Tools) läuft jetzt ebenfalls über OPA/Rego, nicht Casbin.
  R21 selbst bleibt unverändert als historisches Rechercheergebnis stehen
  (zeigt den Stand vor dieser Entscheidung), aber jede Umsetzung folgt
  dieser Entscheidung, nicht dem Casbin-Vorschlag darin.

**Noch offen (Umsetzungsdetail, keine Blockierung mehr):** wo die
Rego-Bundles herkommen (Datei/Verzeichnis im MVP, echter Bundle-Server erst
mit dem ersten B2B-Kunden) — siehe `SPRINT-22` WP4 für den Umsetzungsstand.

**Umsetzungsstand (8.9.2026, WP4):** Engine ist live — embedded via
`github.com/open-policy-agent/opa/rego` (dieselbe Engine, kein Sidecar;
das `sdk`-Bundle-Server-Paket folgt mit dem ersten B2B-Kunden, ehrlich
notiert). Default-Policy + Datei-Override (`JIMESH_RBAC_POLICY`), Admin-
Mutationen auf `/api/*` gatet, live verifiziert — Umfang: SPRINT-22 WP4,
Kontrakt: `docs/reference/AUTH-CONTRACT.md` §3b.

## E-IdP — Identity Broker: Keycloak, jetzt deployt (Operator-approved, 7.9.2026)

Quelle: `docs/research/R22-identity-broker-external-idp.md` (Gemini-
Recherche + eigene Prüfung), `sprint docs (internal)`.

**Ursprüngliche Empfehlung war "Kontrakt jetzt fixieren, Broker erst bei
echtem B2B-Kundenbedarf deployen"** — vom Operator explizit abgelehnt.
Begründung: Es geht nicht nur um einen hypothetischen künftigen Kunden —
der Operator will jetzt schon ordentliches Auth, auch für sich selbst, mit
Blick auf ein späteres Public-Release des Projekts, und ein Package, das
wirklich skaliert statt später neu gebaut werden zu müssen.

**Entschieden: Keycloak** (nicht Zitadel), aus einer Reihe von Nachfragen
zum Vergleich mehrerer Optionen (Casbin/OPA/Cerbos/OpenFGA/Permit.io+OPAL
für Autorisierung — separat unter E-Policy behandelt; Zitadel/Ory/Keycloak/
Auth0 für Identität/Föderation):

1. **Zitadel vs. Keycloak:** beide sind eigene Services mit eigenem
   Datenbestand (kein Embedding wie bei OPA/Casbin) — der
   Betriebsaufwand-Unterschied zwischen beiden ist gering. Zitadel ist Go
   (passt zu Mandat 7), leichter, aber jünger/kleinere Community. Keycloak
   ist Java/Quarkus (erstes JVM-Bauteil im sonst reinen Go-Stack), aber
   extrem ausgereift, seit über einem Jahrzehnt in Produktion, riesige
   Community, breiter Enterprise-Wiedererkennungswert. **Operator wählt
   Keycloak** — bewusst gegen die Stack-Reinheit, für Reife/Skalennachweis.
2. **`hugocortes/go-keycloak` geprüft und verworfen:** ist ein REST-Client
   für Keycloaks Admin-API (Token-Fetch, User-Management, UMA), kein
   eingebetteter Server-Ersatz — ändert nichts an Keycloaks JVM-Betriebskosten.
   Zusätzlich: unmaintained seit 2018, kein `go.mod`. Falls ein Go-Client
   für Keycloaks Admin-API gebraucht wird: `Nerzal/gocloak` ist die
   gepflegte Alternative.
3. **Scope:** Keycloak ersetzt die menschliche Dashboard-Anmeldung (WP0s
   Passwort-Login), NICHT die Agent-/M2M-Session-Tokens
   (`store.MintSessionToken` aus Sprint 20 WP1) — die bleiben ein eigener,
   interner Mechanismus für spawnte Container, kein Login-Fall.
4. **Getrennt von E-Policy:** Keycloak liefert Identität (RS256-JWT,
   Rollen-Claims möglich), OPA (E-Policy) entscheidet anhand dessen über
   Zugriff. Zwei Schritte einer Kette, nicht eine Engine.

Umsetzung: `sprint docs (internal)` (Docker-
Compose-Service, eigene Postgres-Datenbank `keycloak` auf dem bestehenden
Server, Realm/Client-Bootstrap, Ingress-RS256-Verify in `internal/auth`,
Migration des bestehenden Operator-Logins, mindestens ein externer IdP —
GitHub — als Föderations-Nachweis).

## E-Editions — Produkt-Tiering & Edge-Control-Plane (Operator-approved, 13.9.2026)

**Quelle:** Operator-Diskussion 13.9. („das kann JiMesh Enterprise sein;
überlegen ob man JiMesh DB Pro mit installiert" + „beim SSH-Target-Deploy
auswählen können, ob man die JiMesh Control Plane dort deployt — wegen
Logs und DB-Services in Production: der Router routet direkt an die
Control-Plane-Node auf dem Remote-Target").

### Tier-Modell

| Tier | Enthält | Lizenz |
|---|---|---|
| **Core** | LLM-Gateway (/v1, Routing, Keypool, Budgets, Consumer-/Service-Keys), K-LAF-Security (Egress, Socket-Guard, Freeze), Workspace-Provisioning (Zero-Port, gVisor opt-in), Logger-SDK + Per-App-Attribution, Headscale-Mesh (opt-in), Keycloak, MCP-Provider, Key-Mgmt | PolyForm-NC (Hauptrepo) |
| **DB Pro** | Router-Node L7 (pgproto3+RESP, Alias-Registry), CDC in-process (pglogrepl), DB-Discovery/-Management, Provisioning-Kopplung | Commercial-License-File (LICENSE-COMMERCIAL.md — Dual-Lizenz) |
| **Enterprise** | Debezium-Hub (NoSQL-Zoo), Router-als-Tunnel zum Hub, SIEM-Integrationen, OPA-Bundle-Distribution | Commercial-License-File |

### Edge-Control-Plane-Node (verteilte Datenfläche — Operator-Anforderung)

Beim SSH-Target-Deploy wird **optional (Checkbox)** ein **JiMesh Edge
Node** auf dem Target installiert — EIN Go-Binary (Evolution des
TASK-033-Router), localhost-only (Zero-Port):

```
[Apps/Agents auf dem Target]
    → localhost (fixer Port) → [Edge Node: L7-Router + Log-Ingest + CDC-Forward]
                                     │  outbound-only Sync (Mesh/Service-Token)
                                     ▼
                      [Zentrale Control Plane (Verwaltung, UI, Langfuse, Hub)]
```

**Warum (Operator-Begründung):** Production-DB-Traffic und Logs dürfen
KEINEN WAN-Roundtrip pro Query machen. Der Edge Node bedient lokal
(Alias-Routing, Log-Buffer), synct asynchron zur Zentrale (Config-Pull
und Event-Forward sind bereits im Router-WIP angelegt: pull.go +
gateway/router_config.go). Zentrale bleibt Verwaltungs-/Observability-
Fläche, Edge ist die Datenfläche.

**Verbindungssemantik:** WAN-down → Edge arbeitet weiter (Buffer +
Forward), Verwaltung eingefrort bis Sync zurückkommt — dokumentiert im
UI (Edge-Status im Networks-Tab).

**Packaging:** Edge-Node-Binary ist eins; Editionen schalten FEATURES
frei (Core: Log-Ingest/Forward; DB Pro: L7-Router/CDC lokal; Enterprise:
Hub-Tunnel). Ein Build, Runtime-Entitlement — keine separaten Downloads.

## E-Firewall — Firewall-Scope: Environment-scoped, NICHT Host-Level (Operator-approved, 13.9.2026)

**Operator-Entscheidung:** „Firewall muss nur für unsere Environments gelten.
JiMesh stellt sichere Environments bereit — die Firewall läuft NICHT auf dem
Host, sondern als Container (die NAT-Node) oder in der Control-Plane pro
Environment/Projekt, das Apps hat."

**Konsequenzen:**
1. **Host-Firewall bleibt unberührt** — UFW/iptables des Hosts sind nicht
   JiMeshs Geschäft (kein `nft` auf dem Backend-Host nötig — erklärt den
   Fund: firewall_provider.go lief `nft` LOKAL und fand nichts).
2. **Firewall = Container/Control-Plane-Komponente:** die nftables-Regeln
   leben (a) im Network-Namespace des Workspace-Containers (bereits so:
   `jimesh_egress_eth0`-Tabelle, projects_ssh.go:366) oder (b) am Edge-Node/
   NAT-Container des Environments (Sprint-36-WP6-Richtung).
3. **firewall_provider.go Ziel-Fix:** Provider-Interface bekommt ein
   Target (SSH-Target-Exec statt lokal-exec) — Capabilities/EffectiveRule
   kommen vom Environment, nicht vom Backend-Host.

---

## E-Projects — Project = Repo/Folder, Apps darin, Network-Editing (Operator, 13.9.2026)

**Operator:** „Es fehlt noch: ein Git-Repo oder ein Folder IST ein Project,
wo Apps wie DBs drinlaufen und discovered werden. Und der Network-Editing-
Tab: Networking einstellen, Bridges deployen, Container neu starten bei
Netzwerk-Änderung. Obwohl das im Compose-File geht — beides soll gehen."

**Drei fehlende Bausteine (→ BACKLOG TASK-049):**
1. **Project = Repo/Folder:** Git-Repo ODER Folder ist das Project; Apps
   (DBs, Services) laufen DARIN und werden gediscovered (Project-scoped
   Discovery statt globaler Container-Discovery).
2. **Network-Editing-Tab:** Networking pro Projekt konfigurieren
   (Bridges/Netze deployen, Alias→Netz-Zuordnung), Container-Neustart
   bei Netzwerk-Änderung (Migration-Flow: Netz ändern → betroffene
   Container reschedulen).
3. **Beide Pfade:** Compose-File UND UI-Tab führen zum selben Zustand
   (Compose-Edit bleibt Source-of-Truth-fähig, UI schreibt dieselben
   Compose-/DB-Zustände — kein zweites Schema).

## E-Priority — Managed-Ports-First: Wir verwalten Ports/Firewall für den User (BYOF später) (Operator, 13.9.2026)

**Operator:** „Was unsere App machen soll: wir verwalten die Ports und
Firewall-Rules DIREKT für den User. Er kann seine eigene Firewall mitbringen
— das kommt SPÄTER. Erstmal ist wichtig: in unseren Safe-Environments haben
wir die SIEM und werden PERMANENT gescannt. Networks aber auch Code — wir
sichern den User ab, dass er KEINE Ports offen hat für seinen DSG-Container."

**Entscheidung (Priorität):**
1. **Managed-Model jetzt:** JiMesh verwaltet Ports/Firewall-Rules direkt
   für den User (er sieht seine Rules, ändert sie nicht selbst) —
   BYOF (eigene Firewall mitbringen) = SPÄTER.
2. **Safe-Environments = SIEM + Permanent-Scan:** SIEM lebt in den
   Safe-Environments (TASK-032-Approach A JiMesh-native light) und
   scannt PERMANENT (continuous, nicht einmalig — E-SIEM greift).
3. **Zero-Open-Ports-Enforcement (DSG):** User-Container (DSG-konform)
   haben KEINE offenen Ports außer den explizit vergebenen —
   Inbound-Closure greift per Network-Namespace (nftables-Tabelle im
   Container-NS, wie Egress bereits) + NAT-Node am Edge (E-Firewall).
4. **Networks und Code:** die Absicherung gilt für Netzwerke UND den
   Code darin (beides wird gescannt — SIEM-Attribution Deployment/App/
   Project via K-LAF-Identitätskette, TASK-032).

**Consequence:** TASK-050 (Inbound-Enforcement + Permanent-Scan) wird
PRIORITY vor BYOF-Tasks; TASK-048/049-Reihenfolge bleibt.

---

## E-BYOL — Bring-Your-Own-License/Scanner-Integration (Operator, 14.9.2026)

**Operator-Quelle:** Aikido-Research (Bing, 14.9.): Aikido Zen (in-app
firewall, MIT-lizenzierte OS-Komponente), Local Scanner (on-premise,
Premium ~$700/Monat), BYOL-Prinzip (User bringt eigenes Konto, JiMesh
baut nur die technische Brücke).

**Entscheidung: BYOL als Integrationsmuster für ALLE optionalen
Drittanbieter-Security-Tools** (Aikido, CrowdSec, eigener Firewall-Provider):

1. **JiMesh integriert, User lizenziert:** Der Kunde meldet sich selbst
   beim Drittanbieter an (BYOL) — JiMesh liefert nur die Brücke:
   Settings-Feld für den Token/API-Key + Runner der die CLI/API aufruft.
   Kein Reselling, kein White-Labeling → kein Partner-Zwang.
2. **Zen (MIT) darf EINGEBETTET werden** — als Alternative zum
   handgerollten Inbound-Regelwerk am Router (TASK-050): Zen ist eine
   embedded runtime firewall die File-Access + outbound HTTP instrumentiert.
   Kann als Utility-Container pro Deployment laufen (Sprint-31-Muster).
   Vorsicht: OS-Variante ohne Dashboard; Dashboard = Aikido-SaaS.
3. **Local-Scanner (SAST/Dependency):** JiMesh stößt die Aikido-CLI im
   Kunden-Deployment an (Token des Kunden, on-premise Code bleibt beim
   Kunden, nur Metadaten-Upload). HINWEIS für Doku: Local-Scanner =
   Premium-Feature beim Kunden (~$700/Monat) — als klaren Hinweis in
   die Einstellungen dokumentieren.
4. **BYOF-Firewall-Provider:** gleiches Muster (E-Priority: Managed-First
   bleibt default, BYOF-Stub in firewall.go:26-29 ist der Ankerpunkt);
   OVS/OPNsense-Anbindung (Operator hat ovs-bridge-collection +
   opnsense-helper) = dedizierte-Box-Szenario, NICHT „any existing VPS" —
   slot in TASK-049 (Network-Editing-Tab) für Home-Lab/Bare-Metal-Targets.

---

## E-IA — Frontend-IA: 5 Haupt-Tabs + separates Admin (Operator, 14.9.2026)

**Quelle:** Claude's SPRINT-22-Drift-Analyse (4-Tab-Disziplin vom 6.9. war still
erodiert: /vault-dashboard + /control-planes landeten per Convenience in
PROJECT_BASES; Security wuchs auf 5+ Sub-Seiten ohne Sub-Nav) + Operator-
Entscheidung 14.9. („ok go go go" auf die 3 Empfehlungen).

**Die 3 Entscheidungen:**
1. **Networks/Headscale → Platform-Tab** (nicht Workspaces): die headplane-geforkte
   NetworksPage ist eine Plattform-Admin-Fläche (Mesh-User/Nodes/Keys), kein
   Workspace-Concept. SSH-Endpoints bleiben in Workspaces (Deploy-Targets).
2. **NEUER 5. Haupt-Tab „Platform"**: Control-Planes + Vault + Networks —
   Registries über „wo läuft was, was erreicht was, welche Engines". Die
   SPRINT-22-4-Tab-Disziplin wird bewusst zu 5 Tabs + separatem Admin erweitert.
3. **VaultDashboardPage gewinnt „Vault" → Platform-Tab; /security/vault wird
   „Project Secrets" → Security-Tab** (per-Project K-LAF-Laufzeit-Secrets).
   TASK-066: NICHT blind mergen — VaultPage's einzigartige Features inventarisieren,
   Secret-Listen-UX nach Security/Project-Secrets, Redirect der alten Route.

**Die Ziel-Struktur:**

| Tab | Konzept | Inhalt |
|---|---|---|
| Proxy | LLM-Kern | Config, Keys, Analytics, Logs, Models, Fallback |
| Workspaces | Was du baust | Workspaces, Apps, SSH-Endpoints, Deployments, Playground/Agents/Chat |
| Platform (NEU) | Wo es läuft & was es erreicht | Control-Planes, Vault (Engine-Registry), Networks/Mesh |
| Security | Ist es sicher | Overview, Events, Scans, Testing, Exposure, Project-Secrets |
| DBs | Daten-Layer | Backups, Discovery |
| Admin (separat, SHOW_ADMIN_NAV) | Multi-Tenancy | Users, Teams, Consumer-Keys, Budgets |

**Runtime-Presets** (dsh/python/go/node/docker/base) = App-Ebene, nicht
Workspace-Root (bereits via TASK-063 umgesetzt).

**Enforcement-Regel für alle zukünftigen Agents:** Neue Routen/Seiten landen
NIE per Convenience in der nächstgelegenen Nav-Gruppe — gegen diese Tabelle
prüfen; ein neues Konzept braucht eine bewusste Platzierungs-Entscheidung im
Sprint-File BEVOR es gebaut wird. (Lessen aus dem SPRINT-22-Drift.)
