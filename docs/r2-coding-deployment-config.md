---
id: "R2"
title: "R2 — Coding Deployment Config: Redeploy vs Hot-Reload"
type: research
date: 2026-09-06
status: final
tags: [docker, mesh]
license: CC-BY-4.0
---

# R2 — Coding Deployment Config: Redeploy vs Hot-Reload

## Frage
Welche deployments brauchen redeploy vs hot-reload? Wie editieren wir config files?

## Recherche-Aufgaben

### 1. Deployment Typen katalogisieren
Für jeden Typ: was ändert sich per config? Was braucht rebuild?

| Typ | Config file | Config change = | Code change = |
|---|---|---|---|
| DSH (DeepSeek Harness) | `vconfig.json` | hot-reload (client HMR) | rebuild backend |
| OpenCode | `config.json` / `.opencode` | restart | git pull + restart |
| JiMesh backend | `docker-compose.yml` env | restart-backend | rebuild Go binary |
| JiMesh frontend | `.env` | frontend-clean | frontend-clean |
| LeadScraper | ? | ? | ? |
| Custom HTTP server | env vars | restart | depends |

- [ ] DSH: wie genau funktioniert client-plugin HMR? Reicht `pnpm run dev:web`?
- [ ] DSH: was passiert bei proto changes? (protoc rebuild nötig)
- [ ] OpenCode: welche config files? Wie restart?
- [ ] LeadScraper: wie deployed? Docker? PM2? Bare process?

### 2. Config Editor
- [ ] Monaco Editor: bundle size? React wrapper (`@monaco-editor/react`)?
- [ ] CodeMirror 6: lighter? Better for config files?
- [ ] Syntax highlight für JSON, YAML, TOML?
- [ ] Diff view: show what changed before save?
- [ ] Read/write access: direkter filesystem access oder via API?

### 3. Restart Mechanism
- [ ] `POST /api/projects/{id}/restart` — wie implementiert?
  - Docker: `docker compose restart {service}`
  - Process: `pkill + restart`
  - PM2: `pm2 restart {name}`
- [ ] Graceful shutdown: health check bis restart fertig?
- [ ] Rollback: config backup vor änderung?

### 4. Settings Button UX
- [ ] Wo platziert? Oben links auf deployment card nervt — besser als ⚙ Icon?
- [ ] Modal vs inline panel?
- [ ] "Apply & Restart" vs "Apply & Hot-Reload" button — wann welcher?

## Output Format
Tabelle pro deployment typ mit: config path, hot-reload ja/nein, restart command.
Empfehlung für editor library und restart mechanismus.

---

