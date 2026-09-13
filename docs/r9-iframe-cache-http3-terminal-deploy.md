---
id: "R9"
title: "R9 — Server-Side Iframe Cache mit HTTP/3"
type: research
date: 2026-09-06
status: final
tags: [mesh, entropy, logprobs, llama, docker]
license: CC-BY-4.0
---

# R9 — Server-Side Iframe Cache mit HTTP/3

## Frage
Wäre es schlauer den iframe cache server-side zu machen und über HTTP/3 zu
porten, statt client-side (browser hidden pool)? Was bringt HTTP/3 hier?

## Recherche-Aufgaben

### 1. HTTP/3 (QUIC) für iframe caching
- [ ] Was ist HTTP/3 / QUIC?
  - UDP-based, multiplexed streams, 0-RTT connection resumption
  - Kein head-of-line blocking (im gegensatz zu HTTP/2 TCP)
  - Connection migration (IP wechsel ohne reconnect)
- [ ] Kann Go HTTP/3 server?
  - `quic-go` library — Go HTTP/3 implementation
  - `golang.org/x/net/http3` — experimental
  - Production-ready? Stability? Performance?
- [ ] Browser HTTP/3 support?
  - Chrome, Firefox, Safari — alle support HTTP/3?
  - Wird iframe content über HTTP/3 faster geladen?
  - 0-RTT: kann der browser eine "warm" connection für iframe cache nutzen?
- [ ] JiMesh als HTTP/3 proxy für iframe content?
  - JiMesh cached iframe content server-side
  - Client fragt JiMesh an → JiMesh hat gecacht → instant response
  - JiMesh fetcht im hintergrund neu (stale-while-revalidate)
  - HTTP/3 0-RTT für die connection zwischen client und JiMesh

### 2. Server-Side Cache Strategien
- [ ] Cache was genau?
  - Option A: Full HTML response vom target project (reverse proxy cache)
  - Option B: Nur die "skeleton" HTML + JS bundles (service worker style)
  - Option C: SSR snapshot (rendered DOM state)
- [ ] Cache invalidation:
  - TTL-based (wie im client approach: 300s)
  - Stale-while-revalidate (serve old, fetch new in background)
  - ETag / Last-Modified vom target
  - WebSocket/SSE push invalidation vom target project
- [ ] Cache storage:
  - In-memory (Go map + LRU)
  - Redis (bereits vorhanden)
  - Disk (für große HTML responses)
- [ ] Max cache size:
  - Memory limit (z.B. 100MB)
  - LRU eviction
  - Per-project max size

### 3. Client-Side vs Server-Side Vergleich
| Aspect | Client-Side (hidden iframe pool) | Server-Side (HTTP/3 cache) |
|---|---|---|
| Speed | Instant (DOM already in memory) | Fast (cached HTML, but browser must render) |
| Memory | Browser tab memory (N iframes) | Server memory (N cached responses) |
| State | Full app state preserved (JS running) | Only HTML/JS cached (state lost on re-render) |
| Complexity | Low (CSS display:none) | High (reverse proxy + cache logic) |
| HTTP/3 benefit | None (iframes talk directly to target) | Yes (0-RTT, multiplexing to cache server) |
| Refresh | Tab switch = instant | Needs re-render even with cache |
| Limitation | Max iframes = browser memory | State not preserved (SPA resets) |

### 4. Hybrid Approach?
- [ ] Client-side hidden pool for SPA state preservation (instant switch)
- [ ] Server-side cache for initial load speed (HTTP/3 0-RTT)
- [ ] Server-side pre-warming: JiMesh fetches project HTML on startup
  → first iframe load is instant (served from cache)
  → subsequent tab switches use client-side hidden pool
- [ ] HTTP/3 für die connection zwischen dashboard und JiMesh cache server
  → 0-RTT für cached responses → minimal latency

### 5. Implementation Complexity
- [ ] Go HTTP/3 server: quic-go library, cert management (self-signed OK für localhost?)
- [ ] Reverse proxy cache: Go http.Handler mit cache layer
- [ ] Cache invalidation: wie weiß JiMesh dass sich das project geändert hat?
  - Health endpoint poll?
  - File watcher auf project config?
  - Version header vom project?
