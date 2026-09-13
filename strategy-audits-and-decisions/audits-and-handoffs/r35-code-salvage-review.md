---
okf_version: "1.0"
id: "okf-str-aud-r35-code-salvage-review"
title: "R35 — Code-Salvage-Review: Coder, Headplane, Headscale-Admin, Nebula, DevPod"
topic: "strategy-audits-and-decisions"
subtopic: "audits-and-handoffs"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - audits-and-handoffs
summary: "**Quelle:** Operator-Auftrag 13.9.2026 („bitte die Sachen auch forken bzw. clonen"
---

# R35 — Code-Salvage-Review: Coder, Headplane, Headscale-Admin, Nebula, DevPod

**Quelle:** Operator-Auftrag 13.9.2026 („bitte die Sachen auch forken bzw. clonen
and den Code ansehen and was man salvagen kann"). Echte Repos geclont after
`~/projects/research-forks/` (headplane, headscale-admin, headscale, nebula);
Coder + DevPod **without Clone** via GitHub-API/Dokumente geprüft (Coder-Repo ist
~400 MB; headscale läuft at uns ohnehin als Container — Clone laut Operator
not nötig). Kein Code from diesem Review ist übernommen — es ist eine
Fundstellen-Liste for Sprint 35.

---

## 1. Lizenz-Tabelle (die harte Wahrheit zuerst)

| Repo | Lizenz (verifiziert from LICENSE-Datei / GitHub) | Code übernehmbar? |
|---|---|---|
| `tale/headplane` | **MIT** (LICENSE, „Copyright (c) 2024 Aarnav Tale") | ✅ ja, with Attribution |
| `GoodiesHQ/headscale-admin` | **GPL-3.0** (LICENSE, GNU GENERAL PUBLIC LICENSE) | ❌ **NEIN** — GPL-3 ist viral, kollidiert with PolyForm-NC-Kommerzialisierung. Nur als Referenz ansehen. |
| `juanfont/headscale` | **BSD-3-Clause** (LICENSE) | ✅ (nutzen wir als Service, nichts zu vendor-reifen) |
| `slackhq/nebula` | **MIT** (LICENSE) | ✅ (aber als Transport verworfen — s. R34) |
| `coder/coder` | **AGPL-3.0** (raw.githubusercontent.com/coder/coder/main/LICENSE: „GNU AFFERO GENERAL PUBLIC LICENSE") | ❌ **no Code** — nur Muster/Architecture-Referenz. AGPL-Netzwerk-Klausel macht Copy-in-Produkt unbrauchbar. |
| `loft-sh/devpod` | MPL-2.0 (laut Repo) | ⚠️ nur dateiweise with Header-Erhalt; for uns nur Muster |
| `sorenisanerd/gotty` | MIT | ✅ (obsolet — Sprint 35 WP2 ersetzt ihn through Eigenbau) |

---

## 2. Coder im Detail (AGPL — Muster, no Code)

### 2.1 Was Coder hat, was wir auch haben (Überlappung)

| Baustein | Coder | OpenMesh |
|---|---|---|
| Web-Workspaces | Templates + Workspace-Builds (Terraform) | `/api/projects/*` + `internal/deploy` (SSH-Deploy, Docker, gVisor) |
| Browser-IDE | code-server/Elektron-Fork eingebettet | Sprint 35 WP2: eigenes xterm.js + Go-WebSocket (~0 MB Server-RAM) |
| Agent im Workspace | `agent/` (Reconnectable-PTY, Port-Fwd, Lifecycle) | DSH/Agent-Container + Session-Token (TASK-011) |
| Admin-UI | React-Dashboard | React-Dashboard (Sprint 22 IA) |

### 2.2 Was Ji (Operator) additional will and Coder VORMACHT (Referenz-wert)

1. **Terraform-Provisioning-Lifecycle** — `provisioner/terraform/`
   (executor.go, planresources.go, parse.go, resources.go): Template →
   Plan → Apply → Resources. **Für OpenMesh:** wenn ein Kunde später
   „deklariertes IaC-Deployment" will, ist das der Lifecycle: unser
   `deploy.go` deckt den Docker/SSH-Pfad ab, ein `provisioner`-Interface
   after diesem Muster könnte Terraform als zweiten Treiber aufnehmen —
   **Pattern-Referenz, no Copy** (AGPL).
2. **Agent-Regel-Syntax** — `docs/ai-coder/agent-firewall/rules-engine.md`:
   `key=value`-Regeln (`method=`, `domain=`, `path=`), Wildcards,
   Default-Deny, OR-Logik. Verdächtig einfach and gut — **übernehmen wir
   als Syntax for die K-LAF-/Egress-Regeln** (unsere egress.go hat heute
   inline Go-Regeln; eine deklarative YAML with dieser Syntax wäre
   operator-freundlicher). Syntax-Idee ≠ Code — übernehmbar.
3. **Agent-Firewall „landjail"** — `docs/ai-coder/agent-firewall/landjail.md`:
   Landlock V4 — **alle bind + alle connect verbieten außer zum
   HTTP-Proxy-Port**. Kein Namespace, no Docker-Rechte nötig.
   **Für OpenMesh relevant:** das DSH-Incident-Log (Sprint 19) zeigte
   „landlock-run: partial enforcement (older Landlock ABI)" — Coder löst
   genau das with V4. Referenz for K-LAF WP2 (Prozess-Confinement der
   Agent-Container without gVisor-Overhead for leichte Fälle).
4. **Agent-Protokoll (Reconnectable PTY)** — `agent/agent.go` +
   `agentcontainers/` (Devcontainer-Support). Muster-Referenz for
   Sprint 35 WP2: unser Terminal braucht Reconnect + Resize (SIGWINCH) +
   Session-Überleben at Netzwerk-Abbruch — genau das löst deren
   Agent-PTY-Stream.

### 2.3 Die Agent-Firewall von Coder vs. unser K-LAF (Jis Punkt)

Coder nennt es „Agent Firewall" (früher „Agent Boundaries"), Teil von
**AI Governance = Premium-Lizenz** (Dokument-Header: „included with a
Premium license"; API-Live-Teil liegt in `enterprise/coderd/agentfirewall.go`).
Funktionsumfang laut `docs/ai-coder/agent-firewall/index.md`:

- Prozess-Level-HTTP/HTTPS-Proxy with Domain/Method/Path-Allowlist
- Audit-Logs an die Control-Plane
- 2 Jail-Types: nsjail (Namespace) and landjail (Landlock V4)
- OSS-Anteil: nur die `boundary`-CLI (github.com/coder/boundary)

**Unser Stack dagegen (alles dokumentiert, teils live):**

| Fähigkeit | Coder Agent Firewall | OpenMesh K-LAF/Security |
|---|---|---|
| HTTP-Egress-Allowlist | ✅ (Premium) | ✅ live (`internal/network/egress.go`, TASK-012/019) |
| Docker-Socket-Guard | ❌ | ✅ live (TASK-015/019) |
| Container-Freeze | ❌ | ✅ E5 entschieden (alle Container) |
| Prompt-Injection-Detection | ❌ | ✅ E1 entschieden (purego/ONNX FFI) |
| IaC/Secret-Scanner | ❌ | ✅ geplant (Checkov, Sprint 28/29) |
| SIEM (Wazuh+Falco+Bridge) | ❌ | ✅ geplant (Sprint 32) |
| Forensik/Audit-Retention | Session-Stream | ✅ E3 (redigiert, 30 Tage) |

**Conclusion (bestätigt Jis Einschätzung):** Coder abstrahiert einen Prozess
hinter einem HTTP-Proxy with Allowlist; wir haben die volle Kette von
Egress about Socket-Guard, Freeze, Injection-Detection bis SIEM. Ihr
Vorsprung ist ausschließlich: die Kernel-Isolation ist **landjail**
(Landlock V4) statt gVisor — das ist ein guter Lightweight-Baustein for
Fälle, wo no kompletter gVisor-Sandbox nötig ist. → K-LAF-WP-2-Verweis
aufnehmen, not kopieren.

### 2.4 Coder vs. OpenMesh — wo WIR breiter sind

Coder hat **no** Pendant zu: LLM-Proxy-Kern (Routing/Budgets/Keypool,
Multi-Provider), Headscale-Mesh (Netzwerk-Plane), DB/CDC-Utility-Layer
(Sprint 26), Keycloak+OPA (AuthN/AuthZ), Agent-Observability (Sprint 30),
SIEM (Sprint 32). Ihre Stärke ist der Terraform-Template-Marktplatz and
die Workspace-UX-Reife — dort sind wir noch not. Ehrlich gesagt: for
„Workspaces als Produkt" ist Coder ausgereifter; for „LLM-Gateway +
Multi-Target-Provisioning + Security" sind wir weiter. Beides ist OK —
unterschiedliche Produkte.

---

## 3. Headplane (MIT — der beste Dashboard-Salvage-Kandidat)

**Clone:** `~/projects/research-forks/headplane/` (23 MB, v0.29-kompatibel? →
nein: prüfen! Headplane-Ziel ist eine spezifische Headscale-Version —
unser Container ist v0.29.3; README der gepullten Version prüfen before
Integration).

**Struktur:** React-Router-v7-App (`app/routes/`: acls, auth, dns, home,
machines, settings, ssh, users) + Go-Sidecars (`cmd/hp_agent`,
`cmd/hp_ssh`, `fake_sh`, `hp_healthcheck`) + `internal/tsnet`
(Tailscale-intern-TSNet!) + drizzle/SQLite for Sessions.

**Salvage-Potenzial for Sprint 35 WP3/WP4:**
1. **Musterspende React-Views:** `app/routes/machines/`, `users/`, `acls/`
   zeigen, wie man die Headscale-v1-API (Users/Nodes/ACLs/PreAuthKeys)
   sauber im UI präsentiert. Unsere `NetworksPage.tsx` ist bewusst
   minimal; wenn wir Nodes-Tags, ACL-Editor and Key-Management brauchen,
   sind das dieReferenz-Views. MIT = Adapter/Copy with Attribution legal.
2. **`internal/tsnet`**: Headplane spricht with Tailscale about TSNet
   (eingebetteter Node) — interessant for später: OpenMesh-Backend könnte
   selbst Mesh-Node werden (statt nur API-Client). Referenz, no Copy
   for v1.
3. **`cmd/hp_ssh`**: SSH-basierte Node-Verwaltung about Headscale —
   Muster for „SSH-Endpoint-Verwaltung im Networks-Tab".

## 4. Headscale-Admin (GPL-3 — NICHT salvage-fähig)

**Clone:** 28 MB, SvelteKit (not React). Nur als Referenz: zeigt die
API-Oberfläche (nodes/users/acls/deploy/routes/settings) in einer
zweiten UI-Implementation. **Keine Code-Übernahme** — GPL-3 + kommerzielle
Pläne verträgt sich not. Vermerkt, damit niemand später „schnell was
daraus adaptiert".

## 5. Headscale selbst (BSD-3 — Service, no Salvage nötig)

Läuft at uns als Container v0.29.3 (Sprint-35-Commit 07385d9, health
pass). Der 380-MB-Clone (versehentlich mitgelaufen) kann wieder weg —
wir brauchen ihn not; API-Referenz genügt: `hscontrol/api/`
(v1: Users/Nodes/PreAuthKeys/Policy; v2: ACLs/Devices/OAuth).
Policy-Format-Umbau v0.23→v0.29 (`acl_policy_path` → `policy.mode/path`)
haben wir beim Boot bereits live erlebt and gefixt.

## 6. Nebula (MIT — verworfen als Transport, Referenz for Tag-ACLs)

Als Transport verworfen (R34: no Control-Server, manuelle
Cert-Verteilung per SSH — eigener Eiffelturm). **Aber:** das Muster
„Firewall-Gruppen als Cert-Claims statt IPs" ist genau das, was wir with
Headscale-Tags (`tag:proj-<id>`) + ACL-Policy bauen (Sprint 35 WP3).
Nebula macht es im Zertifikat, Headscale in der Policy — wir übernehmen
das **Prinzip** (gruppenbasierte statt IP-basierte Regeln), not den Code.

## 7. DevPod (MPL-2.0 — not geclont, ein Musterwert)

Ein einziger Takeaway: **devcontainer.json als Workspace-Manifest.** Wenn
OpenMesh-Workspaces später ein Standard-Format bekommen, ist das der
etablierte (IDE-unabhängig, von VS Code/Codespaces/GitHub geprägt).
Sprint 35 WP2 könnte beim Projekt-Anlegen ein `devcontainer.json`
akzeptieren statt/zusätzlich zu unserem eigenen Deploy-Formular.
Decision später; nur dokumentiert.

## 8. GoTTY (MIT — obsolet through Eigenbau)

Nicht geclont (Clone-Job wurde gestoppt). Sprint 35 WP2 ersetzt ihn
sowieso: eigenes `internal/terminal` (Go-WebSocket-PTY-Bridge) +
xterm.js im Frontend — 0 MB Server-RAM statt Node-Prozess pro Shell,
SSH-Exec ins den Container, no Ports. Kein Salvage-Wert about das
hinaus, was WP2 ohnehin plant.

---

## 9. Resultierende To-dos (Sprint-35-Backlog-Eintrag, nichts implementiert)

- [ ] K-LAF-WP2-Verweis: landjail (Landlock V4) als Lightweight-Confinement
      neben gVisor dokumentieren (`docs/sprints/SPRINT-20…`-K-LAF-Teil) —
      Fundstelle: coder `docs/ai-coder/agent-firewall/landjail.md`.
- [ ] Egress-Regel-Syntax: Coder-Rules-Syntax (`method=/domain=/path=`,
      Default-Deny, OR) als YAML-Format for unsere egress-Regeln bewerten
      (heute inline Go in `internal/network/egress.go`).
- [ ] Networks-Tab (WP3/WP4): headplane `app/routes/machines|users|acls`
      als Musterspende prüfen (MIT) — Übernahme in unsere React-Views.
- [ ] devcontainer.json als Workspace-Manifest-Option bewerten (DevPod-Muster).
- [ ] Headscale-Clone (380 MB) from `~/projects/research-forks/` löschen
      (läuft als Container, Clone unnötig).

**Ehrlichkeits-Notiz:** Coder wurde absichtlich NICHT geclont (~400 MB,
AGPL — ein Clone verführt nur zum Copy-Paste-Fehler). Alle Coder-Fundstellen
kommen from GitHub-API + raw-Docs, verifiziert per curl (LICENSE, index.md,
rules-engine.md, landjail.md, codersdk/agentfirewall.go).

---

## 10. Positionierung + Coder-Neuausrichtung (Operator-Entscheidung, 13.9.2026)

**Operator-Statement:** „Wir sind not Coder. Wir sind eine sichere
Environment for Vibe-Coding and Agents — with Security-Aspekt. Das with
den Terraform-Presets ist cool, aber Security and Networking ist unser
Vorteil."

### 10.1 Was das Coder-README (2026) verrät — Competitive-Intel

Coder hat sich neu positioniert: „self-hosted platform for cloud
development environments **and AI coding agents**" with eigenem
**AI Gateway** („Centralize authentication, auditing, and cost controls
for AI tooling"). Verifiziert im Repo-Baum:

- `enterprise/cli/aigateway*.go`, `enterprise/coderd/aigatewaykeys.go`,
  `helm/ai-gateway`, `codersdk/aigatewaykeys.go` → **AI Gateway ist
  Premium/Enterprise** (liegt im enterprise/-Baum), not OSS-Kern.
- Workspaces „connected through a secure WireGuard® tunnel" → sie
  betten ein proprietäres Tailnet ein; wir nutzen Headscale
  (Standard-Tailscale-Client, austauschbar, MIT/BSD-Stack).
- „No API keys in workspaces, user identity on every action" →
  bestätigt unsere Architecture (Proxy hält Keys, Workspace bekommt
  nur Identität). Sie validieren den Markt for genau das, was
  TASK-011 + Keypool schon bauen.

**Überlappung ist real, aber:** ihr Gateway ist Enterprise-licensed and
agent-zentriert; unser Multi-Provider-Routing (Chains, Failover,
Bandit-Gewichte, Keypool-Cooldown) existiert dort not. Ihr Vorsprung
bleibt Terraform-Template-Marktplatz + Workspace-UX-Reife.

### 10.2 Service-Accounts for Deployments (M2M — „no LLM keys in workspaces")

**Entschieden (Operator):** Deployments/Workspaces bekommen **Service
Accounts** statt LLM-Provider-Keys. LLM-Credentials liegen NIE im
Container (Vault + Keypool bleiben die einzige Quelle).

```
Workspace-/Agent-Container
  ├─ bekommt: Service-Account-Token (kurzlebig, an Container-ID gebunden)
  └─ bekommt NICHT: LLM-Provider-Keys (nie — Vault-only, Mandat 9)
        │
        ▼
OpenMesh-Gateway /v1/*
  ├─ Auth: Service-Account → Workspace → Projekt → Budget-Cascade
  ├─ Routing-Chain/Failover (echte Provider-Keys from Vault/Keypool)
  └─ Audit: jede Anfrage on die Workspace-Identität attribuiert
        │
        ▼
OpenAI / Anthropic / Gemini / …
```

**Bausteine, die es schon geben:** `store.CreateSession` +
Session-Token-Injektion (TASK-011, live), Keypool (Provider-Keys nur im
Gateway), M2M-Vorbild `cnf.x5t#S256` (RFC 8705, sc-gateway, TASK-002),
Budget-Cascade (TASK-016-Entwurf).

**Was fehlt (→ Sprint 35 WP1-Erweiterung):**
- [ ] `proxy_keys`-Tabelle um `kind` (`user` | `service`) ergänzen;
      Service-Account-Keys sind an `workspace_id` gebunden, not an
      `user_id`.
- [ ] Gateway-Auth-Pfad: Service-Account-Key → Workspace-Identität →
      Budget (not User-Budget — Projekt-Budget).
- [ ] Deployment-Engine: beim Spawn Service-Account-Key minten +
      injizieren (TASK-011-Muster), NIE `OPENAI_API_KEY` o.ä.
- [ ] Audit-Log: `workspace_id` on jede /v1-Request (Sprint-30-Hook).

### 10.3 Terraform-Presets — was wir MITNEHMEN (Muster, not Code)

Das gefällt dem Operator zu Recht: **deklarative, versionierbare,
teilbare Workspace-Definitionen**. Übersetzung on OpenMesh without
Terraform-Verpflichtung:

- OpenMesh-„Framework-Presets" (dsh/code-server/…) werden **deklarative
  Templates** (YAML with Variablen) statt hardcoded Deploy-Options in
  `projects_ssh.go`.
- Ein Template beschreibt: Image, gVisor an/from, Netzwerk-Profil
  (Mesh-Tag, Egress-Regeln), IDE-Wahl (terminal/code-server/none),
  Budget-Defaults, Env-Injektionen (Service-Account, nie Secrets).
- Preset-Bibliothek im Repo (`config/presets/*.yaml`) — später vom
  Operator erweiterbar, wie Coder-Registry, aber without Terraform-Runtime.
  Optional später ein Terraform-Treiber hinter demselben Interface
  (R35 §2.2 Lifecycle-Referenz).
