---
okf_version: "1.0"
id: "okf-sec-gua-llm-misalignment-audits"
title: "R40 — Voll-Audit: Misalignments gegen die System Administrator-Vision (14.9.2026)"
topic: "general/security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - security-and-observability
  - guardrails-and-firewalls
summary: "**Source:** System Administrator 14.9. („alles kacke … ich wollte das als ganzes anders,"
---

# R40 — Voll-Audit: Misalignments gegen die System Administrator-Vision (14.9.2026)

**Source:** System Administrator 14.9. („alles kacke … ich wollte das als ganzes anders,
kompletten Audit machen was misaligned ist"). Systematischer Abgleich aller
Code-Fundstellen gegen die destillierte System Administrator-Vision (Sprints 34–37,
E-Decisionen, Chat-Logs 20260911/13).

**System Administrator-Vision (Kanon):**
1. The Multi-Provider Gateway = sichere Environment for Vibe-Coding + Agents (SaaS, self-hosted)
2. Domain-Modell: Project (= Repo/Folder, Team-Sache) → SSH-Endpoint (Node-Infra) → Workspace (per-User) → Apps (Container im Workspace)
3. Router-Node = DER Security-Node pro Environment (Gateway + Firewall + Control-Plane-Edge)
4. Managed-Ports-First (System Administrator verwaltet, User sieht read-only; BYOF später)
5. Frontend muss das Modell abbilden — not 3 Sprints Kraut-and-Rüben

---

## Misalignment-Register (alle with Fundstelle)

- **Finding:** the Workspace Management View:26,422,523 — `installGVisor`-Checkbox im
  Workspace-Deploy-Form; onboardInstallGVisor-Onboarding-Zustand

  installieren, projects_ssh.go:890-893 macht das bereits beim Node-Provision)
- **Fix:** Install-GVisor in die SSH-Endpoint-Verwaltung verschieben;
  Workspace-Preset `useGVisor` NUR als Auswahl (on/off), nie als Install-Trigger

- **Finding:** the Workspace Management View:419-421 — onboardHost/onboardUser/onboardPass
  Zustände im gleichen Form wie der Deploy; 053-Agent soll das trennen,
  aber Basis war immer noch die gemischte Page

- **Finding:** store/vault.go:47-61 — `vault_secrets`-Tabelle hat KEINE
  project_id/workspace_id-Spalte (DB-Check: leer); `AllowedAgents` als
  JSON-Array ist die einzige Zugangskontrolle
