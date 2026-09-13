---
okf_version: "1.0"
id: "okf-fro-per-frontend-performance-audit"
title: "R39 — Frontend-Slop-Audit + Lücken-Register (Requirement)"
topic: "general/frontend-and-ui-architecture"
subtopic: "performance-and-rendering"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - frontend-and-ui-architecture
  - performance-and-rendering
summary: "**Datum:** 14.9.2026 · **Agent:** Requirement (Dokumentier-Lane, nur docs/) · **Basis:** Arbeitsbaum `main` @ commit-hash + Live-Stack (Backend :19091, Fro"
---

# R39 — Frontend-Slop-Audit + Lücken-Register (Requirement)

**Datum:** 14.9.2026 · **Agent:** Requirement (Dokumentier-Lane, nur docs/) · **Basis:** Arbeitsbaum `main` @ commit-hash + Live-Stack (Backend :19091, Frontend :19090, authentifiziertes Live-Curl with Admin-Session)

**Methode:** Voll-Lektüre aller 29 Views (`src/frontend/src/views/*.tsx`) gegen die komplette Backend-Route-Inventur (`HandleFunc` about `src/backend/internal/**`), authentifizierte Live-Curl-Checks on jeden verdächtigen Pfad, i18n-Key-Kreuzcheck (alle `t('…')`-Nutzungen vs. `de.json`/`en.json`), Git-Archäologie for jede Planungs-Behauptung (Roadmap, Milestone, Requirement ee7055b). Jede Behauptung with Datei:Zeile; negative Funde explizit. **Live-Curl-Beleg for die Zentrale-Aussage:** unauthentifiziert antwortet die Auth-Middleware (the Backend Gateway Core:576-655`) on *jeden* /api-Pfad with 401 — deshalb wurden alle Route-Checks authentifiziert wiederholt.

---

## 1) Summary

| Kategorie | Zahl |
|---|---|
| Views gesamt | 29 |
| **OK** (echte Daten, ehrliche Zustände, no Slops) | 19 |
| **Lücke** (geplant-vs-gebaut fehlt, i18n/Theme-Lücken, Register-Einträge) | 8 |
| **Slop** (Mandat-2-nah: Fake-Success, fabrizierte Kontrollen, unverbundene UI, falsche Verification) | 2 Views / 6 Funde |
| Dead-Code-Komponenten (not importiert) | 4 Dateien, 878 Z. (davon 1 with 5×404-Routen) |
| Backend-Routen without Frontend-Verbraucher (Lücken-Kandidaten) | 10+ |
| 051-in-flight **P0-Blocker** (noch uncommittet) | 1 ( Klartext-SSH-Credentials im Quellcode ) |

Die Codequalität der Security- and Admin-Views ist hoch (echte Queries, ehrliche Empty/Error-States, konsequente No-Mock-Kommentare). Die Slops konzentrieren sich on die ältere Playground-Welt (`the Workspace Management View`, `the Network Management View`) and on **falsch abgehakte Planungs-Zeilen** — drei dokumentierte Behauptungen (Milestone-Work Package-Filter, „DiscoveryPage 730Z live", „Networks live 200/200/200") halten der Codeprüfung not stand.

---

## 2) View-Register (29 Views — Status · Fundstelle · Fix · Priorität)

Legende: **P0** = Commit-Blocker/Security · **P1** = kaputte/sichtbar falsche Funktion · **P2** = geplante Lücke · **P3** = Konsistenz.

### OK (19) — negative Funde gezählt, nichts fabriziert

| View | Z. | Beleg (Stichprobe) |
|---|---|---|
| AnalyticsPage | 1178 | `/api/profiles`,`/api/models`,`/api/fallback/token-usage` (491,497,582) + CostDashboard `/api/cost/*` — alle Routen live 200; i18n stark (129 t-Zeilen) |
| AudioPage / ImagePage / VideoPage | 5 | Wrapper → MediaModelsView (`/api/media` live 200) |
| BackupsPage | 18 | BackupsPanel shared; `/api/backups` live 200 |
| AdminLayout | 45 | reine Nav (4 Tabs, App.tsx:530-536) |
| AdminBudgetsPage | 17 | BudgetsSection; `/api/budgets` live 200 |
| the User Management View | 105 | echte Mutation `/api/users/{id}/enabled` (41-44); live 200 |
| ConsumerKeysPage | 402 | `/api/consumer-keys` + `/revoke` (134,168) live 200; i18n 48 |
| EmbeddingDetailPage | 147 | `/api/embeddings`+`/usage`+api-key live 200 |
| EmbeddingsPage | 248 | ehrliche No-Mock-Kommentare (23, 112: „read-only badge statt fake Switch") |
| FusionPage | 333 | `/api/fallback`+`/api/settings/fusion|unify` — Routen existieren |
| KeysPage | 315 | `/api/keys*`, `/api/health/check-all` live 200; i18n for Headstrings |
| MediaDetailPage | 124 | echtes PUT `/api/media/{id}` (35) |
| ModelDetailPage | 768 | alle Routen echt; OpenRouter-Katalog-Fetch (73-75) ist öffentliches Live-Enrichment, degradiert ehrlich on null |
| NotFoundPage | 24 | i18n, echter Link |
| PremiumPage | 248 | `/api/premium/key|portal|sync` live 200 |
| SecurityEventsPage | 135 | `/api/security/events` live 200; Fehler/Empty ehrlich (63-79); detail als inertes Text-Node (120-124, Injektions-Schutz) |
| TeamsPage | 413 | echte CRUD `/api/teams`,`/api/team-members` (81,93,137,150) live 200 |
| VaultPage | 623 | echte Secrets-CRUD + Token-Issue + Audit (120-134, 241-248, 331, 480-481) live 200; Token „shown exactly once"-Idiom (321-323) |

### SLOP (2 Views, 6 Funde)

#### 🔴 the Network Management View (120 Z.) — unverbundene UI + falsche Backend-Behauptung

| # | Finding | Fundstelle | Fix | Prio |
|---|---|---|---|---|
| S1 | **Drei Fetches on nichtexistierende Routen** `/api/networks/{users,nodes,preauthkeys}` | `views/the Network Management View.tsx:29-33` — authentifizierter Live-Curl: **404/404/404** („404 page not found"); Route-Nirgends-Registrierung: `grep HandleFunc` about `src/backend/internal/**` = 0 Treffer for `api/networks` | Headscale-Proxy-Routen im Gateway bauen (GET /api/networks/* → Headscale-API, wie im Kommentar beschrieben) **or** Seite entfernen | **P1** |
| S2 | **Kommentar behauptet Backend, das not existiert**: „Echte Daten … via /api/networks/* Backend-Proxy — Backend liest HEADSCALE_URL + HEADSCALE_API_KEY from .env" | `views/the Network Management View.tsx:9-11` | Kommentar streichen, bis das Backend existiert | P1 |
| S3 | **Falsche Verification im Task-036-Commit**: „… Backend-Proxy … — live 200/200/200" | Prior Commit (Message); berührt **nur 5 Frontend-Dateien, no Backend-File** (`git history check

Positiv (no Fake-Data-Slop): Die Fehler-UI ist ehrlich — `loadError`-Banner statt erfundener Zahlen (`the Network Management View.tsx:37-38,61-63`). Aber: **Sichtbarkeits-Lücke**: `/networks` ist in keiner Nav-Gruppe (`App.tsx:90-93,126-155`) and not im Command-Palette-Seitenindex (`components/command-palette.tsx:108-121`) — nur per Direkt-URL erreichbar.

#### 🔴 the Workspace Management View (HEAD 1881 Z.) — Fake-Success ×2 + fabrizierte Log-„Kontrolle"

| # | Finding | Fundstelle | Fix | Prio |
|---|---|---|---|---|
| S4 | **„Successfully connected remote Workspace Node" without Verbindung**: `handleCreateNode` fügt nur ein localStorage-Objekt hinzu — no einziger Netzwerk-/SSH-Call — and toastet trotzdem Erfolg | `HEAD views/the Workspace Management View:443-472`, Toast: `:465` | Ehrlich machen: „Node hinzugefügt (Verbindung wird beim ersten Deploy geprüft)" or echter SSH-Preflight (Muster: `/api/nodes/provision`, das existiert) | **P1** |
| S5 | **Fabrizierte Deploy-Terminal-Logs**: der Deploy selbst ist echt (POST `/api/projects/deploy`, `:532+`), aber die „Terminal build log emulation" (`:322`) schreibt nachträglich klient-seitig eine erfundene Erfolgsstory: „[ssh] Authenticated successfully", „[env] Verified environment dependencies. Docker active." (`:570-571`), „[ok] … 100% success!" (`:584`) — Steps, die das Frontend not beobachtet hat | `HEAD views/the Workspace Management View:322,570-584` | echtes Server-Log-Streaming (SSE, Muster existiert: `/api/agents/logs/stream`, `analytics.go:41`) or Zeilen als „Summary der Server-Antwort" kennzeichnen | **P1** |
| S6 | **„Project settings saved successfully!" without Persistence**: `handleUpdateProject` without Re-Deploy schreibt nur localStorage and toastet Erfolg; es existiert **no** Backend-Route for Project-Updates (Backend hat nur GET-Liste `projects_ssh.go:1816-1852` + DELETE `:1857-1873`; anlegen/updaten läuft ausschließlich about deploy/redeploy) | `HEAD views/the Workspace Management View:240-274` (Toast `:267`), localStorage `:336-365` | PUT/POST `/api/projects` im Backend ergänzen **or** Toast ehrlich on „lokal gespeichert — Redeploy übernimmt" umformulieren; Liste zusätzlich from GET /api/projects hydratisieren (Backend hat die Zeilen in PostgreSQL) | **P1** (Mandat 3: „must round-trip to PostgreSQL") |

Zusatz-Finding (Security, HEAD): SSH-Node-Credentials (sshPassword/sshKey) liegen **im Klartext im localStorage** (`HEAD:22,316,458-459` + Persistence-Effect `:361`) — Umgehung der Vault-Pflicht (Mandat 9). Fix: Nodes-Credentials via `/api/vault/*` referenzieren, localStorage without Secrets halten. **P1.**

### LÜCKE (8 Views)

| View | Lücke | Fundstelle | Fix | Prio |
|---|---|---|---|---|
| **AgentsPage** (183 Z.) | **Milestone-Work Package-Filter fehlen komplett**: „[x] Frontend: Agents-Tab bekommt Filter-Dropdowns (endpoints, apps, sessions, agents)" — falsch abgehakt; no einzige Filter-Control in der Datei; Commit ee7055b hat AgentsPage **nie** berührt (`git history check
| **LogsPage** (15 Z.) | **SDK-/Audit-Logs-UI fehlt komplett** (041-Welle, Requirement): `GET /api/sdk/logs?type=&level=&workspace=&session=&agent=&range=&limit=` ist live 200 (verify), hat **0** Frontend-Verbraucher (grep about src) | Backend-Filterfläche: `internal/sdklogs/sdklogs.go:247-263`; Fehlen: `views/LogsPage.tsx` (nur RealtimeLogs, konsumiert `/api/agents/logs/stream` ✓) | SDK-Logs-Ansicht with Filter-Dropdowns + type=audit/agent/app-Tabs (→Requirement, in Arbeit) | **P1** |
| **DiscoveryPage** (22 Z.) | **Empty-State-Text ist falsch veraltet**: „Discovery / Debezium ist noch not gebaut" — Container-Discovery existiert and ist live (`GET /api/discovery` → `{"containers":[],"count":0}`, 200; konsumiert von SecurityExposurePage:310). Nicht gebaut ist nur **DB**-Discovery/Debezium-CDC. Zudem: Roadmap-Zeile „041 … DiscoveryPage 730Z live" ist falsch — die Datei war in ihrer ganzen Git-Historie immer 22 Z. (nur Commit 3d81c07) | UI-Text: `de.json` `admin.discoveryEmptyTitle/Description`; falscher Kommentar: `App.tsx:118-124`; falsche Roadmap-Zeile: `docs/backlog/Roadmap.md:9` | Empty-State on den wahren Scope (DB/CDC) umformulieren; Roadmap:9 korrigieren; DB-Discovery-UI = own 041-Aufgabe | **P2** |
| **OnboardingPage** (491 Z.) | **i18n = null**: 0 t()-Nutzungen in 491 Z. (hartcodierte EN-Strings `:81-87` usw.) | ganze Datei | i18n de/en nachziehen | P2 |
| **FallbackPage** (992 Z.) | **i18n-Notstand**: 992 Z., nur 2 t()-Zeilen (Hauptseite /config!); **Theme-Breaks**: rose/emerald without `dark:`-Varianten | i18n: ganze Datei; Theme: `:451,585,733,798,819,856` | i18n-Welle + `dark:text-*` ergänzen | P2 |
| **SecurityExposurePage** (1086 Z.) | (a) **E-Priority Rule-Management-UI fehlt**: FirewallStatusTile ist read-only Capabilities/Version/Tabellen (`:574-678`) — der User sieht seine *manage*dten Rules not („der User SIEHT seine Rules", Requirement). (b) i18n-Lücke: Hierarchy-Selector komplett hartcodiert EN | (a) `:574-678`; (b) `:320-365` („Project:", „All Projects", „Endpoint:" …) | Rules-Ansicht (read-only Liste der effektiven Rules) ergänzen; Selector i18n'n | (a) **P1** (⚡E-Priority) · (b) P3 |
| **SecurityReportPage** (449 Z.) | **Sichtbarer i18n-Bug**: `t('securityReport.requestLogCard.none')` (`:363`) ist in **allen 60 Locales** not definiert — t() gibt den Roh-Key zurück (`I18nProvider.tsx:212`), d.h. die UI zeigt wörtlich „securityReport.requestLogCard.none" | `views/SecurityReportPage.tsx:363`; Locale-Befund: 60/60 Dateien without `requestLogCard.none` (nur `title` existiert) | Key in en/de (+ andere) nachtragen | **P2** (sichtbarer Bug on shipped 042-Feature) |
| **VaultPage** (623 Z.) | **Vault-RBAC-Verwaltungs-UI fehlt** (Backlog:356: „RBAC-Kette … neu zu bauen ist nur die Verwaltungs-UI"): no Rollen-Verwaltung (JWT-roles/OPA/K8s-Role-Labels) irgendwo im Frontend — nur allowedAgents pro Secret (`:144-161,222-248`) and AdminUsers-Enabled-Toggle | Fehlen quer about alle Views; Referenz `docs/backlog/Roadmap.md:356` | RBAC-Rollen-Verwaltungs-UI (Admin-Bereich) planen/bauen | P2 (Register) |

---

## 3) Dead-Code-Funde (Komponenten; Views ausgeschlossen)

Import-Check about den gesamten `src/frontend/src` (0 Referenzen = dead):

| Datei | Z. | Befund |
|---|---|---|
| `components/DiscoveryStatus.tsx` | 460 | **Dead + gefährlich**: nie importiert; ruft 5 Routen, die **not existieren** — `/api/discovery/new` (`:90`), `/new-providers` (`:100`), `/auto-add` (`:121`), `/scheduler/start` (`:133`), `/scheduler/stop` (`:144`) — alle authentifiziert **404** live verifiziert. Buttons (Auto-Add, Scheduler Start/Stop) wären tote Kontroll-UI. **Löschen** (R33-Discovery-UI wird ohnehin neu geplant). |
| `components/getting-started.tsx` | 178 | nie importiert — löschen or reaktivieren |
| `components/peak-hours-controls.tsx` | 126 | nie importiert |
| `components/custom-weights-popover.tsx` | 114 | nie importiert |
| **Negativ-Finding (no Dead Code):** `RealtimeMonitor.tsx` (11.5k, Sep 3) + `RoutingAnalytics.tsx` (12k, Sep 3) | — | verdrahtet in `App.tsx:35-36` + Routen `App.tsx:519-520` — **OK**, bestätigt die 13.9.-Vorfunde. |

---

## 4) Geplant-vs-gebaut-Register gegen die Referenz-Sources

| Referenz | Geplant | Gebaut (Befund) | Status |
|---|---|---|---|
| **Handoff-Map 040–042** (`HANDOFF-2025-09-13…:57`): DB-Discovery-UI + Audit-Logs, Security-Report-Tab, Preset-Picker | 3 Wellen-Items | DB-Discovery-UI: **fehlt** (DiscoveryPage = Empty-State); Audit-Logs-UI: **fehlt** (0 Verbraucher von /api/sdk/logs); Security-Report-Tab: **gebaut** (SecurityReportPage 449Z, Route live — Roadmap „[x]" stimmt); Preset-Picker: **gebaut als Runtime-Picker** (RUNTIMES, HEAD:49-59 + Picker HEAD:1426,1695; Backend nimmt `runtime` echt an) | 2/4 fehlen |
| **Milestone-Work Package-Frontend-Zeile** (`Milestone:46`): Agents-Tab-Filter-Dropdowns, „[x]" | Filter-UI | **not gebaut**, Haken falsch (ee7055b hat AgentsPage nie berührt) | ❌ falsch abgehakt |
| **R33-Blueprint-Presets** (§3.B.1): gVisor-NAT (default, empfohlen) / Airgap / Host-Passthrough **with rotem Warning-Badge** | Network-Presets im Project-Create | **HEAD: 0** (`networkMode` kommt in HEAD not before); **051-in-flight (Arbeitsbaum)**: Network-Mode-Select gebaut (wt `:2077-2086` + NAT/gVisor-Toggles `:2089-2119`), Backend echt verdrahtet (`projects_ssh.go:61,1118,1460`) — aber das **rote Warning-Badge** for Host-Passthrough fehlt weiterhin | in Arbeit; Badge fehlt |
| **R33 §4.2 Tunnel-Mandat**: iframe-Zugriffe strikt about `/api/{workspaces}/projects/{id}/tunnel/{port}` | Tunnel-only | **HEAD: direkt** `http://host:port` (`HEAD:802-813`), Backend-Tunnel-Route existiert with 0 HEAD-Verbrauchern; **051-in-flight**: Tunnel-URLs + `?token=`-Param gebaut (wt `:972-995`), backend-seitig gedeckt through `bearerToken`-Query-Fallback (`auth.go:403-413`) | in Arbeit (HEAD = Lücke) |
| **E-Projects-Network-Editing-Tab** (Requirement, Roadmap:483): Bridges deployen, Alias→Netz-Zuordnung, Container-Neustart at Netz-Änderung | Editing-Tab | **fehlt komplett** — the Network Management View ist read-only + 404; `/api/router/config` (Router-Alias-Verwaltung, Requirement) hat **0** Frontend-Verbraucher | ❌ |
| **E-Priority (Managed-Ports-First)** (Roadmap:16/24, Requirement): „wir verwalten Ports … der User SIEHT seine Rules" — **Rule-Management-UI fehlt** laut Auftrag | Rules-Ansicht | **fehlt** — FirewallStatusTile zeigt nur Provider-Capabilities + Regel-**Anzahl** (`SecurityExposurePage.tsx:574-678`); Port-Zuweisungs-UI existiert partiell (`/api/projects/{id}/ports/assign` wird von SecurityExposurePage-Kontext genutzt) | ❌ P1 |
| **E-Firewall** (Roadmap:23: WAF-Container pro Deployment, NAT-Node am Edge) | Firewall-UI-Fläche | WAF-Integration noch not begonnen (Roadmap:19 „Plan fertig, NICHT begonnen"); Frontend-Fläche not existent — konsistent with Plan | ⬜ geplant |
| **Vault-RBAC-Verwaltungs-UI** (Backlog:328/346→356: „neu zu bauen ist nur die Verwaltungs-UI") | Rollen-UI | **fehlt** (nur allowedAgents + Enabled-Toggle); Backend-RBAC-Kette ebenfalls offen | ❌ |
| **Epic-3-Work Package SSE-Progress-Panel** (Roadmap:28) | Subagent-Progress-SSE-Panel | **fehlt** — `/api/orchestrate*` (+ SSE) existiert im Backend (Backlog:166 „[x] Work Package: Orchestration endpoint (SSE…)"), **0** Frontend-Verbraucher (grep) | ❌ |
| **042 Security-Report-Tab** | Route + View | gebaut & live (`/security/events/:id`, App.tsx:538; GET `/api/security/report/{id}` `:153`) | ✅ |

**Backend-Routen without Frontend-Verbraucher** (Lücken-Kandidaten, grep-gesichert, Stand HEAD): `/api/sdk/logs` + `/api/sdk/sessions` (051 baut), `/api/analytics/by-workspace` (051-Plan), `/api/router/config` (Router-Verwaltung), `/api/orchestrate{,/cancel,/history}` (Epic-3-Work Package), `/api/projects/task/{start,status,apply,discard}` (HITL-Worktrees), `/api/exec/sandbox`, `/api/experts*`, `/api/agent-types`, `/api/model-roles` + `/api/chains/{id}/model-roles`, `DELETE /api/projects/{id}` (bewusst UI-los, Kommentar `projects_ssh.go:1854-1856`). Verbraucht and OK u.a.: `/api/compression/*` (2 Dateien), `/api/cost/daily` (CostDashboard:130), `/api/dedup`, `/api/client-profiles`, `/api/free-tier`.

---

## 5) Konsistenz: i18n & Theme

**i18n-Deckung** (t()-Zeilen / Gesamtzeilen; Auffällige):

| View | Verhältnis | Bewertung |
|---|---|---|
| FallbackPage | 2 / 992 | **Notstand** (Hauptseite!) |
| the Workspace Management View (HEAD) | 3 / 1881 | **Notstand** (Playground-Hauptseite) |
| OnboardingPage | 0 / 491 | **komplett unübersetzt** |
| LogsPage | 0 / 15 | Header hartcodiert EN (`:8-9`) + Slop-Kommentar „fully functional" (`:12`) |
| SecurityExposurePage | 63 / 1086 | gut, aber Selector-Block `:320-365` hartcodiert EN |
| KeysPage | 10 / 315 | ausreichend (Sections tragen own i18n) |

**Key-Bug:** `securityReport.requestLogCard.none` fehlt in 60/60 Locales → UI zeigt den Roh-Key (Fundstelle oben). Sonst sind alle 1046 benutzten Keys in de+en definiert (Kreuzcheck, false-positive-bereinigt).

**Theme-Breaks (without dark:-Variante):** `FallbackPage:451,585,733,798,819,856` (rose/emerald); `the Network Management View:94` (bg-zinc-400 Offline-Punkt). Positiv: SecurityReportPage benutzt konsequent `dark:`-Varianten (`:108-112`).

---

## 6) 051-in-flight (Arbeitsbaum, uncommittet) — Warnung for Review/Merge

1. **P0-BLOCKER — Klartext-SSH-Credentials im Quellcode:** Arbeitsbaum the Workspace Management View:388-390`: `onboardHost='[REDACTED-TS-IP]'`, `onboardUser='[REDACTED-USER]'`, **`onboardPass='[REDACTED-SSH-PASS]'`** (als useState-Defaults des Onboarding-Wizards). Enthält echte IP (Tailscale-Range), User and ein realistisches Passwort — würde ins Bundle and den Git-Verlauf wandern. Verstoß gegen Mandat 9 (Secrets niemals Klartext). **Vor jedem 051-Commit: löschen, leere Defaults + Passwortfeld.** (In HEAD not enthalten — eingeführt im 051-Diff, `git diff` Zeilen 106-108.)
2. Token-in-URL (`?token=<session>`, wt `:972-974`): for iframe nötig and backend-gedeckt (`auth.go:403-413`), aber Session-Token landet in Access-Logs/History — später on kurzlebige scoped Tunnel-Tokens umstellen (Beobachtung, P3).
3. Positiv: Network-Presets + Tunnel-iFrame + WS-Proxy (`vite.config.ts` `ws:true`) schließen genau die R33-Lücken — Review-Fokus: Host-Passthrough rotes Badge (fehlt), Credential-Blocker (oben).

---

## 7) TOP-10-Fix-Liste for die nächste Frontend-Welle

1. **P0 — 051-Commit-Blocker:** Klartext-SSH-Credentials from dem Arbeitsbaum entfernen (the Workspace Management View wt:388-390) — sonst not mergen (Mandat 9).
2. **P1 — the Network Management View backenden or entfernen:** `/api/networks/{users,nodes,preauthkeys}` als echte Headscale-Proxy-Routen bauen (Kommentar 9-11 einlösen) and `/networks` in Nav+Palette verdrahten — aktuell 404-end-to-end (live bewiesen) and unsichtbar.
3. **P1 — SDK-/Audit-Logs-UI (Milestone-Kern, 051):** GET `/api/sdk/logs` with type/level/workspace/session/agent-Filtern + audit/agent/app-Tabs in LogsPage/AgentsView; daneben `/api/analytics/by-workspace`.
4. **P1 — Milestone:46-Haken ehrlich rückgängigen** (Agents-Filter nie gebaut) and Roadmap:9 korrigieren („DiscoveryPage 730Z live" war nie wahr) — Mandat 1/5.
5. **P1 — the Workspace Management View Fake-Success entschlacken:** „Successfully connected" without Verbindung (HEAD:465) and fabrizierte Deploy-Log-Story (HEAD:570-584) through ehrliche Texte/echtes SSE-Log-Streaming ersetzen; SSH-Node-Secrets from localStorage in Vault-Referenz.
6. **P1 — Mandat 3 runden:** PUT/POST `/api/projects` (Persistence-Route) + Projektliste from GET /api/projects hydratisieren statt nur localStorage (HEAD:240-274,336-365); Toast-Wortlaut anpassen.
7. **P1 — E-Priority Rule-Management-UI (Requirement, ⚡):** FirewallStatusTile um die effektiven Rules des llm-mesh-gateway-Tables erweitern (read-only for den User, verwaltet through Control-Plane) — Fundstelle SecurityExposurePage.tsx:574-678.
8. **P2 — i18n-Key-Bug:** `securityReport.requestLogCard.none` in en/de (+ weitere Locales) nachtragen (SecurityReportPage.tsx:363 zeigt heute den Roh-Key).
9. **P2 — Dead-Code-Aufräumwelle:** `DiscoveryStatus.tsx` (460 Z., 5×404-Routen), `getting-started.tsx`, `peak-hours-controls.tsx`, `custom-weights-popover.tsx` löschen (878 Z.); LogsPage-Header i18n'n + „fully functional"-Kommentar entfernen.
10. **P2 — i18n-/Theme-Welle:** FallbackPage (992/2) + the Workspace Management View (1881/3) + OnboardingPage (491/0) übersetzen; SecurityExposurePage-Selector (320-365); FallbackPage dark:-Varianten (451,585,733,798,819,856); in 051s neuem Network-Picker das R33-roten Host-Passthrough-Warning-Badge ergänzen.

*(Größere Register-Lücken — E-Projects-Network-Editing-Tab, Vault-RBAC-Verwaltungs-UI, Epic-3-Work Package-SSE-Panel, DB-Discovery-UI — sind planbare Features (Requirement/050, Backlog:356, Backlog:28) and gehören in die Planung, not in die Fix-Welle.)*

---

## 8) Fundstellen-Zählung

- **Slop-Funde: 6** (S1 the Network Management View unbound-Trio · S2 false Backend-Kommentar · S3 false „live 200"-Verification · S4 Fake-„Successfully connected" · S5 fabrizierte Deploy-Logs · S6 „saved" without Persistence) + 1 P0-in-flight (Credentials, uncommittet)
- **Lücken: 11** (SDK-Logs-UI · Work Package-Filter · R33-Network-Presets+Badge · R33-Tunnel-am-HEAD · E-Projects-Network-Editing-Tab · E-Priority-Rule-Management-UI · E-Firewall-UI-Fläche · Vault-RBAC-Verwaltungs-UI · Epic-3-Work Package-SSE-Panel · DB-Discovery-UI/DiscoveryPage-Stale-Claim · by-workspace-Kostenansicht)
- **i18n/Theme: 9** (requestLogCard.none-Bug · 4 Notstands-Views · SecurityExposure-Selector · LogsPage-Header · FallbackPage-Theme · the Network Management View-Theme-Punkt)
- **Dead Code: 4** Komponenten (878 Z.), davon 1 with 5×404
- **Pro View: OK 19 · Lücke 8 · Slop 2** (29 Views; RealtimeMonitor+RoutingAnalytics bestätigt OK/verdrahtet)

*Alle Route-Status dieser Audit-Runde wurden am Live-Stack authentifiziert verifiziert (200/404 wie angegeben); no Build wurde angestoßen (13.9.-Lesson: no `next build`/`npm run build` neben dem Dev-Server).*
