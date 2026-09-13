---
id: "R41"
title: "R41 — Operator-Feedback-Blitz (14.9.2026): Vollständige Anforderungsliste"
type: research
date: 2026-09-13
status: final
tags: [wazuh, ufw, mesh, ssh, rbac]
license: CC-BY-4.0
---

# R41 — Operator-Feedback-Blitz (14.9.2026): Vollständige Anforderungsliste

**Quelle:** Operator-Session 14.9., ~3h. Alles was verwirrend, fehlend,
durcheinander oder geplant-aber-nie-gebaut ist. Dies ist die ARBEITS-GRUNDLAGE
für die nächste Claude-Session + Agent-Welle.

---

## A) NAMING/IA-DURCHEINANDER (Operator: „alles durcheinandergekommen")

**Gewollte Hierarchie:** SSH Remote Target → Workspace → App
(vorher: Projects → Deployments; Workspace ersetzte Projects, Deployments→Apps)

| Problem | IST | SOLL | Fix |
|---|---|---|---|
| Workspace hat „Runtime-Preset" | ProjectsPage:52 `runtime?: string // dsh\|python\|go\|node\|docker\|base` | Runtime = App-Eigenschaft, nicht Workspace | Runtime-Presets in den APP-Layer verschieben (App-Create/Config), Workspace nur Netzwerk+SSH+User |
| Workspace-Deploy braucht „Projekt" | WorkspacesPage referenziert ProjectRow, Deploy prefills aus Projekt | Workspace = eigenständiges Objekt; Projekt optional (oder: Projekt = der Workspace-Kontext, NICHT eine separate Tabelle) | Entweder: /api/workspaces akzeptiert Workspace-Creation OHNE Projekt, oder: Projekt-Feld wird zum Alias für Workspace |
| „VSC Port" angezeigt | vermutlich CodeServer-Port in Deploy-Response | = App-Port, nicht Workspace-Port | Port-Anzeige in Apps-Sektion, nicht im Workspace-Header |
| 2 Log-Pages | /logs (LogsPage) + /sdk-logs (SDKLogsPage) | EINE Logs-Seite mit Tabs | Kombinieren: LLM-Proxy-Logs als Tab in die SDK-Logs-Seite (mit type=chat Filter); alte LogsPage redirect |
| SDK-Logs überlappen/unvollständig | SDKLogsPage zeigt nicht alles | breiterer Canvas + Fix | Canvas-Width erhöhen + Pagination |
| Canvas zu schmal | max-w auf Haupt-Content | breiter | CSS-Fix (max-w-* erhöhen) |

## B) SECURITY-VERSTÄNDNIS (Operator: „wieso hat der Router Ports?")

**Der 3-Ebenen-Kontext den der Operator vermisst:**
- gVisor = Sandbox (Kernel-Isolation) — KEINE Host-Firewall nötig
- Der Router ist UNSERE Firewall — Ports werden dynamisch per Grant freigeschaltet
- **Operator will NICHT das JiMesh auf dem Host an UFW/iptables rumfummelt** — aber
  der Deploy hat noch `UfwRule bool json:"ufwRule"` (projects_ssh.go:48,150)!
  Der Router-Grant (nftables im Container-NS) + gVisor + WAF = komplette Security-Chain.
  → UFW-Whitelist-Code entfernen oder als opt-in belassen (deprecated).

## C) FEATURES DIE FEHLEN (Operator-Liste, priorisiert)

### C1 — Secrets-System (GROSSE LÜCKE)
- `jimesh.secrets.get(<kv>, <secret>, <optional: engine/target>, <optional: api-key>)` —
  auto-routing default, override möglich
- Workspace-Create fragt: „KV Storage anlegen? Welche Secrets-Engine?"
- Secrets-Engine-Auswahl pro Remote-Target-Deploy (Vault, AWS-Secrets-Manager, CP-eigen)
- Vault-Dashboard: konfigurierte Engines (remote/worker-nodes), Secrets export/
  import/copy-between-engines, „Import from Engine" Button
- Router entscheidet wo die nächste Control-Plane für Secrets ist

### C2 — Multi-User-Same-Server (gVisor + Port-Kollision)
- 2. User auf gleichem Server, gleiches Projekt → geklonter Workspace mit RANDOM
  Port-Forwarding am Router (keine VM nötig)
- Bei Workspace-Create: „Welcher User?" → automatisch geklonter Workspace + random Ports
- Ports-Section in Workspace UND App-Ansicht

### C3 — RBAC beim Erstellen (nicht nachträglich)
- Bei Project/Workspace/Remote-Target-Create: RBAC direkt einstellbar (wer hat SSH-Berechtigung,
  wer liest Workspaces/Apps, welcher User bekommt geklonten Workspace)
- Heute: RBAC nur im Admin-Tab, nicht im Create-Flow

### C4 — Security-Frontend-Integration (GROSSE LÜCKE)
- Security-Tab Overview-Panel: ALLE Criticals/Warnings von ALLEN Remote-Targets
  (Wazuh, Falco, WAF, Firewall — die Daten fließen in /api/sdk/logs aber das
  Security-Tab zeigt sie NICHT)
- Falco/Wazuh-Dashboards einbetten (iframe oder iframe-Tile)
- SAST & DAST Tabs im Security-Bereich (Checkov läuft, UI fehlt)
- Network-Observing-Tab: Anomaly-Detection, fraudulent traffic, Router-Übersicht
- Notifications: Critical-Funde → Notification-System (nicht nur in Logs)
- Testing-Section: Prompt-Injection-Demo (System friert ein → Agent bekommt
  Response → Llama-Guard-Verdict → SIEM/Firewall-Demo + Attack-Simulationen)