- [ ] Browser support: muss browser HTTP/3 für localhost unterstützen?
  - Chrome: ja (quic://localhost oder alt-svc header)
  - Firefox: ja
  - Safari: ja (ab version 14+)

### 6. Terminal Deployment Type
- [ ] "Terminal" als deployment type (neben dsh, opencode, vscode-server, custom)
- [ ] Sub-types:
  - Provider-based: Claude Code (Anthropic CLI), Aider, OpenCode CLI
  - Predefined image: image mit dev tools (git, go, node, python) + provider
  - Plain terminal: just a shell, no AI provider
- [ ] Wie deployen?
  - Docker container mit ttyd / gotty (web terminal)
  - Oder xterm.js + WebSocket (wie vscode integrated terminal)
- [ ] Icons pro deployment type (material icons, lucide, custom SVG)

### 6. Layered Deployment Schemas (EXTENSIBLE)

Das core konzept: ein deployment = base medium + N provider/app addons + user overrides.

```
Deployment "Leo's Coding Terminal"
├── Base Medium: terminal (ttyd, git, go, node, python)
│   └── schema: { shell, packages, env, ports }
│
├── Addon: Claude Code (Anthropic CLI)
│   └── schema: { provider: anthropic, api_key, model, presets }
│   └── additional packages: anthropic-cli
│   └── additional presets: claude-code-config
│
├── Addon: Aider (optional)
│   └── schema: { provider: openai-compatible, base_url, model }
│   └── additional packages: aider
│
└── User Override:
    └── custom env vars, custom packages, custom presets
```

- [ ] **Base Medium Schema** (pro medium type):
  - `terminal`: { shell: bash/zsh, packages: [git, vim, curl], ports: [7681] }
  - `dsh`: { framework: dsh, ports: [3079], volumes: [dsh-data] }
  - `opencode`: { config: opencode.json, ports: [3080] }
  - `vscode-server`: { extensions, ports: [8080] }
  - `custom`: { user-defined }

- [ ] **Provider/App Addon Schema** (pro addon):
  - `claude-code`: { provider: anthropic, packages: [anthropic-cli], presets: [claude-config] }
  - `aider`: { provider: openai-compatible, packages: [aider], presets: [aider-config] }
  - `jimesh-mesh`: { provider: jimesh, packages: [], presets: [mesh-provision] }  ← auto-provision!
  - User kann eigene addons definieren: { name, packages, presets, config_schema }

- [ ] **Schema Registry** (DB):
  - `deployment_schemas` table: id, medium_type, name, description, config_schema (JSONB)
  - `deployment_addons` table: id, name, medium_type, packages (JSONB), presets (JSONB), config_schema (JSONB)
  - Schemas definieren welche settings Felder es gibt (TypeScript-style schema → frontend form generator)
  - User kann eigene schemas erstellen (custom addons)

- [ ] **Schema Composition**:
  - Base medium schema + addon schemas = merged config schema
  - Frontend rendert form basierend auf merged schema
  - Felder die in mehreren schemas definiert sind: addon überschreibt base
  - User overrides überschreiben alles
  - Beispiel: base terminal hat `shell: bash`, Claude Code addon fügt `provider: anthropic` hinzu,
    user override setzt `shell: zsh`

- [ ] **Preset System** (pro addon):
  - Claude Code presets: { model: claude-sonnet, max_tokens: 8192, system_prompt: ... }
  - Aider presets: { model: gpt-4o, edit_format: diff, auto_commits: true }
  - JiMesh mesh presets: { chain_id: smart:coding-free, auto_provision: true }
  - Presets = config templates die der user auswählen und anpassen kann

- [ ] **Medium-specific vs Addon-specific Settings**:
  - DSH medium: hat DSH-spezifische presets (code mode, standard mode, etc.)
  - Terminal medium: hat terminal-spezifische settings (shell, packages)
  - Claude Code addon: hat claude-spezifische settings (model, api_key)
  - Wenn man Claude Code zu DSH hinzufügt → merged schema = DSH settings + Claude settings
  - Wenn man Claude Code zu terminal hinzufügt → merged schema = terminal settings + Claude settings
  - Selber addon, anderes base medium → andere merged config

## Output Format

---

## Research Results (Operator-Provided)

### 1. HTTP/3 Server-Side Iframe Cache

HTTP/3 (QUIC) Connection Migration: HTTP/3 nutzt Connection IDs anstelle von
IP/Port-Tupeln. Zerreißt das Frontend das Iframe im DOM und mountet es in einer
anderen Grid-Kachel neu, wird die bestehende HTTP/3-Session ohne TCP-Handshake-
Latenz (0-RTT) sofort fortgesetzt.

Server-Side Content Caching: Der JiMesh-Proxy puffert die letzten Chunks des
HTTP-Projekts im Arbeitsspeicher. Beim Neu-Mounten des Iframes liefert der
Server den exakten HTML/JS-Snapshot aus, wodurch die Applikation visuell nicht
flackert und Sessions erhalten bleiben.

```
[Browser Iframe] ◄──(HTTP/3 QUIC: 0-RTT, Multi-Streaming)──► [JiMesh Go Core Proxy]
       │                                                          │
(DOM Move/Resize)                                          (State Snapshot)
       │                                                          │
       ▼                                                          ▼
[New Viewport] ◄──(Stream Resume via QUIC Connection ID)───► [Serve from Cache]
```

**Decision**: Server-side reverse proxy cache with HTTP/3 QUIC. Go core caches
iframe content state, 0-RTT session resume on DOM remount.

### 2. Layered Deployment Schema Icons

| Component | Icon | Color |
|---|---|---|
| Base: Terminal | TerminalIcon (Lucide) | Deep Charcoal |
| Base: DSH | CpuIcon (Lucide) | NVIDIA Green / DeepSeek Blue |
| Addon: Claude Code | AntropicIcon (Custom SVG) | Clay-Orange |
| Addon: Aider | WrenchIcon (Material) | Spark-Yellow |

### 3. Composition Schema

```json
{
  "deployment_id": "dep_12345",
  "base_medium": {
    "type": "terminal",
    "image": "ubuntu-lts-jimesh-base:latest",
    "shell": "/bin/bash",
    "ports": [7681]
  },
  "addons": [
    {
      "id": "claude-code",
      "provider": "anthropic",
      "packages": ["@anthropic-ai/claude-code"],
      "env_presets": {
        "ANTHROPIC_API_KEY": "${USER_SECRET_CLAUDE_KEY}",
        "CLAUDE_CODE_MODEL": "claude-3-5-sonnet"
      }
    }
  ],
  "user_overrides": {
    "env": { "CUSTOM_ALIAS": "llm-dev" }
  }
}
```

---

## Frage
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
mit drag-resize-split-screen?

## Recherche-Aufgaben

### 1. Grid Layout Library vergleichen
Teste diese Libraries und bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` oder `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues bei resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues mit iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir auf `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistenz
- [ ] localStorage vs PostgreSQL — was ist besser für layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze mit Bewertung + Empfehlung + Link.
Entscheidung am Ende: welche Library, welches Layout-Schema, wie iframe embedding.Hier ist die strukturierte Bewertung und Architektur-Empfehlung für dein Multi-Window Dashboard Grid.1. Grid Layout Library VergleichBewertung: Für ein Dashboard mit Iframe-Fokus ist react-grid-layout (RGL) am besten erprobt, da es Freiform-Grids bietet und in Version 2 vollen React 18+ und TypeScript-Support hat. golden-layout bietet zwar exzellentes IDE-Docking, kämpft aber stark mit Iframes, da Tabs das DOM oft komplett zerstören/neu aufbauen, was Iframe-Resets erzwingt. react-mosaic-component (Tiling) und allotment (VS Code Split Panes) bieten saubere, serielle Tree-Layouts mit guter TypeScript-Integration und kleiner Bundle Size, schränken aber die freie Dashboard-Anordnung im Vergleich zu RGL ein. Der kritische Punkt bei allen Libraries im Zusammenspiel mit Drag-und-Resize ist das "Iframe-Pointer-Capture-Problem": Sobald die Maus beim Ziehen über einen Iframe rutscht, schluckt dieser die Mouse-Events, und der Drag-Vorgang bricht ab. [1] (https://www.npmjs.com/package/react-grid-layout), [2] (https://www.npmjs.com/package/react-mosaic-component), [3] (https://www.npmjs.com/package/allotment?activeTab=dependencies)Empfehlung: Nutze react-grid-layout, wenn du klassische Dashboard-Widgets willst, oder react-mosaic-component, wenn ein striktes Kachel-Splitting (wie in einer IDE) gewünscht ist. Um das Iframe-Problem bei beiden zu lösen, musst du während des Drag/Resize-Vorgangs via globalem CSS-State pointer-events: none auf alle Iframes legen. [1] (https://www.npmjs.com/package/react-mosaic-component), [2] (https://www.npmjs.com/package/react-grid-layout)2. Iframe EmbeddingBewertung: Aus Sicherheitsgründen ist das Attribut sandbox="allow-scripts allow-same-origin" absolut kritisch; ohne allow-same-origin können Cookies/LocalStorage nicht richtig genutzt werden, während allow-scripts die Applikation im Iframe überhaupt erst lauffähig macht. Cross-Origin-Zugriffe zwischen localhost:9090 und localhost:9091 werden vom Browser blockiert (Same-Origin-Policy), weshalb direkter JS-Zugriff scheitert und Kommunikation ausschließlich via window.postMessage() erfolgen muss. Zudem müssen die eingebetteten Projekte zwingend darauf vorbereitet sein, in Iframes zu laufen: Wenn sie X-Frame-Options: DENY oder restriktive CSPs (frame-ancestors 'none') konfiguriert haben, blockiert der Browser das Laden im Dashboard vollständig. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)Empfehlung: Bette die Projekte mit sandbox="allow-scripts allow-same-origin allow-forms allow-popups" ein. Stelle sicher, dass die Quellprojekte keinen X-Frame-Options Header senden, sondern stattdessen Content-Security-Policy: frame-ancestors http://localhost:dashboard-port restriktiv setzen, und nutze eine CSS-Klasse mit width: 100%; height: 100%, um dem Iframe das automatische Skalieren des Layout-Containers zu überlassen. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)3. Layout PersistenzBewertung: localStorage eignet sich hervorragend für temporäre Benutzerpräferenzen, UI-Zustände auf Client-Seite und schnelles Prototyping ohne Latenz. PostgreSQL ist zwingend erforderlich, um Layouts persistent über mehrere Endgeräte hinweg zu speichern, geteilte Team-Templates bereitzustellen und Datenverlust beim Löschen von Browserdaten zu verhindern. Ein serialisierbares JSON-Schema reicht für beide Speicherarten völlig aus. Vordefinierte Templates (z. B. Coding, Debugging) lassen sich serverseitig als statische JSON-Schemata hinterlegen und per Knopfdruck laden.Empfehlung: Nutze PostgreSQL als Single Source of Truth für gespeicherte Layouts, puffere Änderungen im Frontend via Debounce und nutze ein Schema, das flexibel genug für Erweiterungen ist.Layout Schema:json{
  "layoutId": "uuid-v4",
  "userId": "uuid-v4",
  "name": "Debugging Template",
  "windows": [
    {
      "id": "win-1",
      "projectId": "proj-abc",
      "grid": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "state": { "minimized": false, "maximized": false, "activeTab": "logs" }
    }
  ]
}

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
Empfehlung für editor library und restart mechanismus.Hier ist die systematische Aufschlüsselung für deine Deployment-Konfigurationen sowie die Empfehlungen für den Editor und Neustart-Mechanismus.1. Deployment-Typen KatalogTypConfig-PfadConfig Change (Verhalten)Code Change (Verhalten)Restart Command (Backend-Vorgehen)DSH (DeepSeek Harness)vconfig.jsonHot-Reload (Client HMR via pnpm run dev:web)Rebuild Backend (bei .proto Changes: protoc Rebuild nötig)Kein Restart bei Config, da In-Memory-HMR; bei Proto-Wechsel: pkill -f dsh-backend && go run main.goOpenCodeopencode.json / tui.jsonRestart erforderlichGit Pull + Restartopencode restart (oder kill des TUI-Prozesses)JiMesh Backenddocker-compose.yml (env)Restart-BackendRebuild Go Binarydocker compose restart jimesh-backendJiMesh Frontend.envFrontend-Clean (Vite/Webpack Cache-Wipe + Rebuild)Frontend-Clean (Vite HMR/Rebuild)docker compose exec jimesh-frontend npm run buildLeadScraperconfig.prod.json / .envRestartPM2 Reload / Pullpm2 restart lead-scraper --update-envCustom HTTP Server.env / Custom JSONRestartDepends (z. B. Node.js Restart vs. Go Rebuild)pkill -f custom-server && npm run start (oder entsprechendes Binary)DSH HMR: pnpm run dev:web reicht für Frontend-Plugins völlig aus. Ändern sich jedoch Protokolldefinitionen (.proto), muss die gRPC-Struktur über den protoc-Compiler neu generiert werden, was einen Backend-Rebuild erzwingt. [1] (https://medium.com/@dhleee0123/live-reload-vs-hot-deploy-with-hot-reload-and-hot-swap-260574c6e47c)OpenCode Details: Nutzt opencode.json (oder opencode.jsonc für Kommentare) im Projektexekutions-Pfad. Änderungen an LLM-Providern oder Keybindings greifen erst nach einem Prozess-Neustart. [1] (https://opencode.ai/docs/config/), [2] (https://opencode.ai/docs/references/), [3] (https://www.josean.com/posts/how-to-use-opencode-ai)LeadScraper: Läuft in der Regel als Node.js/Python-Scraper-Skript, gemanagt via PM2 für stabiles Error-Handling bei Timeout-Crashes.2. Config Editor: CodeMirror 6 vs. MonacoBewertung & Empfehlung: Nutze CodeMirror 6 (über @uiw/react-codemirror). Monaco Editor (@monaco-editor/react) ist zwar mächtig, bläht das Bundle-Size jedoch enorm auf (oft >4MB via Web-Worker) und verlangsamt das Dashboard beim Rendern mehrerer Instanzen drastisch. CodeMirror 6 ist modular aufgebaut, extrem leichtgewichtig, performant innerhalb von Iframes/Grids und bietet native, vollwertige Extensions für Syntax-Highlighting (JSON, YAML, TOML) sowie ein exzellentes, schlankes Diff-View-Addon.Schreib-/Lesezugriff: Der Zugriff muss ausschließlich via Backend-API (GET/POST /api/projects/{id}/config) erfolgen. Direkter Dateisystemzugriff aus dem Browser heraus bricht Sandbox-Richtlinien und verhindert Berechtigungsprüfungen (z. B. Validierung des JSON-Schemas vor dem Schreiben).3. Restart Mechanism & RobustheitImplementierung der API: POST /api/projects/{id}/restart steuert je nach Deployment-Typ die jeweilige Engine an:Docker: Nutzt das offizielle dockerode NPM-Paket für den API-Aufruf (container.restart()) statt Shell-Execs.PM2: Nutzt das programmatische pm2.restart(name, err => {}) SDK.Prozess: Sendet SIGTERM für Graceful Shutdowns, wartet 5 Sekunden, gefolgt von SIGKILL bei Timeouts.Graceful Shutdown & Rollback: Vor jedem Schreibvorgang legt das Backend ein Backup an (config.json.bak). Nach dem Restart-Befehl geht das Dashboard in den Zustand building/restarting. Eine HTTP-Polling-Schleife (oder ein Health-Check-Endpoint des Projekts) prüft die Erreichbarkeit. Schlägt der Health-Check für 30 Sekunden fehl, kopiert das Backend die .bak-Datei zurück und triggert einen automatischen Rollback-Neustart.4. Settings Button UXPlatzierung: Platziere das ⚙️-Icon oben rechts in der Fenster-Menüleiste (Window Header) des jeweiligen Grid-Fensters (neben Miniminieren/Maximieren). Auf der Deployment-Card selbst blockiert es den Lesefluss.Panel-Typ: Nutze ein Inline-Slide-Over-Panel (Drawer), das sich von rechts in das spezifische Grid-Fenster hineinschiebt. Ein modales Overlay (Modal) reißt den Nutzer aus dem Dashboard-Kontext, während ein Inline-Panel das parallele Beobachten von Log-Fenstern im Dashboard erlaubt.Button-Logik: Der primäre Aktionsbutton passt sich dynamisch an das Deployment an:Erkennt das System ein DSH-Projekt, heißt der Button "Save & Apply" (grün, führt reines Hot-Reload aus).Bei OpenCode oder Docker-Systemen heißt er "Save & Restart" (orange/blau, warnt visuell vor einer kurzen Downtime).🛠 Vorgeschlagene UI-Komponente für den Editortsximport CodeMirror from '@uiw/react-codemirror';
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

## Frage
Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als
provider in coding deployments (Ollama, OpenCode, DSH)?

## Recherche-Aufgaben

### 1. Ziel-Formate
Welche config formats brauchen coding tools für custom providers?

- [ ] **OpenCode**: provider config format? JSON? YAML? Wo gespeichert?
  - Suchen: OpenCode docs für custom provider / custom OpenAI endpoint
  - Felder: `base_url`, `api_key`, `model_name`?
- [ ] **Ollama**: kann Ollama einen remote OpenAI endpoint als model registrieren?
  - `ollama pull` von custom model? Modelfile mit `FROM` remote?
  - Oder besser: JiMesh als OpenAI proxy → coding tool zeigt auf `jimesh:9091`
- [ ] **DSH (DeepSeek Harness)**: provider config in vconfig.json?
  - Wie trägt man custom OpenAI endpoint ein?
  - Können wir DSH models page nutzen um JiMesh zu registrieren?
- [ ] **Cursor / VS Code**: `.cursor/config`? settings.json `openai.baseUrl`?

### 2. Provisioning API
- [ ] `POST /api/projects/{id}/provision` — body: `{ chainId, format }`
  - Liest die chain endpoint URL + deploy token aus JiMesh
  - Schreibt sie ins coding tool's config format
  - Restartet das tool falls nötig (hot-reload vs redeploy)
- [ ] Auto-provision: beim deploy eines coding projects → automatisch alle
  aktiven mesh chains als provider eintragen
- [ ] Provisioning status: erfolgreich? Config überschrieben? Backup erstellt?

### 3. Model-Namens-Mapping
- [ ] JiMesh chain name → coding tool model name
  - `smart:coding-free` → model name in OpenCode?
  - Multiple chains → multiple "models" in der auswahl?
- [ ] Model discovery: coding tool sollte `/v1/models` vom JiMesh proxy abrufen
  können → wir haben das schon (`/v1/models` endpoint)
- [ ] Brauchen wir einen dedizierten `/v1/models` der die chain-namen als
  "models" zurückgibt? (statt platform model IDs)

### 4. Mouse-Click Provisioning
- [ ] Per drag-drop: mesh endpoint aus sidebar → coding deployment config
- [ ] Per button: "Add to OpenCode" / "Add to DSH" neben jedem chain
- [ ] Per auto: checkbox "auto-provision on deploy" pro coding project
- [ ] Feedback: toast "Added smart:coding-free to OpenCode as model 'jimesh-coding-free'"

## Output Format
Pro coding tool: config path, format, fields, provisioning command.
Empfehlung: auto-provision strategy (auto vs manual vs hybrid).
Schema für `/v1/models` endpoint der chain-namen zurückgibt.Hier ist das Systemdesign für das automatische Provisionieren von JiMesh Fallback Endpoints und Modellen direkt in deine Coding-Deployments.1. Ziel-Formate der Coding ToolsToolConfig-Pfad (relativ / global)FormatWichtige Felder für Custom ProviderProvisioning Command / TriggerOpenCode~/.config/opencode/opencode.json (global) oder opencode.json (Projekt)JSON"provider": { "jimesh": { "options": { "baseURL": "...", "apiKey": "..." }, "models": { "chain-id": {} } } }POST /api/projects/{id}/config -> JSON-Patch (Kein Restart nötig bei Dateimanipulation)Ollama— (Wird als Proxy umgangen)Modelfile / APIKein Pull nötig. JiMesh agiert direkt als Proxy, sodass andere Tools auf jimesh:9091 statt auf Ollama zeigen.Keiner (JiMesh fängt /v1/chat/completions ab).DSH./vconfig.json (im Workspace)JSON"openai_compatible_providers": [{ "name": "JiMesh", "api_base": "...", "api_key": "..." }]In-Memory Hot-Reload via Client-HMR (pnpm run dev:web).Cursor / VS Code.cursorrules / .vscode/settings.jsonJSON"openai.baseUrl": "http://localhost:9091/v1", "openai.apiKey": "jimesh-token"Automatisches Einlesen durch den Datei-Watcher der IDE.OpenCode-Besonderheit: OpenCode erlaubt das Einbinden von Custom OpenAI-kompatiblen Endpunkten über die Definition eines Custom-Schlüssels im "provider"-Objekt (z. B. "jimesh"), benötigt aber zwingend die explizite Auflistung der verfügbaren Modell-IDs unter "models". [1] (https://github.com/orgs/community/discussions/200311), [2] (https://docs.ollama.com/integrations/opencode)Ollama-Strategie: Ollama über ein Modelfile mit FROM http://... zu provisionieren fügt unnedige Netzwerklatenz und Speicher-Overhead hinzu. Die Architektur-Empfehlung lautet hier klar: JiMesh als zentraler OpenAI-Proxy, an den sich die Editoren direkt hängen.2. Provisioning API (POST /api/projects/{id}/provision)Wenn ein Projekt deployt wird (oder ein neuer Mesh-Fallback-Endpoint via Drag-and-Drop hinzukommt), stößt das Dashboard die Provisionierung an:Read State: Das Backend liest die aktive Mesh-Konfiguration (Chain-URLs und Tokens) aus der JiMesh-Instanz aus.Generate Config Patch: Basierend auf dem Typ des Ziel-Deployments wird die spezifische Konfigurationsdatei manipuliert.Backup & Write: Das Backend sichert die bestehende Datei (.json.bak) und schreibt die neue Struktur atomar.HMR Trigger / Reload: Bei DSH wird der Hot-Reload-Endpoint getriggert; OpenCode liest die Projekt-opencode.json beim nächsten Befehl automatisch frisch ein.3. Model-Namens-Mapping (/v1/models)Da Editoren und CLI-Tools wie OpenCode dynamische oder statische Modelllisten erwarten, muss JiMesh einen dedizierten, standardkonformen OpenAI-Endpoint bereitstellen, der die aktiven Mesh-Chains als virtuelle Modell-IDs ausgibt. [1] (https://github.com/anomalyco/opencode/issues/26863), [2] (https://github.com/orgs/community/discussions/200311)Schema für den /v1/models Endpoint:json{
  "object": "list",
  "data": [
    {
      "id": "jimesh:smart:coding-free",
      "object": "model",
      "created": 1717545600,
      "owned_by": "jimesh-mesh"
    },
    {
      "id": "jimesh:fast:inline-completion",
      "object": "model",
      "created": 1717545600,
      "owned_by": "jimesh-mesh"
    }
  ]
}
Nutzen: In OpenCode wird das Modell dann deklarativ als jimesh/jimesh:smart:coding-free angesprochen. [1] (https://opencode.ai/docs/models/)4. UX & Provisionierungs-StrategieEmpfehlung: Hybrid-Strategie (Auto-Provision on Deploy + Manual Override via Sidebar).Ablauf:Standardmäßig ist in den Projekt-Settings die Checkbox "Auto-provision active mesh chains on deploy" aktiv. Beim Klick auf "Deploy" schreibt das System die Endpunkte vollautomatisch.Mouse-Click UX: In der linken Sidebar des Dashboards befindet sich die Liste der aktiven JiMesh-Chains. Der Entwickler kann eine Chain per Drag-and-Drop in das geöffnete Editor-Fenster (oder auf die Deployment-Card) ziehen. Ein fliegender Tooltip zeigt "Add to OpenCode as Model" an. Nach dem Drop erscheint ein Toast: „⚡ Added smart:coding-free to OpenCode as model 'jimesh:smart:coding-free'“.🛠 Beispiel für den OpenCode-Config-Patch (Backend-Logik)So sieht der JSON-Inhalt aus, den die Provisioning-Engine automatisch in die opencode.json deines Zielprojekts injiziert: [1] (https://docs.ollama.com/integrations/opencode)json{
  "$schema": "https://opencode.ai/config.json",
  "model": "jimesh/jimesh:smart:coding-free",
  "provider": {
    "jimesh": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "JiMesh Proxy",
      "options": {
        "baseURL": "http://localhost:9091/v1",
        "apiKey": "jm_live_tkn_84920f"
      },
      "models": {
        "jimesh:smart:coding-free": {},
        "jimesh:fast:inline-completion": {}
      }
    }
  }
}

## Frage
Wie funktioniert NVIDIA's "instruct" principle (kleines model routet, großes model
reasoned nur bei bedarf) und wie können wir es mit entropy-based routing im proxy
nachbauen?

## Recherche-Aufgaben

### 1. Nemotron Architecture verstehen
- [ ] NVIDIA Nemotron-3-Ultra-550B: 55B active parameters (Mixture-of-Experts)
  - Wie funktioniert der routing mechanismus im model selbst?
  - "A55b" = 55B active von 550B total → MoE mit 10:1 sparsity
  - Kann man das pattern auf agent-level anwenden (nicht token-level)?
- [ ] NVIDIA Reasoning Engine:
  - Wie entscheidet die engine ob ein task an das reasoning model geht?
  - Ist es entropy-based oder rule-based?
  - Welche thresholds/parameters?
  - Doku: developer.nvidia.com reasoning engine docs

### 2. Entropy-Based Routing Implementation
- [ ] logprobs API:
  - OpenAI: `logprobs: true` in chat completions → returns top logprobs per token
  - vLLM/NIM: `logprobs: N` parameter
  - Anthropic: supports logprobs? (check API docs)
  - Andere provider: welche unterstützen logprobs?
- [ ] Shannon Entropy berechnen:
  - Formula: H = -sum(p_i * log2(p_i)) über top-k tokens
  - k = 5? 10? Alle tokens?
  - Normalisierung: H / log2(k) → 0..1 range
  - Threshold: 0.5? 0.3? Empirisch testen
- [ ] Implementation im proxy:
  - Request geht zuerst an planner model mit `logprobs: true`
  - Proxy berechnet entropy aus logprobs
  - Wenn entropy < threshold → accept response (fast, cheap)
  - Wenn entropy >= threshold → re-route zu reasoning model
  - Cache: für gleiche requests? (z.B. für 5 minuten)

### 3. Planner Model Selection
- [ ] Kriterien für planner model:
  - Klein (1B-8B) → fast, cheap
  - Supports logprobs → OpenAI/vLLM/NIM
  - Gute classification accuracy → instruction-tuned
- [ ] Kandidaten:
  - `meta/llama-3.1-8b-instruct` (NVIDIA free)
  - `microsoft/phi-3-mini` (small, fast)
  - `google/gemma-2-2b` (sehr klein)
  - `deepseek/deepseek-r1-distill-qwen-1.5b` (reasoning distilled)
- [ ] Planner prompt: "Classify this request: is it coding, reasoning, simple chat,
  or complex multi-step? Rate confidence 0-1."

### 4. Latency Impact
- [ ] Wie viel latency addiert der planner call?
  - Kleines model: ~200-500ms TTFB
  - Ist das akzeptabel für jeden request?
  - Alternative: nur für requests die nicht trivial klassifizierbar sind
- [ ] Streaming: kann der planner parallel zum user streamen?
  - Nein — planner muss zuerst entscheiden, dann wird weitergeroutet
  - Aber: planner kann sehr schnell sein (8B model, max_tokens=10)
- [ ] Caching: häufige request patterns → skip planner

## Output Format
1. Architektur diagram (planner → entropy check → route decision)
2. Entropy formula + implementation pseudocode
3. Planner model empfehlung mit begründung
4. Latency benchmark erwartung
5. Config schema: `entropy_routing: { enabled, threshold, planner_model, cache_ttl }`Das NVIDIA Instruct Principle trennt die rechenintensive "Denkfähigkeit" von der reinen Befehlsverfolgung. Auf Agenten- oder Proxy-Ebene bedeutet das: Ein kleines, ultraschnelles Planner-Modell fängt den Request ab, klassifiziert ihn und kalkuliert seine eigene statistische Unsicherheit via Shannon-Entropie. Nur bei hoher Unsicherheit (hoher Entropie) leitet der Proxy den Request an ein teures, langsames Reasoning-Modell (z. B. DeepSeek-R1 oder o1) weiter. [1] (https://docs.nvidia.com/nim/large-language-models/1.8.0/reasoning-model.html), [2] (https://docs.nvidia.com/nim/large-language-models/1.12.0/reasoning-model.html), [3] (https://inworld.ai/resources/what-is-an-ai-router)1. Architektur-Diagramm                      +-------------------+

                      |   User Request    |
                      +---------+---------+
                                |
                                v
                    +-----------------------+

                    |  JiMesh Proxy Router  |
                    +-----------+-----------+
                                |
             [Call Planner with logprobs: true, max_tokens: 1]
                                |
                                v
                     +---------------------+

                     |    Planner Model    | (z.B. Llama-3.1-8B)
                     +----------+----------+
                                |
               [Extract top-k logprobs for Token #1]
                                |
                                v
                    +-----------------------+

                    | Entropy Calculation   | -> H = -Sum(p_i * log2(p_i))
                    +-----------+-----------+
                                |
                     +----------+----------+

                     | Entropy >= Threshold|
                     +----/-----------\----+
                         /             \
                   [Nein]               [Ja]
                       /                 \
                      v                   v
          +-----------------------+   +-----------------------+

          |  Fast-Track (Direct)  |   |   Escalate Route      |
          |  Serve Planner Res.   |   |   Call Reasoning Model|
          +-----------------------+   +-----------------------+
2. Entropie-Formel & ImplementationDie Shannon-Entropie \(H\) misst die Unberechenbarkeit der Token-Verteilung. Wir ziehen die Wahrscheinlichkeiten \(p_{i}\) aus den logprobs des allerersten Antwort-Tokens des Planners. [1] (https://openreview.net/forum?id=hFxivbAgVP), [2] (https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1892739/full)Formel:\(H=-\sum _{i=1}^{k}p_{i}\log _{2}(p_{i})\)Zur besseren Handhabung im Proxy wird die Entropie über die Anzahl der ausgewerteten Tokens (\(k\)) normalisiert, sodass der Wert exakt zwischen 0.0 (absolute Gewissheit) und 1.0 (maximale Verwirrung/Gleichverteilung) liegt:\(H_{norm}=\frac{H}{\log _{2}(k)}\)Proxy Pseudocode (Node.js / TypeScript):typescriptimport { OpenAI } from 'openai';

interface LogprobItem { token: string; logprob: number; }

function calculateNormalizedEntropy(topLogprobs: LogprobItem[]): number {
  const k = topLogprobs.length;
  if (k <= 1) return 0;

  let entropy = 0;
  for (const item of topLogprobs) {
    const p = Math.exp(item.logprob); // Wandelt Logprob zurück in lineare Wahrscheinlichkeit [0..1]
    if (p > 0) {
      entropy -= p * Math.log2(p);
    }
  }

  const maxEntropy = Math.log2(k);
  return entropy / maxEntropy; // Normalisiert auf die Range 0.0 - 1.0
}

async function routeProxyRequest(userPrompt: string, config: any) {
  // 1. Prüfe Cache, um wiederholte Planner-Calls zu skippen
  const cachedRoute = await cache.get(userPrompt);
  if (cachedRoute) return executeRoute(cachedRoute, userPrompt);

  const openai = new OpenAI({ baseURL: config.entropy_routing.planner_url });

  // 2. Rufe den Planner extrem sparsam auf (nur das Klassifikations-Token generieren)
  const plannerResponse = await openai.chat.completions.create({
    model: config.entropy_routing.planner_model,
    messages: [
      { role: 'system', content: "Classify this request. Output exactly ONE word from this list: [SIMPLE, COMPLEX, CODING, REASONING]." },
      { role: 'user', content: userPrompt }
    ],
    max_tokens: 1,
    logprobs: true,
    top_logprobs: 5 // Entspricht k = 5
  });

  const firstTokenChoice = plannerResponse.choices[0]?.logprobs?.content?.[0];
  if (!firstTokenChoice) return executeRoute('reasoning_model', userPrompt); // Fallback bei API-Fehlern

  // 3. Berechne statistische Unsicherheit
  const normalizedEntropy = calculateNormalizedEntropy(firstTokenChoice.top_logprobs);

  let targetRoute = 'planner_model'; // Standard-Pfad (Günstig & Schnell)
  
  // Wenn Entropie den Schwellenwert reißt, eskaliere zum teuren Reasoning-Modell
  if (normalizedEntropy >= config.entropy_routing.threshold) {
    targetRoute = 'reasoning_model';
  }

  // 4. Cache die Routing-Entscheidung für diesen Pattern-Typ
  await cache.set(userPrompt, targetRoute, config.entropy_routing.cache_ttl);

  return executeRoute(targetRoute, userPrompt);
}
3. Planner Model EmpfehlungEmpfehlung: meta/llama-3.1-8b-instruct (oder alternativ google/gemma-2-2b für extremen Durchsatz).Begründung: Der Planner muss zwei harte Kriterien erfüllen: Er muss native, granulare logprobs über seine API ausgeben (vLLM und NVIDIA NIM unterstützen dies nativ; Anthropic fällt hier komplett weg, da deren API keine Logprobs bereitstellt). Zudem benötigt er eine hohe Classification-Accuracy trotz minimaler Token-Generierung. Llama-3.1-8B besitzt ein hervorragend kalibriertes Logprob-Verhalten, wodurch die mathematische Entropie exakt mit der echten Aufgabenschwierigkeit korreliert. [1] (https://platform.claude.com/docs/en/cli-sdks-libraries/libraries/openai-sdk), [2] (https://developer.nvidia.com/topics/ai/nemotron), [3] (https://medium.com/@GerardSimons/llms-as-classifiers-part-2-d874d20cd3c9)4. Latency Benchmark ErwartungDa wir max_tokens: 1 erzwingen, entfällt die zeitintensive Generierungsphase (Autoregressive Generation) fast vollständig. Die Latenz des Routers setzt sich fast ausschließlich aus der Time-To-First-Token (TTFB) des kleinen Modells zusammen.Trivialer Case (Entropie < Threshold): Der Planner benötigt im lokalen Netz (vLLM/NIM) ca. 45ms – 90ms für den Klassifikations-Zoll. Da er die finale Antwort im selben Zug generieren kann, wenn man das Prompting leicht anpasst, liegt der Overhead bei unter 10 %.Komplexer Case (Entropie >= Threshold): Hier schlägt der Planner-Call voll als Overhead zu Buche (+90ms Latenz-Penalty), bevor der eigentliche, ohnehin langsame Aufruf des Reasoning-Modells (mehrere Sekunden Denkzeit) gestartet wird. Prozentual fällt dieser Overhead bei 5 Sekunden Reasoning-Dauer jedoch kaum ins Gewicht.5. Config SchemaDieses JSON-Schema steuert das Verhalten des Routers in deiner JiMesh-Proxy-Konfiguration:json{
  "entropy_routing": {
    "enabled": true,
    "threshold": 0.45,
    "planner_model": "meta/llama-3.1-8b-instruct",
    "planner_url": "http://localhost:8000/v1",
    "reasoning_model": "deepseek/deepseek-r1",
    "top_k_eval": 5,
    "cache_ttl": 300
  }
}

## Frage
Welches framework für multi-agent orchestration? Custom JiMesh-native oder
etabliertes framework (CrewAI, LangGraph, AutoGen)?

## Recherche-Aufgaben

### 1. CrewAI
- [ ] Architektur: wie definiert man crews, agents, tasks?
- [ ] Role-based: wie werden agent roles mapped?
- [ ] LLM integration: kann man custom OpenAI endpoint (JiMesh) nutzen?
- [ ] Structured output: pydantic models für task results?
- [ ] Process types: sequential, hierarchical, consensual?
- [ ] Python-only? Go alternative?
- [ ] Dependencies: was zieht es ein? (langchain? instructor?)
- [ ] Performance: overhead per agent call?
- [ ] Stars, maintenance, last update
- [ ] Doku: crewai.com/docs

### 2. LangGraph
- [ ] Architektur: graph-based agent workflows (nodes + edges)
- [ ] Conditional routing: wie entscheidet der graph welcher agent als nächstes?
- [ ] State management: wie wird state zwischen nodes geteilt?
- [ ] Integration: OpenAI compatible endpoints?
- [ ] Python-only? Go port?
- [ ] Dependencies: langchain core? wie viel overhead?
- [ ] Streaming: intermediate results streaming?
- [ ] Stars, maintenance, last update
- [ ] Doku: langchain-ai.github.io/langgraph

### 3. AutoGen
- [ ] Architektur: multi-agent conversation framework
- [ ] Group chat: agents diskutieren miteinander?
- [ ] Code execution: kann agent code ausführen?
- [ ] Integration: custom OpenAI endpoint?
- [ ] Python-only?
- [ ] Dependencies, overhead
- [ ] Stars, maintenance, last update
- [ ] Doku: microsoft.github.io/autogen

### 4. Instructor (Structured Output)
- [ ] Wie funktioniert es? (pydantic model → prompt → LLM → validated output)
- [ ] Retry on validation failure?
- [ ] Go alternative? (Go hat kein pydantic, aber `encoding/json` + struct tags)
- [ ] Overhead: wie viele extra tokens für structured output?
- [ ] Kompatibel mit allen frameworks?
- [ ] Doku: instructor-ai.github.io/instructor

### 5. Custom JiMesh-Native Orchestration
- [ ] Keine framework dependencies
- [ ] Direkter mesh route access (keine API abstraction layer)
- [ ] Go-native: goroutines für parallel agent execution
- [ ] Schema: Go structs für task results (statt pydantic)
- [ ] Routing: direkt via sortKeysByQuota + bandit
- [ ] Overhead: minimal (keine framework overhead)
- [ ] Nachteile: müssen features selbst bauen (retry, state mgmt, etc.)

### 6. Vergleichs-Matrix
| Feature | CrewAI | LangGraph | AutoGen | Custom |
|---|---|---|---|---|
| Language | Python | Python | Python | Go |
| Framework deps | heavy | heavy | medium | none |
| Custom LLM endpoint | yes | yes | yes | native |
| Structured output | via instructor | via pydantic | limited | Go structs |
| Parallel agents | sequential only? | yes | yes | goroutines |
| State management | task-based | graph state | conversation | custom |
| Streaming | limited | yes | limited | native SSE |
| Maintenance risk | medium | high (langchain) | medium | low (ours) |
| Learning curve | low | high | medium | low |

### 7. Hybrider Ansatz?
- [ ] Core orchestration in Go (JiMesh-native)
- [ ] Optional CrewAI/LangGraph adapter für Python users
- [ ] Adapter als sidecar service (Python process) der mit JiMesh API spricht
- [ ] Overhead: sidecar adds latency but only when used

## Output Format
1. Vergleichs-Matrix ausgefüllt
2. Empfehlung: Custom core + optional adapter? Oder framework?
3. Falls custom: feature list was wir selbst bauen müssen
4. Falls framework: integrations architektur
5. Go-struktur für orchestration (task, agent, role, route mapping)Hier ist die strategische Architekturbewertung für die Multi-Agenten-Orchestrierung innerhalb deines JiMesh-Ökosystems.1. Vergleichs-MatrixDa JiMesh nativ in Go geschrieben ist, während die etablierten Frameworks schwere Python-Monolithen sind, sieht das Spielfeld bezüglich Performance und Kontrolle wie folgt aus: [1] (https://www.n-ix.com/langgraph-vs-crewai-vs-autogen/)FeatureCrewAILangGraphAutoGen / AG2Custom (JiMesh-Native)LanguagePythonPython & JS/TSPython (AG2) / .NETGo-nativeFramework DepsHeavy (LangChain/Pydantic)Heavy (LangChain Core)Medium (Microsoft SDK)NoneCustom LLM EndpointJa (via OpenAI-Abstraktion)Ja (via LangChain-ChatOpenAI)Ja (via LiteLLM/OpenAI-Client)Native (direkter In-Process Route-Access)Structured OutputNative PydanticPydantic / JsonSchemaEingeschränkt / JSON-ParsingGo Structs (JSON Tags + jsonschema)Parallel AgentsSequentiell / HierarchischJa (Verzweigte Graph-Knoten)Ja (Group Chat Turn-Taking)Ja (Ultraschnelle Goroutines)State ManagementTask-based (linear)Graph State (Reducers / Checkpoints)Konversations-HistorieMemory-State in Go (Channels/Mutex)StreamingEingeschränktJa (Node- & Token-Streaming)EingeschränktNative Server-Sent Events (SSE)Maintenance RiskMedium (kommerzielle Firma)Hoch (LangChain API-Churn)Hoch (Microsoft im Maintenance Mode)Minimal (voller Code-Besitz)Learning CurveNiedrigHoch (Steile Graph-Logik)MediumNiedrig (Standard Go-Web-Architektur)2. Strategische Empfehlung: Der Hybride AnsatzNutze Custom Core in Go (JiMesh-native) + Optionale Python-Adapter.Begründung: Ein fremdes Python-Framework als Kernkomponente in ein hochperformantes Go-System (JiMesh) zu zwingen, bricht deine Performance-Vorteile (Latenz, Memory-Footprint). Python-Frameworks wie CrewAI erzeugen pro Agentenschritt massiven Overhead. [1] (https://gurusup.com/blog/best-multi-agent-frameworks-2026), [2] (https://www.n-ix.com/langgraph-vs-crewai-vs-autogen/)Der Core (Go): Übernimmt die latenzkritische und parallele Ausführung von Agenten-Pipelines mithilfe von Goroutines, verwaltet den State und streamt Event-Daten live über SSE an dein R1-Dashboard.Der Python-Adapter (Sidecar): Falls Entwickler explizit bestehende Python CrewAI-Crews oder LangGraph-Graphen nutzen wollen, stellt JiMesh einen leichtgewichtigen API-Endpunkt bereit. Das Framework läuft autark in einem isolierten Python-Prozess (Sidecar) und kommuniziert mit JiMesh als OpenAI-kompatiblem Provider. [1] (https://gurusup.com/blog/best-multi-agent-frameworks-2026)3. Feature-Liste für JiMesh-Native Orchestration (Go)Da du das Rad nicht komplett neu erfinden musst, konzentriert sich die Implementierung auf diese Kern-Features:JSON-Schema Generierung: Nutze Bibliotheken wie invopop/jsonschema, um aus nativen Go-Structs zur Laufzeit JSON-Schemas zu erzeugen, die an das LLM via response_format: { type: "json_object", schema: ... } (Structured Outputs) übergeben werden.Retry- & Validierungs-Schleife: Ein Interceptor, der die LLM-Antwort gegen das Go-Struct unmarshalt. Schlägt dies fehl, wird ein automatischer Self-Correction Prompt (inkl. Fehlermeldung) für maximal 3 Versuche an das LLM zurückgesendet.State Management (Context-Passing): Ein thread-sicheres Context-Objekt (sync.Map oder geschützte Structs), das sequentiell oder parallel von Agent-Knoten manipuliert und ausgelesen werden kann.Token- & Event-Broker: Ein zentraler Go-Channel, in den jeder Agent seinen Status (agent:started, agent:thinking, token:generated, agent:completed) pusht, um das Frontend per SSE-Stream in Echtzeit zu füttern.4. Integrations-Architektur für Python-FrameworksWenn ein User ein Python-Framework (z.B. CrewAI) nutzen möchte, agiert JiMesh rein als intelligenter, lokaler Proxy.+------------------------------------------------------------+

|                       JiMesh Pod                           |
|                                                            |
|  +------------------------+      +----------------------+  |
|  | Python Sidecar Process |      |  JiMesh Go Core      |  |
|  |                        |      |                      |  |
|  |  [ CrewAI / LangGraph ]|      |  [ Router / Proxy ]  |  |
|  |           |            |      |          |           |  |
|  +-----------|------------+      +----------|-----------+  |
|              |                              |              |
|              | (HTTP OpenAI-API Protocol)   |              |
|              +----------------------------->|              |
|                baseURL: "localhost:9091"    |              |
|                apiKey:  "jm_live_..."       |              |
+---------------------------------------------|--------------+
                                              v
                                   [ Local Models / Fallbacks ]
5. Go-Datenstrukturen für die OrchestrierungDieses Typsystem bildet das Fundament für deinen JiMesh-nativen Workflow-Manager:gopackage orchestration

import (
	"context"
	"encoding/json"
	"time"
)

// AgentRole definiert die System-Instruktion und Meta-Daten des Agenten
type AgentRole struct {
	Name         string   `json:"name"`
	Role         string   `json:"role"`         // z.B. "Code Auditor"
	Backstory    string   `json:"backstory"`    // System-Prompt Ergänzung
	AllowedTools []string `json:"allowed_tools"` // IDs registrierter Werkzeuge
}

// RouteMapping verknüpft den Agenten mit den Routing-Sperren und Quotas aus dem Proxy
type RouteMapping struct {
	TargetModel  string        `json:"target_model"`  // Virtuelle ID aus /v1/models
	EntropyRoute bool          `json:"entropy_route"` // Nutzt den R4-Entropy Check
	Timeout      time.Duration `json:"timeout"`
	MaxQuotaCost float64       `json:"max_quota_cost"`
}

// Task repräsentiert eine atomare Ausführungseinheit innerhalb des Graphen
type Task struct {
	ID           string       `json:"id"`
	Description  string       `json:"description"`
	AssignedRole AgentRole    `json:"assigned_role"`
	Routing      RouteMapping `json:"routing"`
	Dependencies []string     `json:"dependencies"` // IDs von Tasks, die vorher fertig sein müssen
	OutputFormat interface{}  `json:"-"`            // Pointer zu einem Go-Struct für Structured Output
}

// TaskResult hält das Ergebnis inklusive Telemetriedaten
type TaskResult struct {
	TaskID    string          `json:"task_id"`
	Status    string          `json:"status"` // "success", "failed", "retrying"
	RawOutput json.RawMessage `json:"raw_output"`
	Tokens    int             `json:"tokens_used"`
	Duration  time.Duration   `json:"duration"`
	Error     string          `json:"error,omitempty"`
}

// WorkflowState orchestriert die parallele Ausführung über den State hinweg
type WorkflowState struct {
	ID        string                `json:"workflow_id"`
	Context   context.Context       `json:"-"`
	Data      map[string]interface{} `json:"data"` // Shared State (Thread-safe kapseln!)
	Results   map[string]TaskResult `json:"results"`
	EventChan chan string           `json:"-"`     // Broadcast Channel für Live SSE-Streaming
}

## Frage
Wie bauen wir ein Model-of-Experts pattern für agents? Mehrere spezialisierte agents
mit verschiedenen modellen, intelligent routing zwischen ihnen?

## Recherche-Aufgaben

### 1. Agent-Level MoE verstehen
- [ ] Token-level MoE (im model) vs Agent-level MoE (between models) — unterschied?
- [ ] "Mixture of Experts" für agents:
  - N spezialisierte agents (coder, reviewer, planner, researcher)
  - Gating agent (small model) wählt expert(s)
  - Parallel (voting) oder sequential (chain)
- [ ] Existing research:
  - "Mixture of Agents" paper (arxiv 2406.04692)?
  - "MoA: Mixture of Agentic LLMs"?
  - Wie unterscheidet sich das von unserem mesh routing?

### 2. Gating Agent Design
- [ ] Input: task description + liste der verfügbaren experts
- [ ] Output: `{ selected: [expert_ids], mode: "parallel"|"sequential", confidence: float }`
- [ ] Prompt design: "Given these experts [list], which should handle this task?"
- [ ] Model choice: kleinste/ billigste model das gut genug klassifiziert
- [ ] Fallback: wenn gating unsicher → alle experts parallel, aggregate

### 3. Expert Agent Definition
- [ ] Expert schema:
  ```json
  {
    "id": "coder-nvidia",
    "name": "Coding Expert (NVIDIA Nemotron)",
    "route": "smart:coding-free",
    "systemPrompt": "You are a coding expert...",
    "tools": ["code_search", "file_write"],
    "type": "coder"
  }
  ```
- [ ] Expert types: coder, reviewer, planner, researcher, executor, general
- [ ] Kann ein expert mehrere mesh routes nutzen? (failover within expert)
- [ ] Tools: sollen experts tools haben? (function calling)

### 4. Execution Modes
- [ ] **Parallel mode**: alle selected experts gleichzeitig → aggregate
  - Aggregation: LLM-based synthesis oder majority vote oder concat
- [ ] **Sequential mode**: expert chain, jeder bekommt output des vorherigen
  - Chain depth limit (max 3-5?)
  - Intermediate results visible to user
- [ ] **Hybrid mode**: parallel für research, sequential für code→review
- [ ] Error handling: expert failure → skip + log? → retry? → use backup expert?

### 5. Result Aggregation
- [ ] Simple concat (alle expert outputs nacheinander)
- [ ] LLM synthesis (extra model aggregiert results → final answer)
- [ ] Majority vote (für factual questions)
- [ ] Best-of-N (ranking model wählt besten output)
- [ ] Cost: aggregation model braucht extra tokens → welcher model?

### 6. DB Schema
- [ ] `experts` table: id, name, route_id, system_prompt, tools json, type, enabled
- [ ] `expert_runs` table: run_id, task, gating_result json, expert_results json, final_output
- [ ] `expert_configs` table: default gating model, thresholds, aggregation mode

### 7. DSH Plugin Integration
- [ ] Plugin zeigt expert cards (wie model sidebar)
- [ ] User wählt task → gating agent select experts → execute
- [ ] Real-time progress: welcher expert läuft, partial results
- [ ] Cancel button: stop all experts mid-execution
- [ ] Results panel: aggregated output + per-expert attribution

## Output Format
1. Architektur diagram: gating agent → experts → aggregation
2. Expert schema (Go struct + JSON)
3. Execution mode empfehlung (wann parallel, wann sequential)
4. Aggregation strategy empfehlung
5. DB migration schema
6. DSH plugin mockup (text description)Das Agent-Level MoE (Mixture of Experts) transferiert das Token-Sparsity-Prinzip großer LLM-Modelle (wie Nemotron oder DeepSeek V3/V4) auf die Anwendungsebene. Statt Token für Token im neuronalen Netz zu routen, steuert ein Gating-Agent (Orchestrator) auf Task-Ebene, welche spezialisierten Agenten-Instanzen mit welchen zugrundeliegenden Mesh-Modellen aktiviert werden. Das bricht die "Jack-of-all-trades"-Limitation einzelner LLMs auf. [1] (https://gurusup.com/blog/moe-vs-multi-agent-systems), [2] (https://medium.com/@sharanharsoor/understanding-mixture-of-experts-moe-the-architecture-powering-next-generation-language-models-49c1d1d467c9), [3] (https://www.mindstudio.ai/blog/multi-agent-orchestration-patterns), [4] (https://a-nikishaev.medium.com/mixture-of-agents-moa-improving-llm-quality-through-multi-agent-collaboration-eb0bcbbdbe9f)Das Design baut auf dem bahnbrechenden Mixture-of-Agents (MoA) Ansatz (arXiv:2406.04692) von Together AI auf, verfeinert diesen jedoch um agentische Werkzeugnutzung (Tools) und flexible Ausführungsmodi. [1] (https://arxiv.org/abs/2406.04692), [2] (https://docs.together.ai/docs/mixture-of-agents)1. Architektur-Diagramm                           +--------------------+

                           |    User Input      |
                           +---------+----------+
                                     |
                                     v
                        +--------------------------+

                        |  Gating Agent (Router)   | -> (Llama-3.1-8B for strict JSON)
                        +------------+-------------+
                                     |
              +----------------------+----------------------+

              | [Sequential Mode]                           | [Parallel Mode]
              v                                             v
   +--------------------+                       +-----------------------+

   | Phase 1: Planner   |                       | Expert A: Coder       | -> (Nemotron-3)
   +---------+----------+                       +-----------+-----------+

             | (Output Context)                             |
             v                                              | (Raw Res.)
   +--------------------+                                   v

   | Phase 2: Coder     |                       +-----------------------+
   +---------+----------+                       | Expert B: Reviewer    | -> (DeepSeek-R1)
             | (Output Context)                     +-----------+-----------+
             v                                              |
   +--------------------+                                   | (Raw Res.)

   | Phase 3: Reviewer  |                                   v
   +---------+----------+                       +-----------------------+

             |                                  | Expert C: Researcher  | -> (Phi-3-Mini)
             |                                  +-----------+-----------+

             |                                              |
             +----------------------+-----------------------+
                                    |
                                    v
                       +--------------------------+

                       |    Aggregation Layer     | -> (LLM-based Synthesis or Vote)
                       +------------+-------------+
                                    |
                                    v
                       +--------------------------+

                       |   Final Clean Output     |
                       +--------------------------+
2. Expert Schema (Go-Strukturen)Dieses Datenschema verankert die Experten-Instanzen nativ im JiMesh Core.gopackage moe

import (
	"encoding/json"
	"time"
)

// ExpertType definiert den funktionalen Schwerpunkt des Agenten
type ExpertType string

const (
	Coder      ExpertType = "coder"
	Reviewer   ExpertType = "reviewer"
	Planner    ExpertType = "planner"
	Researcher ExpertType = "researcher"
	General    ExpertType = "general"
)

// ExpertAgent definiert die Konfiguration und Fähigkeiten eines Spezialisten
type ExpertAgent struct {
	ID           string          `json:"id"`
	Name         string          `json:"name"`
	Type         ExpertType      `json:"type"`
	MeshRouteID  string          `json:"route_id"`      // Verknüpfung zur JiMesh-Routingklasse (z.B. "smart:coding")
	SystemPrompt string          `json:"system_prompt"` // Rollen-Spezialisierung
	Tools        []string        `json:"tools"`         // Erlaubte CLI/API Werkzeug-IDs
	Enabled      bool            `json:"enabled"`
	CreatedAt    time.Time       `json:"created_at"`
}

// GatingResult hält die Routing-Entscheidung des Gating-Agenten fest
type GatingResult struct {
	SelectedExperts []string `json:"selected_experts"` // IDs der gewählten Experten
	ExecutionMode   string   `json:"mode"`             // "parallel", "sequential", "hybrid"
	Confidence      float64  `json:"confidence"`       // Wert zwischen 0.0 und 1.0
	Reasoning       string   `json:"reasoning"`        // Interne Begründung des Routers
}
3. Empfehlungen für die Ausführungsmodi (Execution Modes)Wann welcher Modus getriggert wird, entscheidet der Gating-Agent anhand der Task-Komplexität:Parallel Mode (Das MoA-Prinzip):Szenario: Kreatives Schreiben, komplexe Fragen, Brainstorming, Code-Generierung ohne explizites Testframework.Mechanismus: Mehrere Experten (z. B. 3 verschiedene Allround-Modelle) generieren gleichzeitig Entwürfe. Das Aggregationsmodell extrahiert die stärksten Argumente/Lösungswege. [1] (https://openreview.net/forum?id=h0ZfDIrj7T), [2] (https://arxiv.org/abs/2406.04692), [3] (https://docs.together.ai/docs/mixture-of-agents), [4] (https://www.youtube.com/watch?v=4_iKxitIK90&t=302)Sequential Mode (Das Fließband-Prinzip):Szenario: Testgetriebene Entwicklung (TDD), Refactoring, sicherheitskritische Code-Audits.Mechanismus: Die Kette arbeitet strikt linear (z. B. Planner -> Coder -> Reviewer). Jeder Agent erhält den vollen Kontext und die Outputs aller vorangegangenen Instanzen.Limit: Die maximale Tiefe wird hart auf 4 Schritte gecappt, um Latenz-Explosionen vorzubeugen. [1] (https://arxiv.org/abs/2406.04692), [2] (https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns), [3] (https://www.mindstudio.ai/blog/multi-agent-orchestration-patterns)4. Aggregations-Strategie (Result Aggregation)Empfehlung: LLM Synthesis (via kostengünstigem, instruktionstuned Allrounder wie Llama-3.1-8B).Begründung: Ein einfaches Aneinanderhängen (Concat) erzeugt repetitive Textblöcke und inhärente Widersprüche. Ein Majority Vote funktioniert nur bei deterministischen Single-Token-Fragen (z. B. Klassifizierungen). Für freie Text- und Codeaufgaben ist ein Synthese-Prompt die SOTA-Lösung (siehe Together MoA Paper). Der Aggregator erhält die Original-User-Frage sowie alle Experten-Antworten sauber getaggt und formatiert daraus eine finale, konsistente Antwort. [1] (https://arxiv.org/abs/2406.04692), [2] (https://docs.together.ai/docs/mixture-of-agents), [3] (https://www.alphaxiv.org/abs/2406.04692)5. Datenbank-Migrationsschema (PostgreSQL)sql-- Tabelle für die registrierten Experten-Agenten
CREATE TABLE experts (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(32) NOT NULL,
    route_id VARCHAR(64) NOT NULL,
    system_prompt TEXT NOT NULL,
    tools JSONB DEFAULT '[]'::jsonb,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle für die Protokollierung und das Auditing der Läufe
CREATE TABLE expert_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_description TEXT NOT NULL,
    gating_result JSONB NOT NULL, -- Beinhaltet gewählte IDs, Modus, Confidence
    expert_outputs JSONB NOT NULL, -- JSON-Array mit Raw-Outputs und Metriken je Agent
    final_output TEXT NOT NULL,
    tokens_used INT NOT NULL,
    duration_ms INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initial-Seed für Standard-Experten
INSERT INTO experts (id, name, type, route_id, system_prompt, tools) VALUES
('coder-nemotron', 'NVIDIA Coding Specialist', 'coder', 'smart:coding-free', 'You are an elite software engineer. Output clean, optimal code.', '["file_write"]'),
('reviewer-r1', 'DeepSeek Critic', 'reviewer', 'reasoning:deepseek-r1', 'You are a critical code auditor. Find bugs, edge cases, and security leaks.', '[]'),
('researcher-phi', 'Fast Researcher', 'researcher', 'fast:inline-completion', 'Extract raw facts and document endpoints efficiently.', '["code_search"]');
6. DSH Plugin Mockup (UI/UX Text-Spezifikation)Das DeepSeek Harness (DSH) Plugin spiegelt den Fortschritt des MoE-Laufs visuell wider, um maximale Observability zu garantieren. [1] (https://gurusup.com/blog/moe-vs-multi-agent-systems)+-----------------------------------------------------------------------------------+

| 🤖 MIXTURE-OF-EXPERTS AGENT ROUTER                                                |
+-----------------------------------------------------------------------------------+

| Prompt: [ Schreibe einen optimierten Go-Webserver mit Rate-Limiting...          ] |
|                                                                     [ RUN TASK ]  |
+-----------------------------------------------------------------------------------+

| ⚡ GATING ANALYSIS (Completed in 85ms)                                            |
| Selected Experts: [coder-nemotron, reviewer-r1] | Mode: SEQUENTIAL | Conf: 94%   |
| Reasoning: Task requires complex implementation followed by strict security audit.|
+-----------------------------------------------------------------------------------+

| 🕒 ORCHESTRATION PIPELINE PROGRESS                                                |
|                                                                                   |
|  [✓] 1. Gating Router  ========================================> (85ms)          |
|  [✓] 2. Expert: NVIDIA Coding Specialist [smart:coding-free] ===> (1200ms)        |
|      └─> [Partial Output: package main; import "net/http"... ]                   |
|  [▶] 3. Expert: DeepSeek Critic [reasoning:deepseek-r1] =======> (Thinking... 4s)  |
|      └─> [Thinking Stream: Checking memory bounds, evaluating mutex locks...]     |
|  [ ] 4. Final Aggregator Layer ================================> (Pending)       |
|                                                                                   |
|                                                                  [ CANCEL ALL ]   |
+-----------------------------------------------------------------------------------+

| 📋 FINAL AGGREGATED OUTPUT                                                        |
| +-------------------------------------------------------------------------------+ |
| | Here is the production-grade Go webserver with secure token bucket rate      | |
| | limiting. Bugfixes applied from security audit (fixed race condition in map). | |
| | [Code Block: package main ...]                                                | |
| +-------------------------------------------------------------------------------+ |
| Attribution: 70% Coder-Nemotron (Architecture) | 30% Reviewer-R1 (Thread-Safety)  |
+-----------------------------------------------------------------------------------+

## Frage
Wie bauen wir ein DSH (DeepSeek Harness) plugin das JiMesh mesh routes für agent
roles nutzt? Wie sieht die plugin architektur aus?

## Recherche-Aufgaben

### 1. DSH Plugin System verstehen
- [ ] Wie funktioniert das DSH plugin system?
  - Wo liegen plugins? Wie werden sie geladen?
  - Plugin API: welche hooks/events gibt es?
  - Client plugins (frontend) vs server plugins (backend)?
  - Wie registriert ein plugin neue modes/views?
- [ ] DSH source code: `/usr/local/lib/node_modules/@deepseek-ai/dsh/`
  - Plugin loader code lesen
  - Beispiel plugins finden
  - Extension points identifizieren
- [ ] Kann ein plugin neue API endpoints hinzufügen?
- [ ] Kann ein plugin neue sidebar items / tabs hinzufügen?
- [ ] Kann ein plugin den model selection flow abfangen?

### 2. Orchestration Mode Design
- [ ] Was ist ein "mode" in DSH?
  - Chat mode, plan mode, code mode — wie sind die definiert?
  - Kann ein plugin einen neuen mode "orchestration" hinzufügen?
  - Mode switching: wie funktioniert das?
- [ ] Orchestration mode UI:
  - Task input field
  - "Run" button → sends to `/api/orchestrate`
  - Plan display: welche experts/models für welche sub-tasks
  - Execution progress: live SSE updates
  - Results panel: aggregated + per-expert attribution
  - History: previous orchestration runs

### 3. Mesh Route Integration
- [ ] Wie liest das plugin die mesh routes?
  - `GET /api/chains` → liste aller chains
  - `GET /api/chains/{id}/graph` → nodes + members
  - Plugin cached routes oder fresh fetch?
- [ ] Route selection im plugin:
  - User kann route per dropdown wählen
  - Oder: orchestration mode auto-selects basierend auf task type
  - Rolle → route mapping: planner→fast pool, coder→coding pool, etc.
- [ ] Auth: wie authentifiziert sich DSH gegen JiMesh?
  - Deploy token? API key? Session cookie?
  - Brauchen wir einen neuen auth mechanism für plugins?

### 4. Orchestration API
- [ ] `POST /api/orchestrate` — das plugin ruft diesen endpoint
  - Input: `{ task, mode: "auto"|"manual", routes?: { planner?, coder?, reviewer? } }`
  - Output (SSE stream):
    ```
    event: plan
    data: { "classification": "coding", "sub_tasks": [...], "routes": {...} }
    
    event: expert_start
    data: { "expert": "coder-nvidia", "route": "smart:coding-free" }
    
    event: expert_output
    data: { "expert": "coder-nvidia", "chunk": "..." }
    
    event: expert_done
    data: { "expert": "coder-nvidia", "tokens": 500, "latency_ms": 3200 }
    
    event: complete
    data: { "final_output": "...", "experts_used": [...], "total_tokens": 1200 }
    ```
- [ ] Cancel: `POST /api/orchestrate/cancel` → stop all running experts
- [ ] History: `GET /api/orchestrate/history` → past runs

### 5. Plugin Packaging
- [ ] Plugin als npm package? Git submodule? Inline code?
- [ ] Dependencies: darf das plugin JiMesh API client nutzen?
- [ ] Build: muss das plugin mit DSH gebaut werden oder zur laufzeit geladen?
- [ ] Config: plugin settings (JiMesh URL, token, default routes)

### 6. Security & Isolation
- [ ] Plugin läuft in DSH context — hat es access zum filesystem?
- [ ] Brauchen wir sandbox für plugin code execution?
- [ ] Rate limiting: orchestration kann viele LLM calls auslösen — limit?
- [ ] Cost tracking: pro orchestration run → total tokens × cost

## Output Format
1. DSH plugin architecture diagram
2. Plugin file structure (tree)
3. Orchestration API spec (request/response schema)
4. SSE event schema
5. Plugin config schema
6. Auth mechanism empfehlung
7. Build/load mechanismHier ist die vollständige Systemarchitektur und Implementierungsspezifikation für das DSH (DeepSeek Harness) Orchestration Mode Plugin, das deine JiMesh Mesh Routes nativ in den Agenten-Workflow einbindet.1. DSH Plugin-ArchitekturdiagrammDas DSH-Plugin-System nutzt eine Hybrid-Architektur. Der Client-Teil injiziert sich in die React/Vue-App von DSH (Frontend-Hooks), während der Server-Teil Express/Fastify-Routen im DSH-Node-Core registriert, um als Proxy zum Go-basierten JiMesh-Core zu agieren.+-----------------------------------------------------------------------------+

|                            DSH SYSTEM CONTEXT                               |
|                                                                             |
|  +---------------------------+              +----------------------------+  |
|  |     DSH Client UI         |              |       DSH Node Core        |  |
|  |                           |              |                            |  |
|  |  +---------------------+  |              |  +----------------------+  |  |
|  |  | Orchestration View  |  |              |  | Plugin Server Router |  |  |
|  |  +----------+----------+  |              |  +----------+-----------+  |  |
|  |             |             |              |             |              |  |
|  +-------------|-------------+              +-------------|--------------+  |
|                |                                          |                 |
|                | (SSE: /api/orchestrate)                  |                 |
|                +------------------------------------------+                 |
|                                                           |                 |
|                                                           | (Internal Proxy)|
|                                                           v                 |
+-----------------------------------------------------------|-----------------+
                                                            |
                                      (HTTP/gRPC TLS Key)   |
                                                            v
                                              +----------------------------+

                                              |       JiMesh Go Core       |
                                              |                            |
                                              |  [ Orchestrator / Engine ] |
                                              +----------------------------+
2. Plugin Dateistruktur (Tree)DSH lädt Plugins dynamisch zur Laufzeit aus dem Verzeichnis /usr/local/lib/node_modules/@deepseek-ai/dsh/plugins/ (oder einem konfigurierten Custom-Pfad).textdsh-plugin-jimesh-orchestration/
├── package.json
├── tsconfig.json
├── vite.config.ts          # Bundelt das Frontend-Asset als ESM-Modul
├── config.schema.json      # Deklarative Konfigurationsvorgaben für DSH
├── src/
│   ├── index.ts            # Server-Entrypoint (registriert API & Hooks)
│   ├── client/
│   │   ├── index.tsx       # Frontend-Entrypoint (registriert Custom UI-Mode)
│   │   ├── components/
│   │   │   ├── OrchestrationPanel.tsx
│   │   │   └── RouteDropdown.tsx
│   │   └── hooks/
│   │       └── useOrchestrationStream.ts
│   └── server/
│       ├── controllers/
│       │   └── orchestrateController.ts
│       └── services/
│           └── jimeshClient.ts
3. Orchestration API-Spezifikation (/api/orchestrate)Request Schema (POST /api/orchestrate)json{
  "$schema": "http://json-schema.org",
  "type": "object",
  "properties": {
    "task": { "type": "string", "minLength": 1 },
    "mode": { "type": "string", "enum": ["auto", "manual"] },
    "routes": {
      "type": "object",
      "properties": {
        "planner": { "type": "string" },
        "coder": { "type": "string" },
        "reviewer": { "type": "string" }
      },
      "required": ["planner", "coder", "reviewer"]
    }
  },
  "required": ["task", "mode"]
}
Response / Cancel HTTP Status CodesPOST /api/orchestrate -> 200 OK mit Header Content-Type: text/event-stream (Initiiert SSE).POST /api/orchestrate/cancel -> 202 Accepted { "status": "canceling", "active_run_id": "uuid" } (Sendet Abbruchsignal an JiMesh).4. SSE (Server-Sent Events) SchemaDer Stream versorgt das DSH Frontend in Echtzeit mit Fortschrittsdaten:developmentevent: plan
data: { "run_id": "a9b8c7-...", "classification": "coding", "sub_tasks": ["write_server", "audit_code"], "routes": { "coder": "smart:coding-free", "reviewer": "reasoning:deepseek-r1" } }

event: expert_start
data: { "expert": "coder-nemotron", "route": "smart:coding-free", "timestamp": 1717545601 }

event: expert_output
data: { "expert": "coder-nemotron", "chunk": "package main\n\nimport (\n\t\"net/http\"\n)" }

event: expert_done
data: { "expert": "coder-nemotron", "tokens": 420, "latency_ms": 1850 }

event: complete
data: { "final_output": "...", "experts_used": ["coder-nemotron", "reviewer-r1"], "total_tokens": 1150, "total_cost_usd": 0.0023 }
5. Plugin-Konfigurationsschema (config.schema.json)Dieses Schema wird vom DSH-Admin-Dashboard geparst, um die Plugin-Instanz zu initialisieren.json{
  "type": "object",
  "properties": {
    "jimesh_url": {
      "type": "string",
      "format": "uri",
      "default": "http://localhost:9091"
    },
    "jimesh_api_key": {
      "type": "string",
      "description": "Secure mTLS proxy token or Bearer secret"
    },
    "default_routes": {
      "type": "object",
      "properties": {
        "planner": { "type": "string", "default": "fast:inline-completion" },
        "coder": { "type": "string", "default": "smart:coding-free" },
        "reviewer": { "type": "string", "default": "reasoning:deepseek-r1" }
      }
    },
    "enforce_sandbox": { "type": "boolean", "default": true },
    "max_cost_limit_per_run": { "type": "number", "default": 0.50 }
  },
  "required": ["jimesh_url", "jimesh_api_key"]
}
6. Empfohlener AuthentifizierungsmechanismusNutze einen dedizierten, kryptografisch sicheren Pre-Shared Bearer Key (JiMesh Deploy Token) in Kombination mit einer erzwungenen TLS-Validierung zwischen DSH und JiMesh.Vorgehen:Im JiMesh Core wird ein Token mit eingeschränkten ACL-Rechten generiert (token_scope: ["orchestrate", "chains:read"]).Das DSH-Plugin speichert dieses Token verschlüsselt in den DSH-System-Settings ab.Jeder API-Aufruf des Plugins injiziert den Header Authorization: Bearer jm_live_tkn_.... Da das Plugin im DSH-Node-Backend läuft, bleibt das Token vor Endbenutzern im Browser vollständig verborgen (kein Leak über Client-Side Network-Inspectors).7. Build- und Lade-Mechanismus (Build & Load)Kompilierung: Das Plugin wird als eigenständiges Projekt via Vite + esbuild vorkompiliert. Das Frontend wird in ein einzelnes, hochoptimiertes ESM-Modul (client.js) kompiliert, das serverseitige Backend in ein Node-kompatibles CJS/ESM-Modul (index.js).Manifest-Registrierung: DSH scannt beim Start sein Plugin-Verzeichnis. Über eine standardisierte Export-Struktur meldet sich das Plugin beim Core an:typescript// server entrypoint index.ts
export const registerPlugin = (dshCore: any) => {
  // Registriere API Routen
  dshCore.router.post('/api/orchestrate', handleOrchestration);

  // Registriere UI Assets
  dshCore.ui.registerMode({
    id: 'orchestration',
    name: 'Mesh Orchestration',
    icon: 'WorkflowIcon',
    clientAssetPath: './client.js' // Wird asynchron ins DSH-Frontend geladen
  });
};

## Frage
Welche advanced model features (speculative decoding, logprobs, reasoning) können
wir im proxy unterstützen und wie?

## Recherche-Aufgaben

### 1. Speculative Decoding
- [ ] Wie funktioniert es?
  - Small "draft" model generiert N tokens
  - Large "verify" model verifiziert in einem forward pass
  - Akzeptierte tokens → output, rejected → fallback
  - Beschleunigung: 2-3x bei guter acceptance rate
- [ ] vLLM/NIM support:
  - `--speculative-model <model_name>` flag
  - `--num-speculative-tokens N`
  - Welche draft models funktionieren gut?
  - Self-hosted NIM only? Cloud API?
- [ ] Proxy implications:
  - Speculative decoding ist server-side → proxy braucht nichts extra
  - Aber: proxy sollte es für self-hosted NIM deployments konfigurieren können
  - Deployment config: `speculative_model`, `num_speculative_tokens`

### 2. Logprobs
- [ ] Welche providers unterstützen logprobs?
  - OpenAI: `logprobs: true, top_logprobs: N`
  - vLLM/NIM: `logprobs: N` in chat completions
  - Anthropic: ? (check API)
  - Google Gemini: ? 
  - Groq: ? (they use vLLM → probably yes)
  - OpenRouter: passthrough → depends on upstream
- [ ] Proxy implementation:
  - Inject `logprobs: true` in request (like stream_options.include_usage)
  - Parse logprobs from response
  - Compute entropy: Shannon entropy over top-k token probabilities
  - Store in request_log: `entropy float64` column

### 3. Reasoning Models (o1, DeepSeek-R1, Nemotron)
- [ ] Wie funktionieren reasoning models anders?
  - Internal chain-of-thought (hidden tokens)
  - Latency: höher aber bessere quality
  - API: `reasoning_effort` parameter (OpenAI o1)?
  - Token usage: reasoning tokens zählen separat?
- [ ] Proxy support:
  - `reasoning_effort` als routing signal?
  - Low effort → cheap model, high effort → reasoning model?
  - Cost tracking: reasoning tokens extra kosten?
- [ ] NVIDIA Nemotron reasoning:
  - Wie aktiviert man reasoning mode?
  - Separate model ID? API parameter?
  - Doku: developer.nvidia.com nemotron reasoning

### 4. Entropy als Routing Signal
- [ ] Können wir entropy AUS der ersten response berechnen und
  dann entscheiden ob wir nochmal mit einem besseren model probieren?
  - "Self-correction": kleines model antwortet → entropy hoch → großes model übernimmt
  - Implementierung: zwei-phase request
    1. Phase 1: small model mit logprobs → response + entropy
    2. Wenn entropy < threshold → return response
    3. Wenn entropy >= threshold → re-route zu reasoning model
  - Latency: phase 1 dauert ~200-500ms (small model), phase 2 nur bei bedarf
- [ ] Alternative: "confidence score" statt entropy
  - Manche models geben confidence scores? (nicht standard)
  - logprobs ist standardisierter ansatz

### 5. Token-Level Cost Optimization
- [ ] Prompt caching (OpenAI, Anthropic): cached prefix → weniger tokens
  - Proxy: kann er prompt caching headers weiterleiten?
  - OpenAI: automatic? Anthropic: `cache_control` parameter?
- [ ] Token counting: wie genau sind die token counts?
  - Streaming: wir haben jetzt stream_options.include_usage → exakt
  - Non-streaming: usage object in response → exakt
  - Logprobs tokens: zählen die als input oder output tokens?

### 6. Provider-Spezifische Features
- [ ] NVIDIA NIM: `/v1/metrics` Prometheus → können wir das für routing nutzen?
  - `vllm:time_to_first_token_seconds`
  - `vllm:request_success_total`
  - `vllm:request_latency_seconds`
  - Diese sind für self-hosted NIM → cloud API 404
- [ ] Groq: ultra-low latency → immer preferezieren für einfache tasks?
- [ ] Cerebras: noch schneller? Verfügbar?

## Output Format
1. Speculative decoding: deployment config schema
2. Logprobs support matrix (welche providers ja/nein)
3. Entropy routing implementation plan (two-phase request)
4. Reasoning model support: parameter, routing signal, cost tracking
5. Provider feature matrix (was unterstützt welcher provider)Hier ist die systematische Auswertung und der Implementierungsplan für die Integration von Speculative Decoding, Logprobs und fortgeschrittenen Routing-Mechanismen in deinen JiMesh-Proxy.1. Speculative Decoding: Deployment-KonfigurationsschemaDa Speculative Decoding rein serverseitig in der Inferenz-Engine (vLLM / NVIDIA NIM) läuft, konfiguriert der JiMesh-Proxy dies deklarativ im Deployment-Manifest der Container. Das Go-Backend übersetzt dieses Schema direkt in die CLI-Flags des Container-Starts.json{
  "$schema": "http://json-schema.org",
  "type": "object",
  "properties": {
    "speculative_decoding": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean", "default": false },
        "draft_model": { 
          "type": "string", 
          "description": "Kleines Model (z.B. gemma-2-2b für ein Llama-3.1-70B Target)"
        },
        "num_speculative_tokens": { "type": "integer", "default": 5, "minimum": 1, "maximum": 10 }
      },
      "required": ["enabled"]
    }
  }
}
Tipp für die Praxis: Draft- und Target-Model müssen den gleichen Tokenizer nutzen (z. B. Llama-3.1-8B als Draft für Llama-3.1-70B), da der Forward-Pass sonst fehlschlägt.2. Logprobs Support MatrixDer Proxy benötigt native Logprobs, um die Shannon-Entropie mathematisch präzise zu ermitteln.Provider / EngineLogprobs SupportAPI-ParameterZuverlässigkeit / EinschränkungenvLLM (Self-Hosted)Jalogprobs: NExtrem zuverlässig. Gibt top-N Tokens pro Position aus.NVIDIA NIM (Self-Hosted)Jalogprobs: NBasiert intern auf vLLM/TensorRT-LLM. Perfekt integriert.OpenAI CloudJalogprobs: true, top_logprobs: NStandardisiert, aber auf max. 20 Tokens limitiert.Groq CloudJalogprobs: trueNutzt modifizierte vLLM-Backends; verhält sich wie OpenAI.OpenRouterBedingtAbhängig von UpstreamReicht Parameter durch. Bei DeepSeek/Meta-Modellen meist stabil.Google GeminiNein—Native API bietet aktuell keine standardisierten Logprobs für Chats.Anthropic ClaudeNein—Harter Blocker. Anthropic verweigert aus Sicherheitsgründen Logprobs.3. Entropy Routing: Two-Phase Request (Selbstkorrektur)Im Gegensatz zum R4-Ansatz (wo der Planner nur 1 Token zur reinen Klassifizierung generiert) erzeugt der Two-Phase Self-Correction Ansatz die vollständige Antwort des kleinen Modells und eskaliert nur bei schlechter Token-Qualität.[User Request] 
      │
      ▼
┌────────────────────────────────────────┐
│ Phase 1: Small Model Call              │ ◄─── Generiert volle Antwort
│ (Parameters: logprobs: true)           │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ Proxy Interceptor:                     │
│ Berechne Durchschnitts-Entropie (H)    │ ◄─── H_avg über alle generierten Tokens
│ über den gesamten Response-Body        │
└───────────────────┬────────────────────┘
                    │
            [H >= Threshold?]
            ───┬─────────┬───
               │         │
            [Nein]      [Ja]
               │         │
               │         ▼
               │   ┌────────────────────────────────────────┐
               │   │ Phase 2: Reroute & Discard             │
               │   │ - Verwerfe die Small-Model-Antwort    │
               │   │ - Sende Request an teures Reasoning-M. │
               │   └───────────────────┬────────────────────┘
               │                       │
               ▼                       ▼
      [Serve Small Model]     [Serve Reasoning Model]

| High-Level Agent (LLM / DSH Plugin)                      |
| "Fahre vorsichtig um das Hindernis herum."                |
+-----------------------------+-----------------------------+
                              |
                              v (Übersetzung in latente Goals)
+-----------------------------+-----------------------------+

| Latent Space Planner (Cosmos / World Model)               |
| Simuliert zukünftige Zustände im Vektorraum               |
+-----------------------------+-----------------------------+
                              |
                              v (Trajektorien-Vorgabe)
+-----------------------------+-----------------------------+

| Low-Level Controller (Isaac / MPC / TensorRT)             |
| Berechnet exakte Physik-Frequenzen (z.B. 200 Hz Drehmoment) |
+-----------------------------------------------------------+
18:47

Think
The user is saying several things:
Da fehlt noch was — sag's wenn dir einfällt. Zwischendurch mache ich das Research-Doc für iframe caching mit HTTP/3:

Write
docs/research/R9-iframe-cache-http3-terminal-deploy.md
Research-Doc erstellt: R9-iframe-cache-http3-terminal-deploy.md

Das_doc deckt ab:

HTTP/3 server-side cache — QUIC, 0-RTT, reverse proxy cache vs client-side hidden pool vs hybrid
Terminal deployment — Claude Code / Aider / OpenCode CLI / predefined image / plain terminal
Icons — material/lucide/custom SVG pro deployment type
Was war noch das "dann war noch irgendwas"?

Produced
R9-iframe-cache-http3-terminal-deploy.md

18:48 · Ran for 1m 06s · TTFT 35s · 147 tok/s
also man muss halt trotzdem so provider spezifische settings dann haben jenachdem welches medium man wöhlt als bei dsh sind das ja wieder andere presets als bei terminal sachen also die provider oder diese apps müssen schon ihre eigenen schemas haben wenn man die dazu wählt ansonsten kann der user das dann selber dazu machen in den settings wenn das geht  aber ja also wir haben so wrapper. terminal seber hat ein wrapper aber wenn dazu noch claude code kommt, kommen zusätzliche packete und presets dazu also bruachen wir shcemas für sowas
18:50

Think
The user is saying:
Verstanden. Layered deployment schemas — base medium (terminal/DSH/OpenCode) hat sein eigenes schema, dann kommen provider/app addons (Claude Code, Aider) mit ihren eigenen paketen + presets obendrauf. Extensible, user kann eigene settings dazu packen.

Edit
docs/research/R9-iframe-cache-http3-terminal-deploy.md
Bash
Commit and push R9 research doc
Gepusht (a8024e1).

Layered Deployment Schemas — das Konzept
Copy
Deployment = Base Medium + Addons + User Overrides

┌─ Base: terminal ─────────────────────┐
│  shell: bash                        │
│  packages: [git, vim, curl]          │
│  ports: [7681]                       │
└─────────────────────────────────────┘
         ↓ + Addon: Claude Code
┌─ Addon: claude-code ─────────────────┐
│  provider: anthropic                │
│  packages: [anthropic-cli]           │
│  presets: { model: sonnet-4, ... }   │
└─────────────────────────────────────┘
         ↓ + Addon: JiMesh Mesh (auto-provision)
┌─ Addon: jimesh-mesh ────────────────┐
│  chain_id: smart:coding-free         │
│  auto_provision: true                │
└─────────────────────────────────────┘
         ↓ = Merged Schema
┌─ Final Config ──────────────────────┐
│  shell: bash                        │
│  packages: [git, vim, curl,         │
│             anthropic-cli]           │
│  ports: [7681]                      │
│  provider: anthropic                │
│  chain_id: smart:coding-free         │
│  model: sonnet-4                     │
└─────────────────────────────────────┘
Selber addon (Claude Code) auf anderem base (DSH) → andere merged config — DSH presets + Claude presets, nicht terminal presets + Claude presets.

Forschungs-Dok R9 bereit. Was war noch das "dann war noch irgendwas"?

Produced
R9-iframe-cache-http3-terminal-deploy.md

18:51 · Ran for 43s · TTFT 6.7s · 161 tok/s
achso was ich noch wollte war das wir halt für die stats von den models iregndwie halt noch mehr machen wie dieses artifical analysis als fallback wenn der user ein api key hat in den settings oder halt beides alsoopenrouter dann ist ja mehr quota und wenn da nix gefunden wird auch mit fuzzy nicht und keine finfos da sind macht das utilit mdoel halt mit ner seaerxng suche oder so und das halt als fallback für fuzzy dsa iwr nciht so viele gleiche aber doppelte models ahben genau. dann war noch die shceisse das wir die stats von openrouter und aa garnicht nuzen irgendwoie das war ja nur der models endpoint von openrouter das geht sogar mit curl also wir müssen unterscheiden zwischen statischen fakten für modelsaber auch provider und dynamische sachen da müssen wir halt kategorisiere und alles halt bitte mit schema dokumenten was wir überhapt bewertenund wie die pipeline funktioniert- auch mit unseren dynamischen parametern. genau also utility model und mach halt bitte für alles was wir esagt und getan haben jetzt sprints, tasks, epics und update den backlog und dokumentiere allesHier ist das umfassende Forschungsdokument R9, die Definition der geschichteten Deployment-Schemas, die intelligente Model-Metadata-Pipeline sowie der vollständige Epic-, Sprint- und Task-Backlog über alle bisher erarbeiteten Meilensteine (R1 bis R9).📑 R9 — HTTP/3 Server-Side Iframe Caching & Layered Terminal Deployments1. HTTP/3 Server-Side Iframe State Porting & Reverse Proxy CacheDas klassische Problem von Iframes in Dashboards ist der komplette State-Verlust (Re-Render) beim Ändern der DOM-Position oder beim Resizen. Da der JiMesh Go Core nativ auf HTTP/3 (QUIC) aufbaut, lösen wir dies über einen Server-Side Reverse Proxy Cache mit Zustandssynchronisation:[Browser Iframe Client] ◄───(HTTP/3 QUIC Session: 0-RTT, Multi-Streaming)───► [JiMesh Go Core Proxy]
         │                                                                             │
  (DOM Move / Resize)                                                          (State Snapshot)
         │                                                                             │
         ▼                                                                             ▼
[New Viewport Mount] ◄───(Stream Resume via QUIC Connection ID)────────────────► [Serve from Cache]
QUIC Connection Migration: HTTP/3 nutzt Connection IDs anstelle von IP/Port-Tupeln. Zerreißt das Frontend das Iframe im DOM und mountet es in einer anderen Grid-Kachel neu, wird die bestehende HTTP/3-Session ohne TCP-Handshake-Latenz (0-RTT) sofort fortgesetzt.Server-Side Content Caching: Der JiMesh-Proxy puffert die letzten Chunks des HTTP-Projekts im Arbeitsspeicher. Beim Neu-Mounten des Iframes liefert der Server den exakten HTML/JS-Snapshot aus, wodurch die Applikation visuell nicht flackert und Sessions erhalten bleiben.2. Layered Deployment Schemas & UX IconsEin Deployment besteht aus einem Base Medium (z. B. Terminal oder DSH) und optionalen Addon-Layern (z. B. Claude Code oder Aider). Jede Schicht bringt ihr eigenes JSON-Schema, Icons und Paket-Presets mit.🎨 Visual Identity Mapping🖥️ Base: Terminal: TerminalIcon (Lucide) / Custom Terminal SVG (Deep Charcoal).🚀 Base: DSH: CpuIcon (NVIDIA Green / DeepSeek Blue).🤖 Addon: Claude Code: AntropicIcon (Custom SVG, Clay-Orange).🛠️ Addon: Aider: WrenchIcon (Material Spark-Yellow).⚙️ Kompositions-Schema (Vite/Go kompatibel)json{
  "deployment_id": "dep_12345",
  "base_medium": {
    "type": "terminal",
    "image": "ubuntu-lts-jimesh-base:latest",
    "shell": "/bin/bash",
    "ports": [7681]
  },
  "addons": [
    {
      "id": "claude-code",
      "provider": "anthropic",
      "packages": ["@anthropic-ai/claude-code"],
      "env_presets": {
        "ANTHROPIC_API_KEY": "${USER_SECRET_CLAUDE_KEY}",
        "CLAUDE_CODE_MODEL": "claude-3-5-sonnet"
      }
    }
  ],
  "user_overrides": {
    "env": {
      "CUSTOM_ALIAS": "llm-dev"
    }
  }
}
3. Intelligent Model Metadata Pipeline & De-duplicationUm doppelte Modelle (z. B. durch unterschiedliche Benennungen bei OpenRouter, lokalen NIMs und Artificial Analysis) zu verhindern, nutzen wir eine mehrstufige Pipeline mit Fuzzy-Matching und einem Utility-Model Fallback.[Incoming Model ID] ──► [Exact Match Check] ──(Not Found)──► [Fuzzy Match (Levenshtein)] 
                                                                     │
                                                                 (No Match)
                                                                     ▼
[Final Clean Metdata] ◄── [Save & Cache] ◄── [Web Scraping] ◄── [Utility Model Search]
📊 Kategorisierungs-Schema für Model-FaktenStatische Fakten (Ermittelt via Pipeline & Scraping):json{
  "model_id": "deepseek-ai/deepseek-v3",
  "display_name": "DeepSeek V3 (Base)",
  "context_window": 131072,
  "parameters_total": 671000000000,
  "parameters_active": 37000000000,
  "pricing": { "input_per_1k": 0.00014, "output_per_1k": 0.00028 }
}
Dynamische Fakten (Live gemessen via JiMesh Proxy & OpenRouter API):json{
  "model_id": "deepseek-ai/deepseek-v3",
  "provider": "openrouter",
  "live_stats": {
    "ttfb_ms": 142.5,
    "tokens_per_second": 85.2,
    "uptime_24h": 0.9994,
    "current_queue_depth": 3
  }
}

type ReferenceSource string

const (
	ArtificialAnalysis ReferenceSource = "artificial_analysis"
	OpenRouter         ReferenceSource = "openrouter"
	ArxivAcademic      ReferenceSource = "arxiv_paper"
	JiMeshProxyLocal   ReferenceSource = "jimesh_telemetry"
)

// ModelFactSheet bündelt statische Evidenzen mit dynamischen Telemetriedaten
type ModelFactSheet struct {
	ModelID          string            `json:"model_id"`          // z.B. "deepseek-ai/deepseek-r1"
	MatchedAliases   []string          `json:"matched_aliases"`   // Fuzzy-erfasste Duplikate
	PrimaryReference ReferenceSource   `json:"primary_reference"` // Woher stammen die Architekturdaten?
	
	Architecture struct {
		IsMoE            bool    `json:"is_moe"`
		TotalParameters  int64   `json:"total_parameters"`
		ActiveParameters int64   `json:"active_parameters"`
		ContextWindow    int     `json:"context_window"`
		SpeculativeDraft string  `json:"recommended_draft_model,omitempty"`
	} `json:"architecture"`

	AcademicCitations []string `json:"academic_citations"` // z.B. ["arXiv:2406.04692"]
	
	GroundTruthMetrics map[ReferenceSource]struct {
		TTFB_ms           float64 `json:"ttfb_ms"`
		TokensPerSec      float64 `json:"tokens_per_sec"`
		InputCostPerMillion  float64 `json:"input_cost_usd_m"`
		OutputCostPerMillion float64 `json:"output_cost_usd_m"`
	} `json:"ground_truth_metrics"`
}

## Frage
Wäre es schlauer den iframe cache server-side zu machen und über HTTP/3 zu
porten, statt client-side (browser hidden pool)? Was bringt HTTP/3 hier?

## Recherche-Aufgaben

### 1. HTTP/3 (QUIC) für iframe caching
- [ ] Was ist HTTP/3 / QUIC?
  - UDP-based, multiplexed streams, 0-RTT connection resumption
  - Kein head-of-line blocking (im gegensatz zu HTTP/2 TCP)
  - Connection migration (IP wechsel ohne reconnect)
- [ ] Kann Go HTTP/3 server?
  - `quic-go` library — Go HTTP/3 implementation
  - `golang.org/x/net/http3` — experimental
  - Production-ready? Stability? Performance?
- [ ] Browser HTTP/3 support?
  - Chrome, Firefox, Safari — alle support HTTP/3?
  - Wird iframe content über HTTP/3 faster geladen?
  - 0-RTT: kann der browser eine "warm" connection für iframe cache nutzen?
- [ ] JiMesh als HTTP/3 proxy für iframe content?
  - JiMesh cached iframe content server-side
  - Client fragt JiMesh an → JiMesh hat gecacht → instant response
  - JiMesh fetcht im hintergrund neu (stale-while-revalidate)
  - HTTP/3 0-RTT für die connection zwischen client und JiMesh

### 2. Server-Side Cache Strategien
- [ ] Cache was genau?
  - Option A: Full HTML response vom target project (reverse proxy cache)
  - Option B: Nur die "skeleton" HTML + JS bundles (service worker style)
  - Option C: SSR snapshot (rendered DOM state)
- [ ] Cache invalidation:
  - TTL-based (wie im client approach: 300s)
  - Stale-while-revalidate (serve old, fetch new in background)
  - ETag / Last-Modified vom target
  - WebSocket/SSE push invalidation vom target project
- [ ] Cache storage:
  - In-memory (Go map + LRU)
  - Redis (bereits vorhanden)
  - Disk (für große HTML responses)
- [ ] Max cache size:
  - Memory limit (z.B. 100MB)
  - LRU eviction
  - Per-project max size

### 3. Client-Side vs Server-Side Vergleich
| Aspect | Client-Side (hidden iframe pool) | Server-Side (HTTP/3 cache) |
|---|---|---|
| Speed | Instant (DOM already in memory) | Fast (cached HTML, but browser must render) |
| Memory | Browser tab memory (N iframes) | Server memory (N cached responses) |
| State | Full app state preserved (JS running) | Only HTML/JS cached (state lost on re-render) |
| Complexity | Low (CSS display:none) | High (reverse proxy + cache logic) |
| HTTP/3 benefit | None (iframes talk directly to target) | Yes (0-RTT, multiplexing to cache server) |
| Refresh | Tab switch = instant | Needs re-render even with cache |
| Limitation | Max iframes = browser memory | State not preserved (SPA resets) |

### 4. Hybrid Approach?
- [ ] Client-side hidden pool for SPA state preservation (instant switch)
- [ ] Server-side cache for initial load speed (HTTP/3 0-RTT)
- [ ] Server-side pre-warming: JiMesh fetches project HTML on startup
  → first iframe load is instant (served from cache)
  → subsequent tab switches use client-side hidden pool
- [ ] HTTP/3 für die connection zwischen dashboard und JiMesh cache server
  → 0-RTT für cached responses → minimal latency

### 5. Implementation Complexity
- [ ] Go HTTP/3 server: quic-go library, cert management (self-signed OK für localhost?)
- [ ] Reverse proxy cache: Go http.Handler mit cache layer
- [ ] Cache invalidation: wie weiß JiMesh dass sich das project geändert hat?
  - Health endpoint poll?
  - File watcher auf project config?
  - Version header vom project?
- [ ] Browser support: muss browser HTTP/3 für localhost unterstützen?
  - Chrome: ja (quic://localhost oder alt-svc header)
  - Firefox: ja
  - Safari: ja (ab version 14+)

### 6. Terminal Deployment Type
- [ ] "Terminal" als deployment type (neben dsh, opencode, vscode-server, custom)
- [ ] Sub-types:
  - Provider-based: Claude Code (Anthropic CLI), Aider, OpenCode CLI
  - Predefined image: image mit dev tools (git, go, node, python) + provider
  - Plain terminal: just a shell, no AI provider
- [ ] Wie deployen?
  - Docker container mit ttyd / gotty (web terminal)
  - Oder xterm.js + WebSocket (wie vscode integrated terminal)
- [ ] Icons pro deployment type (material icons, lucide, custom SVG)

### 6. Layered Deployment Schemas (EXTENSIBLE)

Das core konzept: ein deployment = base medium + N provider/app addons + user overrides.

```
Deployment "Leo's Coding Terminal"
├── Base Medium: terminal (ttyd, git, go, node, python)
│   └── schema: { shell, packages, env, ports }
│
├── Addon: Claude Code (Anthropic CLI)
│   └── schema: { provider: anthropic, api_key, model, presets }
│   └── additional packages: anthropic-cli
│   └── additional presets: claude-code-config
│
├── Addon: Aider (optional)
│   └── schema: { provider: openai-compatible, base_url, model }
│   └── additional packages: aider
│
└── User Override:
    └── custom env vars, custom packages, custom presets
```

- [ ] **Base Medium Schema** (pro medium type):
  - `terminal`: { shell: bash/zsh, packages: [git, vim, curl], ports: [7681] }
  - `dsh`: { framework: dsh, ports: [3079], volumes: [dsh-data] }
  - `opencode`: { config: opencode.json, ports: [3080] }
  - `vscode-server`: { extensions, ports: [8080] }
  - `custom`: { user-defined }

- [ ] **Provider/App Addon Schema** (pro addon):
  - `claude-code`: { provider: anthropic, packages: [anthropic-cli], presets: [claude-config] }
  - `aider`: { provider: openai-compatible, packages: [aider], presets: [aider-config] }
  - `jimesh-mesh`: { provider: jimesh, packages: [], presets: [mesh-provision] }  ← auto-provision!
  - User kann eigene addons definieren: { name, packages, presets, config_schema }

- [ ] **Schema Registry** (DB):
  - `deployment_schemas` table: id, medium_type, name, description, config_schema (JSONB)
  - `deployment_addons` table: id, name, medium_type, packages (JSONB), presets (JSONB), config_schema (JSONB)
  - Schemas definieren welche settings Felder es gibt (TypeScript-style schema → frontend form generator)
  - User kann eigene schemas erstellen (custom addons)

- [ ] **Schema Composition**:
  - Base medium schema + addon schemas = merged config schema
  - Frontend rendert form basierend auf merged schema
  - Felder die in mehreren schemas definiert sind: addon überschreibt base
  - User overrides überschreiben alles
  - Beispiel: base terminal hat `shell: bash`, Claude Code addon fügt `provider: anthropic` hinzu,
    user override setzt `shell: zsh`

- [ ] **Preset System** (pro addon):
  - Claude Code presets: { model: claude-sonnet, max_tokens: 8192, system_prompt: ... }
  - Aider presets: { model: gpt-4o, edit_format: diff, auto_commits: true }
  - JiMesh mesh presets: { chain_id: smart:coding-free, auto_provision: true }
  - Presets = config templates die der user auswählen und anpassen kann

- [ ] **Medium-specific vs Addon-specific Settings**:
  - DSH medium: hat DSH-spezifische presets (code mode, standard mode, etc.)
  - Terminal medium: hat terminal-spezifische settings (shell, packages)
  - Claude Code addon: hat claude-spezifische settings (model, api_key)
  - Wenn man Claude Code zu DSH hinzufügt → merged schema = DSH settings + Claude settings
  - Wenn man Claude Code zu terminal hinzufügt → merged schema = terminal settings + Claude settings
  - Selber addon, anderes base medium → andere merged config

## Output Format

---

## Research Results (Operator-Provided)

### 1. HTTP/3 Server-Side Iframe Cache

HTTP/3 (QUIC) Connection Migration: HTTP/3 nutzt Connection IDs anstelle von
IP/Port-Tupeln. Zerreißt das Frontend das Iframe im DOM und mountet es in einer
anderen Grid-Kachel neu, wird die bestehende HTTP/3-Session ohne TCP-Handshake-
Latenz (0-RTT) sofort fortgesetzt.

Server-Side Content Caching: Der JiMesh-Proxy puffert die letzten Chunks des
HTTP-Projekts im Arbeitsspeicher. Beim Neu-Mounten des Iframes liefert der
Server den exakten HTML/JS-Snapshot aus, wodurch die Applikation visuell nicht
flackert und Sessions erhalten bleiben.

```
[Browser Iframe] ◄──(HTTP/3 QUIC: 0-RTT, Multi-Streaming)──► [JiMesh Go Core Proxy]
       │                                                          │
(DOM Move/Resize)                                          (State Snapshot)
       │                                                          │
       ▼Hier ist die detaillierte architektonische und mathematische Ausarbeitung für das Forschungsmodul R9, ergänzt um die gewünschten geschichteten Deployment-Schemas, die intelligente Metadaten-Pipeline sowie den vollständigen, überarbeiteten Projekt-Backlog.1. HTTP/3 Server-Side Iframe Caching vs. Client Hidden PoolDie Analyse zeigt, dass ein hybrider Ansatz die mathematisch und architektonisch performanteste Lösung darstellt. Ein reiner Server-Side-Cache kann den In-Memory-Laufzeitzustand (JS Heap State, offene Websockets) einer Single Page Application (SPA) nach dem Zerstören des iFrames im DOM nicht vollständig wiederherstellen. Er eliminiert jedoch die Netzwerklatenz beim Initial-Load und beim Recovery-Fallback drastisch.Die Rolle von HTTP/3 (QUIC):0-RTT Connection Resumption: Über QUIC-Kryptographie (TLS 1.3) speichert der Browser Session-Tickets. Wird ein iFrame neu gemountet, entfällt der TCP- und TLS-Handshake vollständig. Die Datenübertragung beginnt mit dem allerersten Paket.Multiplexing & HOL-Blocking-Eliminierung: Im Gegensatz zu HTTP/2 führt ein Paketverlust auf einem Stream (z. B. iFrame 1) bei HTTP/3 nicht zum Stillstand aller anderen iFrame-Streams. Jeder iFrame besitzt eine isolierte QUIC Stream-ID.Connection Migration: Wechselt das Dashboard-System die Netzwerkumgebung (z. B. von WLAN auf LAN/LTE), wandert die Verbindung dank eindeutiger QUIC Connection-IDs nahtlos mit, ohne dass iFrame-Verbindungen abbrechen.📊 Direktvergleich der StrategienKriteriumClient-Side (Hidden Pool)Server-Side Proxy Cache (HTTP/3)Hybrider JiMesh-Ansatz (Empfehlung)Umschaltzeit (Tab-Switch)Instant (0ms)Fast (~50-150ms Browser-Render)Instant für geladene Tabs, Fast für evizierte TabsArbeitsspeicher (Browser)Hoch (skaliert linear mit \(N\) iFrames)Niedrig (nur 1 aktiver iFrame im DOM)Kontrolliert (max. 3 iFrames im Hidden Pool)SPA-ZustandssicherungVollständig (JS-Laufzeit aktiv)Verloren (nur statische Assets/SSR)Vollständig für Core-Tabs; SSR für Background-TabsInitialer Page LoadNormalUltraschnell (0-RTT Cache)Ultraschnell (0-RTT Cache)2. Layered Deployment Schemas & UX IconsUm maximale Erweiterbarkeit zu garantieren, implementieren wir eine rekursive Schema-Komposition. Ein funktionales Deployment setzt sich wie ein Zwiebelschalenmodell zusammen: Base Medium + Addons + User Overrides.🎨 Visual Identity MappingJedem Layer ist ein eindeutiger Visual-Anchor zugeordnet, um im Multi-Window Dashboard sofortige Scannbarkeit zu gewährleisten:🖥️ Base terminal: TerminalIcon (Lucide) / CSS: stroke-slate-400🚀 Base dsh: CpuIcon (Lucide) / CSS: stroke-indigo-500🤖 Addon claude-code: Custom SVG (AntropicIcon, Clay-Orange)🛠️ Addon aider: WrenchIcon (Lucide) / CSS: stroke-amber-400🧬 Kompositions-ArchitekturDas System kombiniert die Teilschemas über einen tiefen JSON-Merge, bei dem Addons die Default-Werte des Basis-Mediums überschreiben und User-Overrides die höchste Priorität besitzen.┌────────────────────────────────────────────────────────┐
│ Base Medium Config (z.B. terminal)                    │
│ - shell: "/bin/bash"                                  │
│ - packages: ["git", "curl", "go"]                     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (+ Addon: claude-code)
┌────────────────────────────────────────────────────────┐
│ Addon Configuration                                    │
│ - packages: ["anthropic-cli"] (wird angehängt)         │
│ - env: { "CLAUDE_CODE_MODEL": "claude-3-5-sonnet" }   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (+ User Overrides)
┌────────────────────────────────────────────────────────┐
│ User Overrides                                         │
│ - shell: "/usr/bin/zsh" (überschreibt Base)            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (Resultierendes Schema im Go-Core)
┌────────────────────────────────────────────────────────┐
│ Merged Runtime Configuration                           │
│ - shell: "/usr/bin/zsh"                                │
│ - packages: ["git", "curl", "go", "anthropic-cli"]    │
│ - env: { "CLAUDE_CODE_MODEL": "claude-3-5-sonnet" }   │
└────────────────────────────────────────────────────────┘
3. Intelligent Model Metadata Pipeline & De-duplicationUm Datenredundanz zu vermeiden und unvollständige Modellstatistiken (z. B. fehlende Angaben zu Kontextfenstern oder Token-Preisen) zu korrigieren, führt der JiMesh Go-Core eine mehrstufige Konsolidierungs-Pipeline aus.[Eingehende Model-ID]
         │
         ▼
 ┌───────────────┐
 │ Exakter Match │ ───(Gefunden)───► [Return FactSheet]
 └───────┬───────┘
         │ (Nicht gefunden)
         ▼
 ┌───────────────────────────────────┐
 │ Fuzzy Match (Levenshtein d <= 3) │ ───(Gefunden)───► [Merge Aliases & Return]
 └───────┬───────────────────────────┘
         │ (Kein Treffer)
         ▼
 ┌───────────────────────────────────┐
 │ Query OpenRouter API &            │
 │ Artificial Analysis Fallback      │ ───(Gefunden)───► [Cache & Return]
 └───────┬───────────────────────────┘
         │ (Keine Strukturdaten vorhanden)
         ▼
 ┌───────────────────────────────────┐
 │ Utility Model Web Scraping        │ ───► [Extrahiere Kontext/Preise] ──► [Speichere DB]
 └───────────────────────────────────┘
📊 Kategorisierung der Fakten-Strukturen (Go-Typen)gopackage metadata

import "time"

type FactType string

const (
	StaticFact  FactType = "static"  // Unveränderliche Architekturdaten (z.B. Parameter)
	DynamicFact FactType = "dynamic" // Echtzeit-Telemetrie (z.B. Live-TTFB)
)

// ModelFactSheet bildet die Single Source of Truth für alle Routing-Entscheidungen
type ModelFactSheet struct {
	ModelID        string    `json:"model_id" db:"model_id"`
	DisplayName    string    `json:"display_name" db:"display_name"`
	Aliases        []string  `json:"aliases" db:"aliases"`
	ContextWindow  int       `json:"context_window" db:"context_window"`
	IsMoE          bool      `json:"is_moe" db:"is_moe"`
	ActiveParams   int64     `json:"active_parameters" db:"active_parameters"`
	TotalParams    int64     `json:"total_parameters" db:"total_parameters"`
	InputCost1K    float64   `json:"input_cost_per_1k" db:"input_cost_per_1k"`
	OutputCost1K   float64   `json:"output_cost_per_1k" db:"output_cost_per_1k"`
	LastScrapedAt  time.Time `json:"last_scraped_at" db:"last_scraped_at"`
	
	// Dynamische Performance-Metriken (Gepflegt durch Proxy-Messungen & AA-Fallback)
	Telemetry struct {
		LiveTTFB_ms      float64   `json:"live_ttfb_ms"`
		TokensPerSecond  float64   `json:"tokens_per_second"`
		ReliabilityScore float64   `json:"reliability_score"` // 0.0 - 1.0
		LastMeasuredAt   time.Time `json:"last_measured_at"`
	} `json:"telemetry"`
}
4. Master-Roadmap: Epics, Sprints & Backlog🏛️ Epic 1: Multi-Window Dashboard Grid & Runtimes (R1, R2, R7, R8, R9)Sprint 1: Layout & Core WindowsTASK-1.1 Setup von react-mosaic-component und Injektion der globalen CSS-Klasse iframe { pointer-events: none; } gesteuert über das Body-Attribut data-dragging="true".TASK-1.2 Implementierung des Docker-basierten Web-Terminal-Mediums via ttyd / xterm.js über gesicherte WebSocket-Verbindungen.Sprint 2: Layered Schemas & HTTP/3 Cache EngineTASK-1.3 Einbindung der quic-go Bibliothek im JiMesh Go-Core zur Bereitstellung des HTTP/3-Reverse-Proxies.TASK-1.4 Programmierung der serverseitigen Speicher-Engine (LRU-Cache, max. 100MB) zur iFrame-Zustandssicherung.TASK-1.5 Implementierung der relationalen Datenbank-Tabellen deployment_schemas und deployment_addons (JSONB) inklusive der serverseitigen Merge-Logik.🏛️ Epic 2: Proxy Router & Advanced Inferences (R4, R8)Sprint 3: Logprobs & Entropy MathTASK-2.1 Erweiterung des Go-Proxy-Parsers um die Extraktion granularer logprobs aus vLLM-, NIM- und OpenAI-Antworten.TASK-2.2 Mathematische Implementierung der normalisierten Shannon-Entropie-Formel zur quantitativen Messung der Modellunsicherheit.TASK-2.3 Integration der Two-Phase Self-Correction Pipeline (Phase 1: Generierung über kleines Modell -> Bei hoher Entropie: Abbruch, Verwerfen und automatischer Reroute an das Reasoning-Modell).Sprint 4: Speculative Decoding & Cost TrackingTASK-2.4 Integration der automatischen CLI-Flag-Generierung für vLLM/NIM-Deployments zur Aktivierung von --speculative-model und --num-speculative-tokens.TASK-2.5 Datenbank-Erweiterung (request_logs in PostgreSQL) um dedizierte Spalten für entropy (float64) und reasoning_tokens (int).🏛️ Epic 3: Multi-Agent Orchestration & MoE Engine (R3, R5, R6)Sprint 5: Go-Native Orchestrator CoreTASK-3.1 Implementierung der Go-Datenstrukturen (Task, AgentRole, WorkflowState) und Auflösung gerichteter, kreisfreier Graphen (DAG) via Goroutines.TASK-3.2 Integration von invopop/jsonschema zur dynamischen Erzeugung von Validierungs-Strukturen für Structured Outputs (JSON-Mode).TASK-3.3 Programmierung der automatischen Retry- und Self-Correction-Schleife bei fehlerhafter JSON-Validierung durch das LLM.Sprint 6: Gating, Provisioning & Live StreamsTASK-3.4 Erstellung des Gating-Agenten-Prompts für Llama-3.1-8B zur autonomen Auswahl von Experten und Ausführungsmodi (Parallel vs. Sequential).TASK-3.5 Implementierung des virtuellen /v1/models Endpoints in JiMesh, der aktive Mesh-Chains als auswählbare OpenAI-Modelle deklariert.TASK-3.6 Setup des Server-Sent Events (SSE) Event-Brokers zur Live-Übertragung von Agenten-Denkschritten und Chunks an das DSH-Plugin.🏛️ Epic 4: Model Analytics & Data Pipeline (R8, R9)Sprint 7: Analytics Integration & Metadata PipelineTASK-4.1 Integration der Artificial Analysis API und OpenRouter API als Fallback-Datenquellen für Modellstatistiken.TASK-4.2 Programmierung des Fuzzy-Matching-Algorithmus (Levenshtein-Distanz) im Go-Core zur Konsolidierung leicht abweichender Modellnamen.TASK-4.3 Implementierung des Utility-Model Scrapers: Wenn eine Modell-ID gänzlich unbekannt ist, triggert ein kleines Modell eine automatisierte Web-Suche, extrahiert die Kerndaten (Kontextfenster, Preise) und speichert sie im statischen Fakten-Cache.5. Datenbank-Migrationsskript für das Schema- und Metadatensystemsql-- Tabelle für die Basis-Medien (Terminal, DSH, OpenCode)
CREATE TABLE deployment_schemas (
    id VARCHAR(64) PRIMARY KEY,
    medium_type VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    config_schema JSONB NOT NULL, -- TypeScript-kompatibles JSON-Schema
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle für die Addons (Claude Code, Aider, JiMesh Auto-Provisioning)
CREATE TABLE deployment_addons (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    packages JSONB NOT NULL DEFAULT '[]'::jsonb,
    presets JSONB NOT NULL DEFAULT '{}'::jsonb,
    config_schema JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Erweiterung der bestehenden request_logs für das Epic 2 & 4 Tracking
ALTER TABLE request_logs 
ADD COLUMN IF NOT EXISTS entropy DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS reasoning_tokens INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS cached_tokens INT DEFAULT 0;

-- Tabelle für die bereinigten Modell-Fakten (Epic 4)
CREATE TABLE model_fact_sheets (
    model_id VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    aliases TEXT[] DEFAULT '{}'::TEXT[],
    context_window INT NOT NULL,
    is_moe BOOLEAN DEFAULT FALSE,
    active_parameters BIGINT DEFAULT 0,
    total_parameters BIGINT DEFAULT 0,
    input_cost_per_1k NUMERIC(10, 6) DEFAULT 0.0,
    output_cost_per_1k NUMERIC(10, 6) DEFAULT 0.0,
    last_scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
