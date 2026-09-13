---
okf_version: "1.0"
id: "okf-str-pos-r41-operator-feedback-blitz"
title: "R41 — Operator-Feedback-Blitz (14.9.2026): Vollständige Anforderungsliste"
topic: "strategy-audits-and-decisions"
subtopic: "positioning-and-plans"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - positioning-and-plans
summary: "**Quelle:** Operator-Session 14.9., ~3h. Alles was verwirrend, fehlend,"
---

# R41 — Operator-Feedback-Blitz (14.9.2026): Vollständige Anforderungsliste

**Quelle:** Operator-Session 14.9., ~3h. Alles was verwirrend, fehlend,
durcheinander or geplant-aber-nie-gebaut ist. Dies ist die ARBEITS-GRUNDLAGE
for die nächste Claude-Session + Agent-Welle.

---

## A) NAMING/IA-DURCHEINANDER (Operator: „alles durcheinandergekommen")

**Gewollte Hierarchie:** SSH Remote Target → Workspace → App
(vorher: Projects → Deployments; Workspace ersetzte Projects, Deployments→Apps)

| Problem | IST | SOLL | Fix |
|---|---|---|---|
| Workspace hat „Runtime-Preset" | ProjectsPage:52 `runtime?: string // dsh\|python\|go\|node\|docker\|base` | Runtime = App-Eigenschaft, not Workspace | Runtime-Presets in den APP-Layer verschieben (App-Create/Config), Workspace nur Netzwerk+SSH+User |
| Workspace-Deploy braucht „Projekt" | WorkspacesPage referenziert ProjectRow, Deploy prefills from Projekt | Workspace = eigenständiges Objekt; Projekt optional (or: Projekt = der Workspace-Kontext, NICHT eine separate Tabelle) | Entweder: /api/workspaces akzeptiert Workspace-Creation OHNE Projekt, or: Projekt-Feld wird zum Alias for Workspace |
| „VSC Port" angezeigt | vermutlich CodeServer-Port in Deploy-Response | = App-Port, not Workspace-Port | Port-Anzeige in Apps-Sektion, not im Workspace-Header |
| 2 Log-Pages | /logs (LogsPage) + /sdk-logs (SDKLogsPage) | EINE Logs-Seite with Tabs | Kombinieren: LLM-Proxy-Logs als Tab in die SDK-Logs-Seite (with type=chat Filter); alte LogsPage redirect |
| SDK-Logs überlappen/unvollständig | SDKLogsPage zeigt not alles | breiterer Canvas + Fix | Canvas-Width erhöhen + Pagination |
| Canvas zu schmal | max-w on Haupt-Content | breiter | CSS-Fix (max-w-* erhöhen) |

## B) SECURITY-VERSTÄNDNIS (Operator: „wieso hat der Router Ports?")

**Der 3-Ebenen-Kontext den der Operator vermisst:**
- gVisor = Sandbox (Kernel-Isolation) — KEINE Host-Firewall nötig
- Der Router ist UNSERE Firewall — Ports werden dynamisch per Grant freigeschaltet
- **Operator will NICHT das OpenMesh on dem Host an UFW/iptables rumfummelt** — aber
  der Deploy hat noch `UfwRule bool json:"ufwRule"` (projects_ssh.go:48,150)!
  Der Router-Grant (nftables im Container-NS) + gVisor + WAF = komplette Security-Chain.
  → UFW-Whitelist-Code entfernen or als opt-in belassen (deprecated).

## C) FEATURES DIE FEHLEN (Operator-Liste, priorisiert)

### C1 — Secrets-System (GROSSE LÜCKE)
- `openmesh.secrets.get(<kv>, <secret>, <optional: engine/target>, <optional: api-key>)` —
  auto-routing default, override möglich
- Workspace-Create fragt: „KV Storage anlegen? Welche Secrets-Engine?"
- Secrets-Engine-Auswahl pro Remote-Target-Deploy (Vault, AWS-Secrets-Manager, CP-eigen)
- Vault-Dashboard: konfigurierte Engines (remote/worker-nodes), Secrets export/
  import/copy-between-engines, „Import from Engine" Button
- Router entscheidet wo die nächste Control-Plane for Secrets ist

### C2 — Multi-User-Same-Server (gVisor + Port-Kollision)
- 2. User on gleichem Server, gleiches Projekt → geklonter Workspace with RANDOM
  Port-Forwarding am Router (no VM nötig)
- Bei Workspace-Create: „Welcher User?" → automatisch geklonter Workspace + random Ports
- Ports-Section in Workspace UND App-Ansicht

### C3 — RBAC beim Erstellen (not nachträglich)
- Bei Project/Workspace/Remote-Target-Create: RBAC direkt einstellbar (wer hat SSH-Berechtigung,
  wer liest Workspaces/Apps, welcher User bekommt geklonten Workspace)
- Heute: RBAC nur im Admin-Tab, not im Create-Flow

### C4 — Security-Frontend-Integration (GROSSE LÜCKE)
- Security-Tab Overview-Panel: ALLE Criticals/Warnings von ALLEN Remote-Targets
  (Wazuh, Falco, WAF, Firewall — die Daten fließen in /api/sdk/logs aber das
  Security-Tab zeigt sie NICHT)
