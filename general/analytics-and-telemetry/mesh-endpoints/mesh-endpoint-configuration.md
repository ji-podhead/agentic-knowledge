---
okf_version: "1.0"
id: "okf-ana-mes-mesh-endpoint-configuration"
title: "R2 — Coding Deployment Config: Redeploy vs Hot-Reload"
topic: "general/analytics-and-telemetry"
subtopic: "mesh-endpoints"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - analytics-and-telemetry
  - mesh-endpoints
summary: "Welche deployments brauchen redeploy vs hot-reload? Wie editieren wir config files?"
---

# R2 — Coding Deployment Config: Redeploy vs Hot-Reload

## Architectural Question
Welche deployments brauchen redeploy vs hot-reload? Wie editieren wir config files?

## Research Objectives

### 1. Deployment Types catalog
Für jeden Typ: was ändert sich per config? Was braucht rebuild?

| Typ | Config file | Config change = | Code change = |
|---|---|---|---|
| DSH (DeepSeek Harness) | `vconfig.json` | hot-reload (client HMR) | rebuild backend |
| OpenCode | `config.json` / `.opencode` | restart | git pull + restart |
| The Multi-Provider Gateway backend | `docker-compose.yml` env | restart-backend | rebuild Go binary |
| The Multi-Provider Gateway frontend | `.env` | frontend-clean | frontend-clean |
| LeadScraper | ? | ? | ? |
| Custom HTTP server | env vars | restart | depends |

- [ ] DSH: wie genau funktioniert client-plugin HMR? Reicht `pnpm run dev:web`?
- [ ] DSH: was passiert at proto changes? (protoc rebuild nötig)
- [ ] OpenCode: welche config files? Wie restart?
- [ ] LeadScraper: wie deployed? Docker? PM2? Bare process?

### 2. Config Editor
- [ ] Monaco Editor: bundle size? React wrapper (`@monaco-editor/react`)?
- [ ] CodeMirror 6: lighter? Better for config files?
- [ ] Syntax highlight for JSON, YAML, TOML?
- [ ] Diff view: show what changed before save?
- [ ] Read/write access: direkter filesystem access or via API?

### 3. Restart Mechanism
- [ ] `POST /api/projects/{id}/restart` — wie implementiert?
  - Docker: `docker compose restart {service}`
  - Process: `pkill + restart`
  - PM2: `pm2 restart {name}`
- [ ] Graceful shutdown: health check bis restart fertig?
- [ ] Rollback: config backup before änderung?

### 4. Settings Button UX
- [ ] Wo platziert? Oben links on deployment card nervt — besser als ⚙ Icon?
- [ ] Modal vs inline panel?
- [ ] "Apply & Restart" vs "Apply & Hot-Reload" button — wann welcher?

## Output Format
Tabelle pro deployment typ with: config path, hot-reload ja/nein, restart command.
Recommendation for editor library and restart mechanismus.

---