Hier ist die systematische Aufschlüsselung für deine Deployment-Konfigurationen sowie die Empfehlungen für den Editor und Neustart-Mechanismus.1. Deployment-Typen KatalogTypConfig-PfadConfig Change (Verhalten)Code Change (Verhalten)Restart Command (Backend-Vorgehen)DSH (DeepSeek Harness)vconfig.jsonHot-Reload (Client HMR via pnpm run dev:web)Rebuild Backend (bei .proto Changes: protoc Rebuild nötig)Kein Restart bei Config, da In-Memory-HMR; bei Proto-Wechsel: pkill -f dsh-backend && go run main.goOpenCodeopencode.json / tui.jsonRestart erforderlichGit Pull + Restartopencode restart (oder kill des TUI-Prozesses)JiMesh Backenddocker-compose.yml (env)Restart-BackendRebuild Go Binarydocker compose restart jimesh-backendJiMesh Frontend.envFrontend-Clean (Vite/Webpack Cache-Wipe + Rebuild)Frontend-Clean (Vite HMR/Rebuild)docker compose exec jimesh-frontend npm run buildLeadScraperconfig.prod.json / .envRestartPM2 Reload / Pullpm2 restart lead-scraper --update-envCustom HTTP Server.env / Custom JSONRestartDepends (z. B. Node.js Restart vs. Go Rebuild)pkill -f custom-server && npm run start (oder entsprechendes Binary)DSH HMR: pnpm run dev:web reicht für Frontend-Plugins völlig aus. Ändern sich jedoch Protokolldefinitionen (.proto), muss die gRPC-Struktur über den protoc-Compiler neu generiert werden, was einen Backend-Rebuild erzwingt. [1] (https://medium.com/@dhleee0123/live-reload-vs-hot-deploy-with-hot-reload-and-hot-swap-260574c6e47c)OpenCode Details: Nutzt opencode.json (oder opencode.jsonc für Kommentare) im Projektexekutions-Pfad. Änderungen an LLM-Providern oder Keybindings greifen erst nach einem Prozess-Neustart. [1] (https://opencode.ai/docs/config/), [2] (https://opencode.ai/docs/references/), [3] (https://www.josean.com/posts/how-to-use-opencode-ai)LeadScraper: Läuft in der Regel als Node.js/Python-Scraper-Skript, gemanagt via PM2 für stabiles Error-Handling bei Timeout-Crashes.2. Config Editor: CodeMirror 6 vs. MonacoBewertung & Empfehlung: Nutze CodeMirror 6 (über @uiw/react-codemirror). Monaco Editor (@monaco-editor/react) ist zwar mächtig, bläht das Bundle-Size jedoch enorm auf (oft >4MB via Web-Worker) und verlangsamt das Dashboard beim Rendern mehrerer Instanzen drastisch. CodeMirror 6 ist modular aufgebaut, extrem leichtgewichtig, performant innerhalb von Iframes/Grids und bietet native, vollwertige Extensions für Syntax-Highlighting (JSON, YAML, TOML) sowie ein exzellentes, schlankes Diff-View-Addon.Schreib-/Lesezugriff: Der Zugriff muss ausschließlich via Backend-API (GET/POST /api/projects/{id}/config) erfolgen. Direkter Dateisystemzugriff aus dem Browser heraus bricht Sandbox-Richtlinien und verhindert Berechtigungsprüfungen (z. B. Validierung des JSON-Schemas vor dem Schreiben).3. Restart Mechanism & RobustheitImplementierung der API: POST /api/projects/{id}/restart steuert je nach Deployment-Typ die jeweilige Engine an:Docker: Nutzt das offizielle dockerode NPM-Paket für den API-Aufruf (container.restart()) statt Shell-Execs.PM2: Nutzt das programmatische pm2.restart(name, err => {}) SDK.Prozess: Sendet SIGTERM für Graceful Shutdowns, wartet 5 Sekunden, gefolgt von SIGKILL bei Timeouts.Graceful Shutdown & Rollback: Vor jedem Schreibvorgang legt das Backend ein Backup an (config.json.bak). Nach dem Restart-Befehl geht das Dashboard in den Zustand building/restarting. Eine HTTP-Polling-Schleife (oder ein Health-Check-Endpoint des Projekts) prüft die Erreichbarkeit. Schlägt der Health-Check für 30 Sekunden fehl, kopiert das Backend die .bak-Datei zurück und triggert einen automatischen Rollback-Neustart.4. Settings Button UXPlatzierung: Platziere das ⚙️-Icon oben rechts in der Fenster-Menüleiste (Window Header) des jeweiligen Grid-Fensters (neben Miniminieren/Maximieren). Auf der Deployment-Card selbst blockiert es den Lesefluss.Panel-Typ: Nutze ein Inline-Slide-Over-Panel (Drawer), das sich von rechts in das spezifische Grid-Fenster hineinschiebt. Ein modales Overlay (Modal) reißt den Nutzer aus dem Dashboard-Kontext, während ein Inline-Panel das parallele Beobachten von Log-Fenstern im Dashboard erlaubt.Button-Logik: Der primäre Aktionsbutton passt sich dynamisch an das Deployment an:Erkennt das System ein DSH-Projekt, heißt der Button "Save & Apply" (grün, führt reines Hot-Reload aus).Bei OpenCode oder Docker-Systemen heißt er "Save & Restart" (orange/blau, warnt visuell vor einer kurzen Downtime).🛠 Vorgeschlagene UI-Komponente für den Editortsximport CodeMirror from '@uiw/react-codemirror';
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
Möchtest du als Nächstes den TypeScript-Typen-Entwurf für das Config-Validierungs-Schema sehen, oder sollen wir die API-Routen für den Backup- und Rollback-Mechanismus im Backend definieren?MediumLive Reload vs. Hot Deploy (with Hot Reload and Hot Swap) | by leedohyung28 | Medium08.12.2025 — Hot Reload only replaces the changed module for refresh. Hot Reload can be used in the following situations: * **Frontend HMR** * ...OpenCodeConfig | OpenCode03.09.2026 — * Usage. * Configure. ... Config. Using the OpenCode JSON config. You can configure OpenCode using a JSON config file. Format * "m...OpenCodeConfig - OpenCodePer project. 프로젝트 루트에 opencode.json 을 추가하세요. 프로젝트 config는 표준 config 파일 중 우선순위가 가장 높아 전역 및 Remote config를 모두 override합니다. 프로젝트별 TUI...