- Falco/Wazuh-Dashboards einbetten (iframe or iframe-Tile)
- SAST & DAST Tabs im Security-Bereich (Checkov läuft, UI fehlt)
- Network-Observing-Tab: Anomaly-Detection, fraudulent traffic, Router-Übersicht
- Notifications: Critical-Funde → Notification-System (not nur in Logs)
- Testing-Section: Prompt-Injection-Demo (System friert ein → Agent bekommt
  Response → Llama-Guard-Verdict → SIEM/Firewall-Demo + Attack-Simulationen)

### C5 — Agent-Feedback-Loop (NEU, GROSSE IDEE)
- Wenn Coding-Agent Code-Änderungen macht → Wazuh/SIEM findet Critical → dem
  Coding-Agenten INJEKTEN dass er Scheiße gebaut hat (statt dass er in Logs sucht)
- Utility/Session auswählen pro Workspace → kriegt automatisch injiziert
- Agent kann andere Sessions callen wenn er rausfindet wer es verursacht hat
- = Guardrails-Fehler als aktives Feedback, not passives Log

### C6 — OAuth-Provider (Google + GitHub)
- Keycloak läuft, aber Google/GitHub als Identity-Provider fehlen (Federation)

### C7 — Scanopy in den Router
- Scanopy = OVS/VLAN-Automation (Operator hat ovs-bridge-collection + opnsense-helper)
- INS Router-Code schreiben (not als separates Tool)

### C8 — MCP + Skills + Knowledge-Base
- Agent soll on die KOMPLETTE API zugreifen (Coding-Agents nutzen OpenMesh-Infra direkt)
- Skills im OKF/Skill-Format
- Knowledge-Base for Agents

### C9 — Frontend-IA-2 (Mini-Sidebar + Overview-Tabs)
- Mini-Sidebar pro Haupt-Route (statt Dropdowns oben)
- Jede Haupt-Route bekommt Overview/Landing-Page with wichtigsten Infos
- Dropdowns im Tab können bleiben

### C10 — Ghost-Daten aufräumen
- Alte Users/Keys/Projects from Tests die man not löschen kann → DELETE-Routes
  prüfen (ConsumerKeys-Delete existiert aber wo ist der Button?), Test-Daten
  from der Live-DB entfernen

---

## D) WAS DER OPERATOR ZU WAZUH/FALCO-SAGT (Daten die er fand)

Falco-Event (funktioniert, fließt in /api/sdk/logs):
```json
{"scanner":"falco","rule":"OpenMesh Workspace Agent: known miner binary executed",
 "priority":"Critical","proc.cmdline":"xmrig",...}
```

Wazuh-Alert (funktioniert, fließt in /api/sdk/logs):
```json
{"scanner":"wazuh","rule_id":"19008","rule_level":3,
 "full_log":"CIS Benchmark... Ensure default group for the root account..."}
```

**Beide Systeme LIEFERN Daten, aber das Frontend zeigt sie NICHT im Security-Tab.**

## E) WAS NOCH OFFEN IST AUS RESEARCH (Operator: „da steht noch einiges from")

- Open-Source-Projekte from R20 (saits-cloud-Review) die noch not übernommen wurden
- DAP/Skills-Hub (Sprint 23, R21) — Epic-18 noch 0/7
- Dashboard-IA Epic 17 — WP1-WP3, WP5, WP6 offen
- Sprint-24 (Doc-Konsolidierung) nie begonnen
- Sprint-33 (AWS Multi-Provider, O1-O5) nie begonnen
- History-Rewrite (TASK-047) before Public-Flip

## F) CHECKOV-AGENT

Der letzte Agent (Checkov/Quarantine) läuft noch, macht Tests. Warten bis er
fertig ist, dann Review+Merge.

---

## PRIORITÄTEN (Operator-Entscheidung nötig)

| # | Was | Warum | Aufwand |
|---|---|---|---|
| 1 | A) Naming/IA-Durcheinander fixen | Operator versteht sein eigenes Produkt not mehr | M |
| 2 | C4) Security-Frontend (Overview+Dashboards+Notifications) | SIEM/WAF/Falco liefern Daten aber User sieht sie not | L |
| 3 | C2) Multi-User-Same-Server (gVisor+random Ports) | Kern-Feature for Teams | L |
| 4 | C1) Secrets-System (Engine-Auswahl+API+Dashboard) | Kern-Feature for Utility-Layer | L |
| 5 | C5) Agent-Feedback-Loop | Unique-Selling-Point | M |
| 6 | C6) OAuth Google/GitHub | Onboarding-Reibung | S |
| 7 | C9) Mini-Sidebar+Overview-Tabs | UX-Überholung | M |
| 8 | C3) RBAC beim Create | Feature-Complete | S |
| 9 | B) UFW-Code entfernen | Cleanup | S |
| 10 | C10) Ghost-Daten aufräumen | Hygiene | S |

---

## Appendix

- **Lizenz:** AGPL-3.0 — gleiche Kategorie wie Coder, den das Repo bereits explizit
  NICHT geklont hat (R35-Regel: AGPL = reference-only, clean-room nachimplementieren)
- **Status:** Gitpod Classic sunset Oktober 2025, Pivot zu „Ona" (agent-orchestration,
  näher an OpenMesh's eigenem Fokus als das alte Dev-Workspace-Produkt)
- **Wertvoll trotzdem:** das alte **ws-proxy**-Komponente machte EXAKT das
  Identity-based Workspace-Routing, das TASK-079 jetzt baut — Reference-only
  Architecture-Studie lohnt (Ideen verfallen not), Code-Nutzung nie.