### C5 — Agent-Feedback-Loop (NEU, GROSSE IDEE)
- Wenn Coding-Agent Code-Änderungen macht → Wazuh/SIEM findet Critical → dem
  Coding-Agenten INJEKTEN dass er Scheiße gebaut hat (statt dass er in Logs sucht)
- Utility/Session auswählen pro Workspace → kriegt automatisch injiziert
- Agent kann andere Sessions callen wenn er rausfindet wer es verursacht hat
- = Guardrails-Fehler als aktives Feedback, nicht passives Log

### C6 — OAuth-Provider (Google + GitHub)
- Keycloak läuft, aber Google/GitHub als Identity-Provider fehlen (Federation)

### C7 — Scanopy in den Router
- Scanopy = OVS/VLAN-Automation (Operator hat ovs-bridge-collection + opnsense-helper)
- INS Router-Code schreiben (nicht als separates Tool)

### C8 — MCP + Skills + Knowledge-Base
- Agent soll auf die KOMPLETTE API zugreifen (Coding-Agents nutzen JiMesh-Infra direkt)
- Skills im OKF/Skill-Format
- Knowledge-Base für Agents

### C9 — Frontend-IA-2 (Mini-Sidebar + Overview-Tabs)
- Mini-Sidebar pro Haupt-Route (statt Dropdowns oben)
- Jede Haupt-Route bekommt Overview/Landing-Page mit wichtigsten Infos
- Dropdowns im Tab können bleiben

### C10 — Ghost-Daten aufräumen
- Alte Users/Keys/Projects aus Tests die man nicht löschen kann → DELETE-Routes
  prüfen (ConsumerKeys-Delete existiert aber wo ist der Button?), Test-Daten
  aus der Live-DB entfernen

---

## D) WAS DER OPERATOR ZU WAZUH/FALCO-SAGT (Daten die er fand)

Falco-Event (funktioniert, fließt in /api/sdk/logs):
```json
{"scanner":"falco","rule":"JiMesh Workspace Agent: known miner binary executed",
 "priority":"Critical","proc.cmdline":"xmrig",...}
```

Wazuh-Alert (funktioniert, fließt in /api/sdk/logs):
```json
{"scanner":"wazuh","rule_id":"19008","rule_level":3,
 "full_log":"CIS Benchmark... Ensure default group for the root account..."}
```

**Beide Systeme LIEFERN Daten, aber das Frontend zeigt sie NICHT im Security-Tab.**

## E) WAS NOCH OFFEN IST AUS RESEARCH (Operator: „da steht noch einiges aus")

- Open-Source-Projekte aus R20 (saits-cloud-Review) die noch nicht übernommen wurden
- DAP/Skills-Hub (Sprint 23, R21) — Epic-18 noch 0/7
- Dashboard-IA Epic 17 — WP1-WP3, WP5, WP6 offen
- Sprint-24 (Doc-Konsolidierung) nie begonnen
- Sprint-33 (AWS Multi-Provider, O1-O5) nie begonnen
- History-Rewrite (TASK-047) vor Public-Flip

## F) CHECKOV-AGENT

Der letzte Agent (Checkov/Quarantine) läuft noch, macht Tests. Warten bis er
fertig ist, dann Review+Merge.

---

## PRIORITÄTEN (Operator-Entscheidung nötig)

| # | Was | Warum | Aufwand |
|---|---|---|---|
| 1 | A) Naming/IA-Durcheinander fixen | Operator versteht sein eigenes Produkt nicht mehr | M |
| 2 | C4) Security-Frontend (Overview+Dashboards+Notifications) | SIEM/WAF/Falco liefern Daten aber User sieht sie nicht | L |
| 3 | C2) Multi-User-Same-Server (gVisor+random Ports) | Kern-Feature für Teams | L |
| 4 | C1) Secrets-System (Engine-Auswahl+API+Dashboard) | Kern-Feature für Utility-Layer | L |
| 5 | C5) Agent-Feedback-Loop | Unique-Selling-Point | M |
| 6 | C6) OAuth Google/GitHub | Onboarding-Reibung | S |
| 7 | C9) Mini-Sidebar+Overview-Tabs | UX-Überholung | M |
| 8 | C3) RBAC beim Create | Feature-Complete | S |
| 9 | B) UFW-Code entfernen | Cleanup | S |
| 10 | C10) Ghost-Daten aufräumen | Hygiene | S |

---

## Anhang C — Gitpod-Salvage-Bewertung (Claude, 14.9.)

- **Lizenz:** AGPL-3.0 — gleiche Kategorie wie Coder, den das Repo bereits explizit
  NICHT geklont hat (R35-Regel: AGPL = reference-only, clean-room nachimplementieren)
- **Status:** Gitpod Classic sunset Oktober 2025, Pivot zu „Ona" (agent-orchestration,
  näher an JiMesh's eigenem Fokus als das alte Dev-Workspace-Produkt)
- **Wertvoll trotzdem:** das alte **ws-proxy**-Komponente machte EXAKT das
  Identity-based Workspace-Routing, das TASK-079 jetzt baut — Reference-only
  Architektur-Studie lohnt (Ideen verfallen nicht), Code-Nutzung nie.