- **Soll (System Administrator: „nur ein Vault KV — not geklärt"):** Secrets-Trennung
  after Project (mindestens) with Vault-ACL je Workspace; Spalte `project_id`
  + Row-Filter; service-keys lesen nur ihr Project
- **Decision (umgesetzt):** Spalte + WHERE-Filter — no Schema-Bruch,
  bestehende AES-GCM-Encryption bleibt (R40-Recommendation umgesetzt als Requirement):
  - Migration: `vault_secrets` + `vault_audit_log` um `project_id`/
    `workspace_id` (`TEXT DEFAULT ''`) erweitert (idempotent, store.go-Muster);
    Legacy-Zeilen behalten `''` and bleiben System Administrator-erreichbar (Backward-compat)
  - Store-Layer: alle CRUD-Funktionen nehmen Project-Scope (`WHERE project_id`),
    Update/Delete with 0 Treffern = ehrlicher Fehler statt stummem OK;
    `project_id` ist Pflicht-Feld beim Create
  - Endpoint-Layer: Scope from authentifizierter Identität — Service-Key →
    sein project_id (read-only, `/api/vault/secrets*` + `/api/vault/access`
    im selben Middleware-Gate wie Router/Firewall-Kanäle); Dashboard-Session →
    `?project=` or alle (System Administrator). NIE from dem Body (X-Header-Kontrakt)
  - Tests: `store/vault_test.go` (Projekt A sieht B not — gateway_test-DB),
    `security/vault_scope_test.go` (Service-Key-Pinning, no Eskalation
    about `?project=`, Fail-closed for kind=user-Keys)
  - Doku: API_DOCS /api/vault-Sektion + RBAC-Absatz erweitert

- **Finding:** project_user_budgets-Tabelle hat `role` (default 'developer') —
  aber: the User Management View hat 0 role-Referenzen (105 Z. = nur enable/
  disable); Keycloak-Rollen existieren (realm_access.roles via OPA), aber
  die Project-Rollen-Zuweisung (Wer ist Developer/Viewer/Admin in Project
  X?) hat KEINE UI and no dedizierte Route

  UI im Admin-/Workspace-Kontext; OPA-Policy kann role bereits konsumieren
  Rollen-Picker pro (User, Project) about the Budget Authorization Endpoint (the Authorization Store schreibt
  role+budget in EINER Zeile; neue Zuweisung erhält Budget-Default 5,00 USD,
  Rollenwechsel erhält bestehende Budget-Werte; DELETE entfernt Zuweisung
  inkl. Budget with Confirm-Hinweis); AdminBudgetsPage.tsx — ProjectRolesSection
  zeigt ALLE Zuweisungen (the Budget Query Endpoint without projectId) with inline
  editierbarer Rollen-Spalte, userId zu E-Mail aufgelöst; kanonisches
  Rollen-Set im UI admin|developer|viewer (Legacy-Rollen manager/sub_agent/
  owner bleiben sichtbar + migrierbar); i18n: 15 neue Keys in allen 60
  Locales (de übersetzt, Rest en-Fallback wie 053-Muster — check:i18n-Parität
  grün): teams.roles.viewer, admin.usersRoles*, admin.roles*,
  admin.budgetsRoles*; API_DOCS /api/budgets
  role-Feld dokumentiert. Kein Backend-Change nötig. OPA-Deny (403) zeigt
  ehrliche Inline-Meldung + Toast.

- **Finding:** App.tsx:527,557 — beide Routes aktiv; the Workspace Management View 2713 Z.(!)
  vs WorkspacesPage 693 Z.; Sidebar heißt weiter „Projects"
  (nav.projects, App.tsx:146)

  the Workspace Management View-Kernfunktionen (Deploy-Form) in WorkspacesPage integrieren,
  dann the Workspace Management View entschlacken (2713 Z. sind 3 Sprints Wachs)

- **Finding:** grep firewall/rules in Views = 0 Treffer; SecurityExposurePage
  hat nur das read-only Status-Tile; POST/DELETE /api/firewall/rules
  (OPA-gated, 050, ef7b29b) hat NULL Frontend-Verbraucher

- **Finding:** containers.workspace_id existiert (live, 037), aber no View
  zeigt Apps pro Workspace als own Ebene

- **Finding:** Preset-Picker zeigt „gVisor-NAT" without Kontext; System Administrator-Feedback
  wörtlich: „ich versteh das ganze frontend not"

- **Finding:** 2713 Z. — drei Sprints Parallel-Edits, uncommitted-WIP darin

  Onboarding an Endpoints-View abgeben, Apps an WorkspacesView

- **Finding:** Milestone:46/47 — alter Revert + neuer Checkoff überlappen
  (Claudes Edit hinterließ Zeilen-Reste; Milestone:46-48 doppelt)

---

## Korrektheit bestätigt (NICHT misaligned — zählt auch)

| Baustein | Fundstelle | Status |
|---|---|---|
| workspaces-Tabelle (10 Spalten, UNIQUE) | Real-DB live | ✅ |
| Router-Firewall (Inbound-DROP + Grants OPA-gated) | firewall.go ef7b29b | ✅ |
| Service-Keys (kind=service, Workspace-Bindung) | consumer_keys d36c62e | ✅ |
| OPA embedded (Rollen from Keycloak) | policy.go, live | ✅ |
| Egress (nftables im NS) | projects_ssh.go:1662 | ✅ |
| K-LAF-Attribution (X-Header, /api/sdk/logs) | auth.go, sdklogs | ✅ |

## Abgeleitete Fix-Reihenfolge

1. **053 laufend lassen** (trennt M2, M5-teilweise, M6, M7, M8)
2. **M1 nachziehen:** gVisor-Install → Endpoint-Verwaltung (054-Follow-up
   or Mini-Task; projects_ssh.go macht es ohnehin beim Node-Provision —
   nur die Checkbox-Täuschung im Frontform entfernen)
3. ~~**M3 Vault-Trennung:** neuer Mini-Task (Spalte + Filter + ACL-Klärung) —
    Entwurfs-Decision beim System Administrator~~ **✅ erledigt als Requirement (15.9.):
    Spalte + WHERE-Filter umgesetzt, Service-Key-Scope from authentifizierter
    Identität, Legacy-Secrets System Administrator-erreichbar (Details im M3-Eintrag)**
4. ~~**M4 Rollen-Zuweisungs-UI:** the User Management View erweitern (role-Picker) +
    Route the Budget Authorization Endpoint (the Authorization Store existiert!) verdrahten~~ **✅ erledigt
    als Requirement (15.9.): the User Management View-Rollen-Picker pro (User, Project)
    + AdminBudgetsPage-Rollen-Spalte inline editierbar (Details im
    M4-Eintrag)**
5. **M9/M10 Aufräumen** after 053-Merge

---

## R40-Appendix A — AIM-Comparison (opena2a/agent-identity-management, 14.9.)

**Finding:** Apache-2.0, Go/Python/Java/TS, 60★, aktiv (Stand 12.9.).
Cryptographic identity + capability authorization + audit trails for
non-human Identitäten.

**Verdict: Referenz + selektiver Import, NICHT Ersatz for unseren Stack.**

| AIM-Feature | Haben wir? | Bewertung for The Multi-Provider Gateway |
|---|---|---|
| Ed25519-signierte Agent-Identitäten | Nein (Bearer-Tokens) | Interessant for v2 — unser Service-Key-Modell ist einfacher and funktioniert; Ed25519 wäre Upgrade-Pfad |
| **Capability-Grants per Tool-Call** (`@perform_action(capability="db:read")`) | **NEIN — Epic-3-Work Package-Lücke!** | **Das Beste an AIM.** Genau unser fehlendes Tool-Call-Gating — R12 hat's geplant, nie gebaut. Muster übernehmen: Capability-String (namespace:action) als Rego-Policy-Input |
| 5-Step-FGA (Capability→Attribute→Context→Chain→Intent) | Nein (OPA 1-Step) | Overkill for v1; Intent-Check (NanoMind 3M lokal) ist aber ein schönes Muster for K-LAF Work Package-Variante |
| 9-Faktor-Trust-Scoring | Nein | R21/DAP-Skill-Score-Vorlage passt dazu — später |
| **JIT-Access with Human-Approval** (Pause bis Dashboard-Freigabe) | **NEIN — aber R21/DAP GUARDED-Approval-Queue ist genau das!** | Muster übernehmen for Architecture Pillar |
| SIEM-Adapter (Splunk/Sentinel) | Wir haben /api/sdk/logs | Unser Kanal ist allgemeiner (ein Schema) |
| MCP-Attestation (Multi-Agent-Consensus) | Nein | Later — supply-chain for Skills |
| NanoMind-Classifier (3M, lokal, Intent) | Wir haben Llama Guard via Mesh (73a21b9) | Verschiedene Ansätze — ihres ist leichter (Intent), unseres breiter (Content) |

**Konsequenz:** AIM NICHT als Framework einbinden (wir haben Identity-Stack
schon: Service-Keys + OPA + Keycloak + X-Header). ABER: das
Capability-String-Muster (`namespace:action` + risk levels) als Rego-Policy-
Input for Epic-3-Work Package (Tool-Call-Gating for Subagents/DB/MCP) übernehmen —
+ JIT-Approval-Muster als Implementierungs-Vorlage for die GUARDED-Queue
(R21 §6, Architecture Pillar). In Roadmap: Epic-3-Work Package-Zeile with AIM-Referenz ergänzen.

---