Hier ist die systematische Aufschlüsselung for deine Deployment-Konfigurationen sowie die Recommendations for den Editor and Neustart-Mechanismus.1. Deployment-Types KatalogTypConfig-PfadConfig Change (Verhalten)Code Change (Verhalten)Restart Command (Backend-Vorgehen)DSH (DeepSeek Harness)vconfig.jsonHot-Reload (Client HMR via pnpm run dev:web)Rebuild Backend (at .proto Changes: protoc Rebuild nötig)Kein Restart at Config, da In-Memory-HMR; at Proto-Wechsel: pkill -f dsh-backend && go run main.goOpenCodeopencode.json / tui.jsonRestart erforderlichGit Pull + Restartopencode restart (or kill des TUI-Prozesses)The Multi-Provider Gateway Backenddocker-compose.yml (env)Restart-BackendRebuild Go Binarydocker compose restart llm-mesh-gateway-backendThe Multi-Provider Gateway Frontend.envFrontend-Clean (Vite/Webpack Cache-Wipe + Rebuild)Frontend-Clean (Vite HMR/Rebuild)docker compose exec llm-mesh-gateway-frontend npm run buildLeadScraperconfig.prod.json / .envRestartPM2 Reload / Pullpm2 restart lead-scraper --update-envCustom HTTP Server.env / Custom JSONRestartDepends (z. B. Node.js Restart vs. Go Rebuild)pkill -f custom-server && npm run start (or entsprechendes Binary)DSH HMR: pnpm run dev:web reicht for Frontend-Plugins völlig from. Ändern sich jedoch Protokolldefinitionen (.proto), muss die gRPC-Struktur about den protoc-Compiler neu generiert werden, was einen Backend-Rebuild erzwingt. [1] (https://medium.com/@dhleee0123/live-reload-vs-hot-deploy-with-hot-reload-and-hot-swap-260574c6e47c)OpenCode Details: Nutzt opencode.json (or opencode.jsonc for Kommentare) im Projektexekutions-Pfad. Änderungen an LLM-Providern or Keybindings greifen erst after einem Prozess-Neustart. [1] (https://opencode.ai/docs/config/), [2] (https://opencode.ai/docs/references/), [3] (https://www.josean.com/posts/how-to-use-opencode-ai)LeadScraper: Läuft in der Regel als Node.js/Python-Scraper-Skript, gemanagt via PM2 for stabiles Error-Handling at Timeout-Crashes.2. Config Editor: CodeMirror 6 vs. MonacoBewertung & Recommendation: Nutze CodeMirror 6 (about @uiw/react-codemirror). Monaco Editor (@monaco-editor/react) ist zwar mächtig, bläht das Bundle-Size jedoch enorm on (oft >4MB via Web-Worker) and verlangsamt das Dashboard beim Rendern mehrerer Instanzen drastisch. CodeMirror 6 ist modular aufgebaut, extrem leichtgewichtig, performant innerhalb von Iframes/Grids and bietet native, vollwertige Extensions for Syntax-Highlighting (JSON, YAML, TOML) sowie ein exzellentes, schlankes Diff-View-Addon.Schreib-/Lesezugriff: Der Zugriff muss ausschließlich via Backend-API (GET/POST /api/projects/{id}/config) erfolgen. Direkter Dateisystemzugriff from dem Browser heraus bricht Sandbox-Richtlinien and verhindert Berechtigungsprüfungen (z. B. Validierung des JSON-Schemas before dem Schreiben).3. Restart Mechanism & RobustheitImplementierung der API: POST /api/projects/{id}/restart steuert je after Deployment-Typ die jeweilige Engine an:Docker: Nutzt das offizielle dockerode NPM-Paket for den API-Aufruf (container.restart()) statt Shell-Execs.PM2: Nutzt das programmatische pm2.restart(name, err => {}) SDK.Prozess: Sendet SIGTERM for Graceful Shutdowns, wartet 5 Sekunden, gefolgt von SIGKILL at Timeouts.Graceful Shutdown & Rollback: Vor jedem Schreibvorgang legt das Backend ein Backup an (config.json.bak). Nach dem Restart-Befehl geht das Dashboard in den Zustand building/restarting. Eine HTTP-Polling-Schleife (or ein Health-Check-Endpoint des Projekts) prüft die Erreichbarkeit. Schlägt der Health-Check for 30 Sekunden fehl, kopiert das Backend die .bak-Datei zurück and triggert einen automatischen Rollback-Neustart.4. Settings Button UXPlatzierung: Platziere das ⚙️-Icon oben rechts in der Fenster-Menüleiste (Window Header) des jeweiligen Grid-Fensters (neben Miniminieren/Maximieren). Auf der Deployment-Card selbst blockiert es den Lesefluss.Panel-Typ: Nutze ein Inline-Slide-Over-Panel (Drawer), das sich von rechts in das spezifische Grid-Fenster hineinschiebt. Ein modales Overlay (Modal) reißt den Nutzer from dem Dashboard-Kontext, während ein Inline-Panel das parallele Beobachten von Log-Fenstern im Dashboard erlaubt.Button-Logik: Der primäre Aktionsbutton passt sich dynamisch an das Deployment an:Erkennt das System ein DSH-Projekt, heißt der Button "Save & Apply" (grün, führt reines Hot-Reload from).Bei OpenCode or Docker-Systemen heißt er "Save & Restart" (orange/blau, warnt visuell before einer kurzen Downtime).🛠 Vorgeschlagene UI-Komponente for den Editortsximport CodeMirror from '@uiw/react-codemirror';
import { json } from '@codemirror/lang-json';
import { yaml } from '@codemirror/lang-yaml';

export function ConfigDrawer({ project, onClose }) {
  const isHotReload = project.type === 'DSH';

  return (
    <div className="drawer-container">
      <div className="drawer-header">
        <h3>Konfiguration: {project.name}</h3>
        <button onClick={onClose}>✕</button>
      </div>

      <CodeMirror
        value={project.configString}
        extensions={[project.format === 'yaml' ? yaml() : json()]}
        theme="dark"
      />

      <div className="drawer-footer">
        <button className="btn-secondary" onClick={onClose}>Abbrechen</button>
        <button className={isHotReload ? "btn-hotreload" : "btn-restart"}>
          {isHotReload ? "⚡ Apply & Hot-Reload" : "🔄 Apply & Restart Project"}
        </button>
      </div>
    </div>
  );
}
Möchtest du als Nächstes den TypeScript-Types-Entwurf for das Config-Validierungs-Schema sehen, or sollen wir die API-Routen for den Backup- and Rollback-Mechanismus im Backend definieren?
