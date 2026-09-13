---
id: "audit-2026-09-15-session"
title: "Session-Audit: Measured Findings (R44 + R39 + R40)"
type: audit
date: 2026-09-15
status: final
tags: [audit, slop, misalignment, ssot, frontend, backend]
license: CC-BY-4.0
---

# Session-Audit: Measured Findings (R44 + R39 + R40)

## Backend Audit Results

| Area | Status | Details |
|---|---|---|
| Gateway Handlers | ✅ | All routes have explicit 400/401/403/404/500 JSON errors |
| VLAN-Runner | ✅ | Command-Injection safe (vlanIfaceRe validates), separate Shell-Statements (set -e fix) |
| Policy Engine | ✅ | Katalog↔Gate-Konsistenz verriegelt (6 Policy-Tests), fail-closed |
| Subagent Sessions | ✅ | Token-Verifizierung (RS256+JWKS), fail-closed, Ownership-Gate (403 bewiesen) |
| Store Migrations | ✅ | Fresh-DB-Fix (CREATEs tragen Spalten seit TASK-076) |
| Router-Node | ✅ | HTTP-Demux (Peek-Stall gefixt 30s→0.003s), JSONL Journal+Cursor, WAN-Spill-Resume |
| WAF Coraza | ✅ | CRS einkompiliert, SQLi/XSS live geblockt (403), Kontrollgruppe bewiesen |
| SIEM Bridge | ✅ | Wazuh+Falco→/api/sdk/logs, K-LAF E3 Redaction (1 Identitäts-Feld max) |
| SIEM Compose | ⚠️ | Wazuh-Demo-Creds (SecretPassword/kibanaserver) — .env-Variablen ersetzen vor Public-Flip |
| IaC-Scan | ✅ | Checkov+gosec/trivy, Quarantäne live (docker stop), HITL-Gate (confirm:true) |

## Frontend Audit Results

| Area | Status | Details |
|---|---|---|
| Mock-Daten | ✅ | R41 entfernt (DiscoveryStatus 460Z, getting-started, peak-hours, custom-weights) |
| Fake-Logs | ✅ | R42 entfernt (ProjectsPage: "Authenticated successfully", "100% success") |
| localStorage-Rest | ⚠️ | AnalyticsPage, OnboardingPage, ProjectsPage (3 Refs), SecurityGuardDemoPage — klassifizieren |
| Dead-Ends | ⚠️ | /api/subagents Frontend-Consumer fehlt (SubagentsPanel gebaut in 084) |
| Query-Keys | ✅ | query-keys.ts Registry (TASK-086) |
| Slop-Gate | ✅ | check-frontend-slop.mjs CI-Gate (TASK-086) |
| i18n | ✅ | 60 Locales / 2138 Keys, Parität grün |
| Tests | ✅ | 279/279 (100% grün — ENV-Bug behoben) |
| tsc | ✅ | 202 (unter 205-Baseline) |

## Known SSOT-Chain

```
workspace_routes.go (Store-Read)
  → router_config.go (Gateway-Serve, Composite-Version al=…;ck=…;ws=…)
  → routes.go (Router-Consume, RouteTable + Ownership-Gate)
```

## API_DOCS Routes Verified Present

- GET /api/capabilities ✅
- GET/POST/DELETE /api/control-planes ✅ (+ provision/status/deploy/undeploy)
- POST /api/router/aliases ✅
- GET /api/networks/users|nodes|preauthkeys|policy ✅
- POST /api/networks/preauthkeys/expire ✅
- GET/POST/DELETE /api/projects/{id}/vlan ✅
- GET/POST/DELETE /api/secrets-engines/* ✅
- GET/POST/DELETE /api/firewall/rules ✅
- POST /api/auth/firebase ✅ (geplant, TASK-088)

## Operator-Blockers

| Blocker | Priority |
|---|---|
| SSH-Creds rotieren (R39-Referenz in History) | CRITISCH |
| Firebase-Admin-SDK Key | P0 (TASK-088 Backend-Verifizierung) |
| E-SIEM-1..5 bestätigen | P1 |
| OAuth E2E (echte Google/GitHub-Creds) | P1 |
| Keycloak-Admin-PW | P1 |
| 070 §6 Toggles (welche Domänen) | P1 |
| 076-Design (Multi-Agent-Investigation) | P2 |
| O1-O5 (Sprint-33 AWS) | P2 |
| de.json Gemini-Output (1184 Keys) | P2 |
| jimesch-public Repo anlegen | P2 |
