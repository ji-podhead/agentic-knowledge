---
id: "R40"
title: "R40 — Voll-Audit: Misalignments gegen die Operator-Vision (14.9.2026)"
type: audit
date: 2026-09-13
status: final
tags: [vault, ssh, opa, gvisor, rbac]
license: CC-BY-4.0
---

# R40 — Voll-Audit: Misalignments gegen die Operator-Vision (14.9.2026)

**Quelle:** Operator 14.9. („alles kacke … ich wollte das als ganzes anders,
kompletten Audit machen was misaligned ist"). Systematischer Abgleich aller
Code-Fundstellen gegen die destillierte Operator-Vision (Sprints 34–37,
E-Entscheidungen, Chat-Logs 20260911/13).

**Operator-Vision (Kanon):**
1. JiMesh = sichere Environment für Vibe-Coding + Agents (SaaS, self-hosted)
2. Domain-Modell: Project (= Repo/Folder, Team-Sache) → SSH-Endpoint (Node-Infra) → Workspace (per-User) → Apps (Container im Workspace)
3. Router-Node = DER Security-Node pro Environment (Gateway + Firewall + Control-Plane-Edge)
4. Managed-Ports-First (Operator verwaltet, User sieht read-only; BYOF später)
5. Frontend muss das Modell abbilden — nicht 3 Sprints Kraut-und-Rüben

---

## Misalignment-Register (alle mit Fundstelle)

### M1 — gVisor-Install beim WORKSPACE statt beim NODE ❌ KRITISCH
- **Fund:** ProjectsPage.tsx:26,422,523 — `installGVisor`-Checkbox im
  Workspace-Deploy-Form; onboardInstallGVisor-Onboarding-Zustand
- **Soll:** gVisor (runsc) ist eine **NODE-Eigenschaft** (einmal pro Host
  installieren, projects_ssh.go:890-893 macht das bereits beim Node-Provision)
- **Fix:** Install-GVisor in die SSH-Endpoint-Verwaltung verschieben;
  Workspace-Preset `useGVisor` NUR als Auswahl (on/off), nie als Install-Trigger

### M2 — SSH-Endpoint-Onboarding im Workspace-Deploy-Form ❌ KRITISCH
- **Fund:** ProjectsPage.tsx:419-421 — onboardHost/onboardUser/onboardPass
  Zustände im gleichen Form wie der Deploy; 053-Agent soll das trennen,
  aber Basis war immer noch die gemischte Page
- **Soll:** 2 getrennte Pfade (053-Prompt steht; hier als Audit-Bestätigung)

### M3 — Vault: EIN globaler KV-Store, keine Project/Workspace-Trennung ✅ BEHOBEN (TASK-055, 15.9.)
- **Fund:** store/vault.go:47-61 — `vault_secrets`-Tabelle hat KEINE
  project_id/workspace_id-Spalte (DB-Check: leer); `AllowedAgents` als
  JSON-Array ist die einzige Zugangskontrolle
- **Soll (Operator: „nur ein Vault KV — nicht geklärt"):** Secrets-Trennung
  nach Project (mindestens) mit Vault-ACL je Workspace; Spalte `project_id`
  + Row-Filter; service-keys lesen nur ihr Project
- **Entscheidung (umgesetzt):** Spalte + WHERE-Filter — kein Schema-Bruch,
  bestehende AES-GCM-Encryption bleibt (R40-Empfehlung umgesetzt als TASK-055):
  - Migration: `vault_secrets` + `vault_audit_log` um `project_id`/
    `workspace_id` (`TEXT DEFAULT ''`) erweitert (idempotent, store.go-Muster);
    Legacy-Zeilen behalten `''` und bleiben Operator-erreichbar (Backward-compat)
  - Store-Layer: alle CRUD-Funktionen nehmen Project-Scope (`WHERE project_id`),
    Update/Delete mit 0 Treffern = ehrlicher Fehler statt stummem OK;
    `project_id` ist Pflicht-Feld beim Create
  - Endpoint-Layer: Scope aus authentifizierter Identität — Service-Key →
    sein project_id (read-only, `/api/vault/secrets*` + `/api/vault/access`
    im selben Middleware-Gate wie Router/Firewall-Kanäle); Dashboard-Session →
    `?project=` oder alle (Operator). NIE aus dem Body (X-Header-Kontrakt)
  - Tests: `store/vault_test.go` (Projekt A sieht B nicht — jimesh_test-DB),
    `security/vault_scope_test.go` (Service-Key-Pinning, keine Eskalation
    über `?project=`, Fail-closed für kind=user-Keys)
  - Doku: API_DOCS /api/vault-Sektion + RBAC-Absatz erweitert

### M4 — RBAC: Rollen existieren nur als Budget-Spalte, keine Zuweisungs-UI ✅ FIXED (TASK-056)
- **Fund:** project_user_budgets-Tabelle hat `role` (default 'developer') —
  aber: AdminUsersPage.tsx hat 0 role-Referenzen (105 Z. = nur enable/
  disable); Keycloak-Rollen existieren (realm_access.roles via OPA), aber
  die Project-Rollen-Zuweisung (Wer ist Developer/Viewer/Admin in Project
  X?) hat KEINE UI und keine dedizierte Route
- **Soll:** Project-based RBAC = Rollen-Zuweisung pro (project, user) —
  UI im Admin-/Workspace-Kontext; OPA-Policy kann role bereits konsumieren
- **FIX (TASK-056, 15.9.):** AdminUsersPage.tsx — jede User-Zeile aufklappbar →
  Rollen-Picker pro (User, Project) über POST /api/budgets (rbac.go schreibt
  role+budget in EINER Zeile; neue Zuweisung erhält Budget-Default 5,00 USD,
  Rollenwechsel erhält bestehende Budget-Werte; DELETE entfernt Zuweisung
  inkl. Budget mit Confirm-Hinweis); AdminBudgetsPage.tsx — ProjectRolesSection
  zeigt ALLE Zuweisungen (GET /api/budgets ohne projectId) mit inline
  editierbarer Rollen-Spalte, userId zu E-Mail aufgelöst; kanonisches
  Rollen-Set im UI admin|developer|viewer (Legacy-Rollen manager/sub_agent/
  owner bleiben sichtbar + migrierbar); i18n: 15 neue Keys in allen 60
  Locales (de übersetzt, Rest en-Fallback wie 053-Muster — check:i18n-Parität
  grün): teams.roles.viewer, admin.usersRoles*, admin.roles*,
  admin.budgetsRoles*; API_DOCS /api/budgets
  role-Feld dokumentiert. Kein Backend-Change nötig. OPA-Deny (403) zeigt
  ehrliche Inline-Meldung + Toast.

### M5 — Doppelte Routes: /projects UND /workspaces parallel ❌
- **Fund:** App.tsx:527,557 — beide Routes aktiv; ProjectsPage 2713 Z.(!)
  vs WorkspacesPage 693 Z.; Sidebar heißt weiter „Projects"
  (nav.projects, App.tsx:146)
- **Soll:** Ein Kanon: /workspaces (umbenannt), /projects wird Redirect;
  ProjectsPage-Kernfunktionen (Deploy-Form) in WorkspacesPage integrieren,
  dann ProjectsPage entschlacken (2713 Z. sind 3 Sprints Wachs)

### M6 — Firewall-Rules-UI: nur Status-Tile, kein Editor ❌
- **Fund:** grep firewall/rules in Views = 0 Treffer; SecurityExposurePage
  hat nur das read-only Status-Tile; POST/DELETE /api/firewall/rules
  (OPA-gated, 050, ef7b29b) hat NULL Frontend-Verbraucher
- **Soll:** Rules-Editor (Operator) — 053-Prompt enthält ihn

### M7 — Apps-Ebene unsichtbar ❌
- **Fund:** containers.workspace_id existiert (live, 037), aber keine View
  zeigt Apps pro Workspace als eigene Ebene
- **Soll:** Apps-Dropdown im Workspace-Detail (053-Prompt)

### M8 — Ebenen-Erklärung fehlt komplett ❌
- **Fund:** Preset-Picker zeigt „gVisor-NAT" ohne Kontext; Operator-Feedback
  wörtlich: „ich versteh das ganze frontend nicht"
- **Soll:** Ebenen-Badges (1=Sandbox/2=Egress/3=Router-Firewall) — 053-Prompt

### M9 — ProjectsPage-Größe = Wartbarkeitsrisiko ⚠️
- **Fund:** 2713 Z. — drei Sprints Parallel-Edits, uncommitted-WIP darin
- **Soll:** Nach 053-Merge: ProjectsPage auf Deploy-Kern reduzieren,
  Onboarding an Endpoints-View abgeben, Apps an WorkspacesView

### M10 — Backlog-Divergenz: Sprint-36:46-Zeile doppelt editiert ⚠️
- **Fund:** SPRINT-36-File:46/47 — alter Revert + neuer Checkoff überlappen
  (Claudes Edit hinterließ Zeilen-Reste; Sprint-36:46-48 doppelt)
- **Soll:** Zeilen 44-50 einmal sauber aufräumen

---

## Korrektheit bestätigt (NICHT misaligned — zählt auch)

| Baustein | Fundstelle | Status |
|---|---|---|
| workspaces-Tabelle (10 Spalten, UNIQUE) | Real-DB live | ✅ |
| Router-Firewall (Inbound-DROP + Grants OPA-gated) | firewall.go ef7b29b | ✅ |
| Service-Keys (kind=service, Workspace-Bindung) | consumer_keys d36c62e | ✅ |
| OPA embedded (Rollen aus Keycloak) | policy.go, live | ✅ |
| Egress (nftables im NS) | projects_ssh.go:1662 | ✅ |
| K-LAF-Attribution (X-Header, /api/sdk/logs) | auth.go, sdklogs | ✅ |

## Abgeleitete Fix-Reihenfolge

1. **053 laufend lassen** (trennt M2, M5-teilweise, M6, M7, M8)
2. **M1 nachziehen:** gVisor-Install → Endpoint-Verwaltung (054-Follow-up
   oder Mini-Task; projects_ssh.go macht es ohnehin beim Node-Provision —
   nur die Checkbox-Täuschung im Frontform entfernen)
3. ~~**M3 Vault-Trennung:** neuer Mini-Task (Spalte + Filter + ACL-Klärung) —
    Entwurfs-Entscheidung beim Operator~~ **✅ erledigt als TASK-055 (15.9.):
    Spalte + WHERE-Filter umgesetzt, Service-Key-Scope aus authentifizierter
    Identität, Legacy-Secrets Operator-erreichbar (Details im M3-Eintrag)**
4. ~~**M4 Rollen-Zuweisungs-UI:** AdminUsersPage erweitern (role-Picker) +
    Route POST /api/budgets (rbac.go existiert!) verdrahten~~ **✅ erledigt
    als TASK-056 (15.9.): AdminUsersPage-Rollen-Picker pro (User, Project)
    + AdminBudgetsPage-Rollen-Spalte inline editierbar (Details im
    M4-Eintrag)**
5. **M9/M10 Aufräumen** nach 053-Merge

---

## R40-Anhang A — AIM-Vergleich (opena2a/agent-identity-management, 14.9.)

**Fund:** Apache-2.0, Go/Python/Java/TS, 60★, aktiv (Stand 12.9.).
Cryptographic identity + capability authorization + audit trails für
non-human Identitäten.

**Verdict: Referenz + selektiver Import, NICHT Ersatz für unseren Stack.**

| AIM-Feature | Haben wir? | Bewertung für JiMesh |
|---|---|---|
| Ed25519-signierte Agent-Identitäten | Nein (Bearer-Tokens) | Interessant für v2 — unser Service-Key-Modell ist einfacher und funktioniert; Ed25519 wäre Upgrade-Pfad |
| **Capability-Grants per Tool-Call** (`@perform_action(capability="db:read")`) | **NEIN — Epic-3-WP3-Lücke!** | **Das Beste an AIM.** Genau unser fehlendes Tool-Call-Gating — R12 hat's geplant, nie gebaut. Muster übernehmen: Capability-String (namespace:action) als Rego-Policy-Input |
| 5-Schritt-FGA (Capability→Attribute→Context→Chain→Intent) | Nein (OPA 1-Step) | Overkill für v1; Intent-Check (NanoMind 3M lokal) ist aber ein schönes Muster für K-LAF WP2-Variante |
| 9-Faktor-Trust-Scoring | Nein | R21/DAP-Skill-Score-Vorlage passt dazu — später |
| **JIT-Access mit Human-Approval** (Pause bis Dashboard-Freigabe) | **NEIN — aber R21/DAP GUARDED-Approval-Queue ist genau das!** | Muster übernehmen für Epic 18 |
| SIEM-Adapter (Splunk/Sentinel) | Wir haben /api/sdk/logs | Unser Kanal ist allgemeiner (ein Schema) |
| MCP-Attestation (Multi-Agent-Consensus) | Nein | Later — supply-chain für Skills |
| NanoMind-Classifier (3M, lokal, Intent) | Wir haben Llama Guard via Mesh (73a21b9) | Verschiedene Ansätze — ihres ist leichter (Intent), unseres breiter (Content) |

**Konsequenz:** AIM NICHT als Framework einbinden (wir haben Identity-Stack
schon: Service-Keys + OPA + Keycloak + X-Header). ABER: das
Capability-String-Muster (`namespace:action` + risk levels) als Rego-Policy-
Input für Epic-3-WP3 (Tool-Call-Gating für Subagents/DB/MCP) übernehmen —
+ JIT-Approval-Muster als Implementierungs-Vorlage für die GUARDED-Queue
(R21 §6, Epic 18). In BACKLOG: Epic-3-WP3-Zeile mit AIM-Referenz ergänzen.

---

## R40-Anhang B — Quick-Deploy-Modal (Operator-Idee, 14.9.)

**Operator:** „Unten in der Sidebar nur ein Plus-Icon für Deploy-Zeug — das
macht ein Modal auf. Wenn man deployed und Workspace oder SSH-Target nicht
da ist, kann man das GLEICH MIT-ERSTELLEN oder Preset wählen."

**Konzept (ergänzt 053 — hebt die Trennung NICHT auf):**
- Sidebar unten: [+] → Quick-Deploy-Modal
- Modal-Flow: App wählen/erstellen → Workspace wählen ODER inline-anlegen
  (falls keine da) → SSH-Target wählen ODER inline-onboarding (falls keines
  da) → Preset wählen → Deploy
- Die getrennten Verwaltungs-Sichten (Endpoints-Page, Workspaces-Page)
  bleiben — das Modal ist der Convenience-Einstieg, der bei fehlenden
  Entitäten inline zum Erstellen anbietet
- Implementation: nach 053-Merge als Ergänzung (gleiche Komponenten, die
  053 baut — Selects + Inline-Create-Forms wiederverwenden)
