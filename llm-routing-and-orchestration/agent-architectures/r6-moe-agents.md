---
okf_version: "1.0"
id: "okf-llm-age-r6-moe-agents"
title: "R6 — Model of Experts (MoE) for Agents"
topic: "llm-routing-and-orchestration"
subtopic: "agent-architectures"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-routing-and-orchestration
  - agent-architectures
summary: "Wie bauen wir ein Model-of-Experts pattern für agents? Mehrere spezialisierte agents"
---

# R6 — Model of Experts (MoE) for Agents

## Question
Wie bauen wir ein Model-of-Experts pattern for agents? Mehrere spezialisierte agents
with verschiedenen modellen, intelligent routing zwischen ihnen?

## Research Tasks

### 1. Agent-Level MoE verstehen
- [ ] Token-level MoE (im model) vs Agent-level MoE (between models) — unterschied?
- [ ] "Mixture of Experts" for agents:
  - N spezialisierte agents (coder, reviewer, planner, researcher)
  - Gating agent (small model) wählt expert(s)
  - Parallel (voting) or sequential (chain)
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
  - Aggregation: LLM-based synthesis or majority vote or concat
- [ ] **Sequential mode**: expert chain, jeder bekommt output des vorherigen
  - Chain depth limit (max 3-5?)
  - Intermediate results visible to user
- [ ] **Hybrid mode**: parallel for research, sequential for code→review
- [ ] Error handling: expert failure → skip + log? → retry? → use backup expert?

### 5. Result Aggregation
- [ ] Simple concat (alle expert outputs nacheinander)
- [ ] LLM synthesis (extra model aggregiert results → final answer)
- [ ] Majority vote (for factual questions)
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
1. Architecture diagram: gating agent → experts → aggregation
2. Expert schema (Go struct + JSON)
3. Execution mode empfehlung (wann parallel, wann sequential)
4. Aggregation strategy empfehlung
5. DB migration schema
6. DSH plugin mockup (text description)

---

## Question
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
with drag-resize-split-screen?

## Research Tasks

### 1. Grid Layout Library compare
Teste diese Libraries and bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` or `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues at resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues with iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir on `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistence
- [ ] localStorage vs PostgreSQL — was ist besser for layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze with Bewertung + Empfehlung + Link.
Entscheidung am Ende: welche Library, welches Layout-Schema, wie iframe embedding.Hier ist die strukturierte Bewertung and Architecture-Empfehlung for dein Multi-Window Dashboard Grid.1. Grid Layout Library VergleichBewertung: Für ein Dashboard with Iframe-Fokus ist react-grid-layout (RGL) am besten erprobt, da es Freiform-Grids bietet and in Version 2 vollen React 18+ and TypeScript-Support hat. golden-layout bietet zwar exzellentes IDE-Docking, kämpft aber stark with Iframes, da Tabs das DOM oft komplett zerstören/neu aufbauen, was Iframe-Resets erzwingt. react-mosaic-component (Tiling) and allotment (VS Code Split Panes) bieten saubere, serielle Tree-Layouts with guter TypeScript-Integration and kleiner Bundle Size, schränken aber die freie Dashboard-Anordnung im Comparison zu RGL ein. Der kritische Punkt at allen Libraries im Zusammenspiel with Drag-and-Resize ist das "Iframe-Pointer-Capture-Problem": Sobald die Maus beim Ziehen about einen Iframe rutscht, schluckt dieser die Mouse-Events, and der Drag-Vorgang bricht ab. [1] (https://www.npmjs.com/package/react-grid-layout), [2] (https://www.npmjs.com/package/react-mosaic-component), [3] (https://www.npmjs.com/package/allotment?activeTab=dependencies)Empfehlung: Nutze react-grid-layout, wenn du klassische Dashboard-Widgets willst, or react-mosaic-component, wenn ein striktes Kachel-Splitting (wie in einer IDE) gewünscht ist. Um das Iframe-Problem at beiden zu lösen, musst du während des Drag/Resize-Vorgangs via globalem CSS-State pointer-events: none on alle Iframes legen. [1] (https://www.npmjs.com/package/react-mosaic-component), [2] (https://www.npmjs.com/package/react-grid-layout)2. Iframe EmbeddingBewertung: Aus Sicherheitsgründen ist das Attribut sandbox="allow-scripts allow-same-origin" absolut kritisch; without allow-same-origin können Cookies/LocalStorage not richtig genutzt werden, während allow-scripts die Applikation im Iframe überhaupt erst lauffähig macht. Cross-Origin-Zugriffe zwischen localhost:9090 and localhost:9091 werden vom Browser blockiert (Same-Origin-Policy), weshalb direkter JS-Zugriff scheitert and Kommunikation ausschließlich via window.postMessage() erfolgen muss. Zudem müssen die eingebetteten Projekte zwingend darauf vorbereitet sein, in Iframes zu laufen: Wenn sie X-Frame-Options: DENY or restriktive CSPs (frame-ancestors 'none') konfiguriert haben, blockiert der Browser das Laden im Dashboard vollständig. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)Empfehlung: Bette die Projekte with sandbox="allow-scripts allow-same-origin allow-forms allow-popups" ein. Stelle sicher, dass die Quellprojekte keinen X-Frame-Options Header senden, sondern stattdessen Content-Security-Policy: frame-ancestors http://localhost:dashboard-port restriktiv setzen, and nutze eine CSS-Klasse with width: 100%; height: 100%, um dem Iframe das automatische Skalieren des Layout-Containers zu überlassen. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)3. Layout PersistenzBewertung: localStorage eignet sich hervorragend for temporäre Benutzerpräferenzen, UI-Zustände on Client-Seite and schnelles Prototyping without Latenz. PostgreSQL ist zwingend erforderlich, um Layouts persistent about mehrere Endgeräte hinweg zu speichern, geteilte Team-Templates bereitzustellen and Datenverlust beim Löschen von Browserdaten zu verhindern. Ein serialisierbares JSON-Schema reicht for beide Speicherarten völlig from. Vordefinierte Templates (z. B. Coding, Debugging) lassen sich serverseitig als statische JSON-Schemata hinterlegen and per Knopfdruck laden.Empfehlung: Nutze PostgreSQL als Single Source of Truth for gespeicherte Layouts, puffere Änderungen im Frontend via Debounce and nutze ein Schema, das flexibel genug for Erweiterungen ist.Layout Schema:json{
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

## Question
Welche deployments brauchen redeploy vs hot-reload? Wie editieren wir config files?

## Research Tasks

### 1. Deployment Types catalog
Für jeden Typ: was ändert sich per config? Was braucht rebuild?

| Typ | Config file | Config change = | Code change = |
|---|---|---|---|
| DSH (DeepSeek Harness) | `vconfig.json` | hot-reload (client HMR) | rebuild backend |
| OpenCode | `config.json` / `.opencode` | restart | git pull + restart |
| OpenMesh backend | `docker-compose.yml` env | restart-backend | rebuild Go binary |
| OpenMesh frontend | `.env` | frontend-clean | frontend-clean |
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
Empfehlung for editor library and restart mechanismus.Hier ist die systematische Aufschlüsselung for deine Deployment-Konfigurationen sowie die Recommendations for den Editor and Neustart-Mechanismus.1. Deployment-Types KatalogTypConfig-PfadConfig Change (Verhalten)Code Change (Verhalten)Restart Command (Backend-Vorgehen)DSH (DeepSeek Harness)vconfig.jsonHot-Reload (Client HMR via pnpm run dev:web)Rebuild Backend (at .proto Changes: protoc Rebuild nötig)Kein Restart at Config, da In-Memory-HMR; at Proto-Wechsel: pkill -f dsh-backend && go run main.goOpenCodeopencode.json / tui.jsonRestart erforderlichGit Pull + Restartopencode restart (or kill des TUI-Prozesses)OpenMesh Backenddocker-compose.yml (env)Restart-BackendRebuild Go Binarydocker compose restart openmesh-backendOpenMesh Frontend.envFrontend-Clean (Vite/Webpack Cache-Wipe + Rebuild)Frontend-Clean (Vite HMR/Rebuild)docker compose exec openmesh-frontend npm run buildLeadScraperconfig.prod.json / .envRestartPM2 Reload / Pullpm2 restart lead-scraper --update-envCustom HTTP Server.env / Custom JSONRestartDepends (z. B. Node.js Restart vs. Go Rebuild)pkill -f custom-server && npm run start (or entsprechendes Binary)DSH HMR: pnpm run dev:web reicht for Frontend-Plugins völlig from. Ändern sich jedoch Protokolldefinitionen (.proto), muss die gRPC-Struktur about den protoc-Compiler neu generiert werden, was einen Backend-Rebuild erzwingt. [1] (https://medium.com/@dhleee0123/live-reload-vs-hot-deploy-with-hot-reload-and-hot-swap-260574c6e47c)OpenCode Details: Nutzt opencode.json (or opencode.jsonc for Kommentare) im Projektexekutions-Pfad. Änderungen an LLM-Providern or Keybindings greifen erst after einem Prozess-Neustart. [1] (https://opencode.ai/docs/config/), [2] (https://opencode.ai/docs/references/), [3] (https://www.josean.com/posts/how-to-use-opencode-ai)LeadScraper: Läuft in der Regel als Node.js/Python-Scraper-Skript, gemanagt via PM2 for stabiles Error-Handling at Timeout-Crashes.2. Config Editor: CodeMirror 6 vs. MonacoBewertung & Empfehlung: Nutze CodeMirror 6 (about @uiw/react-codemirror). Monaco Editor (@monaco-editor/react) ist zwar mächtig, bläht das Bundle-Size jedoch enorm on (oft >4MB via Web-Worker) and verlangsamt das Dashboard beim Rendern mehrerer Instanzen drastisch. CodeMirror 6 ist modular aufgebaut, extrem leichtgewichtig, performant innerhalb von Iframes/Grids and bietet native, vollwertige Extensions for Syntax-Highlighting (JSON, YAML, TOML) sowie ein exzellentes, schlankes Diff-View-Addon.Schreib-/Lesezugriff: Der Zugriff muss ausschließlich via Backend-API (GET/POST /api/projects/{id}/config) erfolgen. Direkter Dateisystemzugriff from dem Browser heraus bricht Sandbox-Richtlinien and verhindert Berechtigungsprüfungen (z. B. Validierung des JSON-Schemas before dem Schreiben).3. Restart Mechanism & RobustheitImplementierung der API: POST /api/projects/{id}/restart steuert je after Deployment-Typ die jeweilige Engine an:Docker: Nutzt das offizielle dockerode NPM-Paket for den API-Aufruf (container.restart()) statt Shell-Execs.PM2: Nutzt das programmatische pm2.restart(name, err => {}) SDK.Prozess: Sendet SIGTERM for Graceful Shutdowns, wartet 5 Sekunden, gefolgt von SIGKILL at Timeouts.Graceful Shutdown & Rollback: Vor jedem Schreibvorgang legt das Backend ein Backup an (config.json.bak). Nach dem Restart-Befehl geht das Dashboard in den Zustand building/restarting. Eine HTTP-Polling-Schleife (or ein Health-Check-Endpoint des Projekts) prüft die Erreichbarkeit. Schlägt der Health-Check for 30 Sekunden fehl, kopiert das Backend die .bak-Datei zurück and triggert einen automatischen Rollback-Neustart.4. Settings Button UXPlatzierung: Platziere das ⚙️-Icon oben rechts in der Fenster-Menüleiste (Window Header) des jeweiligen Grid-Fensters (neben Miniminieren/Maximieren). Auf der Deployment-Card selbst blockiert es den Lesefluss.Panel-Typ: Nutze ein Inline-Slide-Over-Panel (Drawer), das sich von rechts in das spezifische Grid-Fenster hineinschiebt. Ein modales Overlay (Modal) reißt den Nutzer from dem Dashboard-Kontext, während ein Inline-Panel das parallele Beobachten von Log-Fenstern im Dashboard erlaubt.Button-Logik: Der primäre Aktionsbutton passt sich dynamisch an das Deployment an:Erkennt das System ein DSH-Projekt, heißt der Button "Save & Apply" (grün, führt reines Hot-Reload from).Bei OpenCode or Docker-Systemen heißt er "Save & Restart" (orange/blau, warnt visuell before einer kurzen Downtime).🛠 Vorgeschlagene UI-Komponente for den Editortsximport CodeMirror from '@uiw/react-codemirror';
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

## Question
Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als
provider in coding deployments (Ollama, OpenCode, DSH)?

## Research Tasks

### 1. Ziel-Formate
Welche config formats brauchen coding tools for custom providers?

- [ ] **OpenCode**: provider config format? JSON? YAML? Wo gespeichert?
  - Suchen: OpenCode docs for custom provider / custom OpenAI endpoint
  - Felder: `base_url`, `api_key`, `model_name`?
- [ ] **Ollama**: kann Ollama einen remote OpenAI endpoint als model registrieren?
  - `ollama pull` von custom model? Modelfile with `FROM` remote?
  - Oder besser: OpenMesh als OpenAI proxy → coding tool zeigt on `openmesh:9091`
- [ ] **DSH (DeepSeek Harness)**: provider config in vconfig.json?
  - Wie trägt man custom OpenAI endpoint ein?
  - Können wir DSH models page nutzen um OpenMesh zu registrieren?
- [ ] **Cursor / VS Code**: `.cursor/config`? settings.json `openai.baseUrl`?

### 2. Provisioning API
- [ ] `POST /api/projects/{id}/provision` — body: `{ chainId, format }`
  - Liest die chain endpoint URL + deploy token from OpenMesh
  - Schreibt sie ins coding tool's config format
  - Restartet das tool falls nötig (hot-reload vs redeploy)
- [ ] Auto-provision: beim deploy eines coding projects → automatisch alle
  aktiven mesh chains als provider eintragen
- [ ] Provisioning status: erfolgreich? Config überschrieben? Backup erstellt?

### 3. Model-Namens-Mapping
- [ ] OpenMesh chain name → coding tool model name
  - `smart:coding-free` → model name in OpenCode?
  - Multiple chains → multiple "models" in der auswahl?
- [ ] Model discovery: coding tool sollte `/v1/models` vom OpenMesh proxy abrufen
  können → wir haben das schon (`/v1/models` endpoint)
- [ ] Brauchen wir einen dedizierten `/v1/models` der die chain-namen als
  "models" zurückgibt? (statt platform model IDs)

### 4. Mouse-Click Provisioning
- [ ] Per drag-drop: mesh endpoint from sidebar → coding deployment config
- [ ] Per button: "Add to OpenCode" / "Add to DSH" neben jedem chain
- [ ] Per auto: checkbox "auto-provision on deploy" pro coding project
- [ ] Feedback: toast "Added smart:coding-free to OpenCode as model 'openmesh-coding-free'"

## Output Format
Pro coding tool: config path, format, fields, provisioning command.
Empfehlung: auto-provision strategy (auto vs manual vs hybrid).
Schema for `/v1/models` endpoint der chain-namen zurückgibt.Hier ist das Systemdesign for das automatische Provisionieren von OpenMesh Fallback Endpoints and Modellen direkt in deine Coding-Deployments.1. Ziel-Formate der Coding ToolsToolConfig-Pfad (relativ / global)FormatWichtige Felder for Custom ProviderProvisioning Command / TriggerOpenCode~/.config/opencode/opencode.json (global) or opencode.json (Projekt)JSON"provider": { "openmesh": { "options": { "baseURL": "...", "apiKey": "..." }, "models": { "chain-id": {} } } }POST /api/projects/{id}/config -> JSON-Patch (Kein Restart nötig at Dateimanipulation)Ollama— (Wird als Proxy umgangen)Modelfile / APIKein Pull nötig. OpenMesh agiert direkt als Proxy, sodass andere Tools on openmesh:9091 statt on Ollama zeigen.Keiner (OpenMesh fängt /v1/chat/completions ab).DSH./vconfig.json (im Workspace)JSON"openai_compatible_providers": [{ "name": "OpenMesh", "api_base": "...", "api_key": "..." }]In-Memory Hot-Reload via Client-HMR (pnpm run dev:web).Cursor / VS Code.cursorrules / .vscode/settings.jsonJSON"openai.baseUrl": "http://localhost:9091/v1", "openai.apiKey": "openmesh-token"Automatisches Einlesen through den Datei-Watcher der IDE.OpenCode-Besonderheit: OpenCode erlaubt das Einbinden von Custom OpenAI-kompatiblen Endpunkten about die Definition eines Custom-Schlüssels im "provider"-Objekt (z. B. "openmesh"), benötigt aber zwingend die explizite Auflistung der verfügbaren Modell-IDs unter "models". [1] (https://github.com/orgs/community/discussions/200311), [2] (https://docs.ollama.com/integrations/opencode)Ollama-Strategie: Ollama about ein Modelfile with FROM http://... zu provisionieren fügt unnedige Netzwerklatenz and Speicher-Overhead hinzu. Die Architecture-Empfehlung lautet hier klar: OpenMesh als zentraler OpenAI-Proxy, an den sich die Editoren direkt hängen.2. Provisioning API (POST /api/projects/{id}/provision)Wenn ein Projekt deployt wird (or ein neuer Mesh-Fallback-Endpoint via Drag-and-Drop hinzukommt), stößt das Dashboard die Provisionierung an:Read State: Das Backend liest die aktive Mesh-Konfiguration (Chain-URLs and Tokens) from der OpenMesh-Instanz from.Generate Config Patch: Basierend on dem Typ des Ziel-Deployments wird die spezifische Konfigurationsdatei manipuliert.Backup & Write: Das Backend sichert die bestehende Datei (.json.bak) and schreibt die neue Struktur atomar.HMR Trigger / Reload: Bei DSH wird der Hot-Reload-Endpoint getriggert; OpenCode liest die Projekt-opencode.json beim nächsten Befehl automatisch frisch ein.3. Model-Namens-Mapping (/v1/models)Da Editoren and CLI-Tools wie OpenCode dynamische or statische Modelllisten erwarten, muss OpenMesh einen dedizierten, standardkonformen OpenAI-Endpoint bereitstellen, der die aktiven Mesh-Chains als virtuelle Modell-IDs ausgibt. [1] (https://github.com/anomalyco/opencode/issues/26863), [2] (https://github.com/orgs/community/discussions/200311)Schema for den /v1/models Endpoint:json{
  "object": "list",
  "data": [
    {
      "id": "openmesh:smart:coding-free",
      "object": "model",
      "created": 1717545600,
      "owned_by": "openmesh-mesh"
    },
    {
      "id": "openmesh:fast:inline-completion",
      "object": "model",
      "created": 1717545600,
      "owned_by": "openmesh-mesh"
    }
  ]
}
  "$schema": "https://opencode.ai/config.json",
  "model": "openmesh/openmesh:smart:coding-free",
  "provider": {
    "openmesh": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "OpenMesh Proxy",
      "options": {
        "baseURL": "http://localhost:9091/v1",
        "apiKey": "jm_live_tkn_84920f"
      },
      "models": {
        "openmesh:smart:coding-free": {},
        "openmesh:fast:inline-completion": {}
      }
    }
  }
}

## Question
Wie funktioniert NVIDIA's "instruct" principle (kleines model routet, großes model
reasoned nur at bedarf) and wie können wir es with entropy-based routing im proxy
nachbauen?

## Research Tasks

### 1. Nemotron Architecture verstehen
- [ ] NVIDIA Nemotron-3-Ultra-550B: 55B active parameters (Mixture-of-Experts)
  - Wie funktioniert der routing mechanismus im model selbst?
  - "A55b" = 55B active von 550B total → MoE with 10:1 sparsity
  - Kann man das pattern on agent-level anwenden (not token-level)?
- [ ] NVIDIA Reasoning Engine:
  - Wie entscheidet die engine ob ein task an das reasoning model geht?
  - Ist es entropy-based or rule-based?
  - Welche thresholds/parameters?
  - Doku: developer.nvidia.com reasoning engine docs

### 2. Entropy-Based Routing Implementation
- [ ] logprobs API:
  - OpenAI: `logprobs: true` in chat completions → returns top logprobs per token
  - vLLM/NIM: `logprobs: N` parameter
  - Anthropic: supports logprobs? (check API docs)
  - Andere provider: welche unterstützen logprobs?
- [ ] Shannon Entropy berechnen:
  - Formula: H = -sum(p_i * log2(p_i)) about top-k tokens
  - k = 5? 10? Alle tokens?
  - Normalisierung: H / log2(k) → 0..1 range
  - Threshold: 0.5? 0.3? Empirisch testen
- [ ] Implementation im proxy:
  - Request geht zuerst an planner model with `logprobs: true`
  - Proxy berechnet entropy from logprobs
  - Wenn entropy < threshold → accept response (fast, cheap)
  - Wenn entropy >= threshold → re-route zu reasoning model
  - Cache: for gleiche requests? (z.B. for 5 minuten)

### 3. Planner Model Selection
- [ ] Kriterien for planner model:
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
  - Ist das akzeptabel for jeden request?
  - Alternative: nur for requests die not trivial klassifizierbar sind
- [ ] Streaming: kann der planner parallel zum user streamen?
  - Nein — planner muss zuerst entscheiden, dann wird weitergeroutet
  - Aber: planner kann sehr schnell sein (8B model, max_tokens=10)
- [ ] Caching: häufige request patterns → skip planner

## Output Format
1. Architecture diagram (planner → entropy check → route decision)
2. Entropy formula + implementation pseudocode
3. Planner model empfehlung with begründung
4. Latency benchmark erwartung
5. Config schema: `entropy_routing: { enabled, threshold, planner_model, cache_ttl }`Das NVIDIA Instruct Principle trennt die rechenintensive "Denkfähigkeit" von der reinen Befehlsverfolgung. Auf Agenten- or Proxy-Ebene bedeutet das: Ein kleines, ultraschnelles Planner-Modell fängt den Request ab, klassifiziert ihn and kalkuliert seine eigene statistische Unsicherheit via Shannon-Entropie. Nur at hoher Unsicherheit (hoher Entropie) leitet der Proxy den Request an ein teures, langsames Reasoning-Modell (z. B. DeepSeek-R1 or o1) weiter. [1] (https://docs.nvidia.com/nim/large-language-models/1.8.0/reasoning-model.html), [2] (https://docs.nvidia.com/nim/large-language-models/1.12.0/reasoning-model.html), [3] (https://inworld.ai/resources/what-is-an-ai-router)1. Architecture-Diagramm                      +-------------------+

                      |   User Request    |
                      +---------+---------+
                                |
                                v
                    +-----------------------+

                    |  OpenMesh Proxy Router  |
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
2. Entropie-Formel & ImplementationDie Shannon-Entropie \(H\) misst die Unberechenbarkeit der Token-Verteilung. Wir ziehen die Wahrscheinlichkeiten \(p_{i}\) from den logprobs des allerersten Answer-Tokens des Planners. [1] (https://openreview.net/forum?id=hFxivbAgVP), [2] (https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1892739/full)Formel:\(H=-\sum _{i=1}^{k}p_{i}\log _{2}(p_{i})\)Zur besseren Handhabung im Proxy wird die Entropie about die Anzahl der ausgewerteten Tokens (\(k\)) normalisiert, sodass der Wert exakt zwischen 0.0 (absolute Gewissheit) and 1.0 (maximale Verwirrung/Gleichverteilung) liegt:\(H_{norm}=\frac{H}{\log _{2}(k)}\)Proxy Pseudocode (Node.js / TypeScript):typescriptimport { OpenAI } from 'openai';

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
  return entropy / maxEntropy; // Normalisiert on die Range 0.0 - 1.0
}

async function routeProxyRequest(userPrompt: string, config: any) {
  // 1. Prüfe Cache, um wiederholte Planner-Calls zu skippen
  const cachedRoute = await cache.get(userPrompt);
  if (cachedRoute) return executeRoute(cachedRoute, userPrompt);

  const openai = new OpenAI({ baseURL: config.entropy_routing.planner_url });

  // 2. Rufe den Planner extrem sparsam on (nur das Klassifikations-Token generieren)
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
  if (!firstTokenChoice) return executeRoute('reasoning_model', userPrompt); // Fallback at API-Fehlern

  // 3. Berechne statistische Unsicherheit
  const normalizedEntropy = calculateNormalizedEntropy(firstTokenChoice.top_logprobs);

  let targetRoute = 'planner_model'; // Standard-Pfad (Günstig & Schnell)

  // Wenn Entropie den Schwellenwert reißt, eskaliere zum teuren Reasoning-Modell
  if (normalizedEntropy >= config.entropy_routing.threshold) {
    targetRoute = 'reasoning_model';
  }

  // 4. Cache die Routing-Entscheidung for diesen Pattern-Typ
  await cache.set(userPrompt, targetRoute, config.entropy_routing.cache_ttl);

  return executeRoute(targetRoute, userPrompt);
}
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

## Question
Welches framework for multi-agent orchestration? Custom OpenMesh-native or
etabliertes framework (CrewAI, LangGraph, AutoGen)?

## Research Tasks

### 1. CrewAI
- [ ] Architecture: wie definiert man crews, agents, tasks?
- [ ] Role-based: wie werden agent roles mapped?
- [ ] LLM integration: kann man custom OpenAI endpoint (OpenMesh) nutzen?
- [ ] Structured output: pydantic models for task results?
- [ ] Process types: sequential, hierarchical, consensual?
- [ ] Python-only? Go alternative?
- [ ] Dependencies: was zieht es ein? (langchain? instructor?)
- [ ] Performance: overhead per agent call?
- [ ] Stars, maintenance, last update
- [ ] Doku: crewai.com/docs

### 2. LangGraph
- [ ] Architecture: graph-based agent workflows (nodes + edges)
- [ ] Conditional routing: wie entscheidet der graph welcher agent als nächstes?
- [ ] State management: wie wird state zwischen nodes geteilt?
- [ ] Integration: OpenAI compatible endpoints?
- [ ] Python-only? Go port?
- [ ] Dependencies: langchain core? wie viel overhead?
- [ ] Streaming: intermediate results streaming?
- [ ] Stars, maintenance, last update
- [ ] Doku: langchain-ai.github.io/langgraph

### 3. AutoGen
- [ ] Architecture: multi-agent conversation framework
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
- [ ] Go alternative? (Go hat no pydantic, aber `encoding/json` + struct tags)
- [ ] Overhead: wie viele extra tokens for structured output?
- [ ] Kompatibel with allen frameworks?
- [ ] Doku: instructor-ai.github.io/instructor

### 5. Custom OpenMesh-Native Orchestration
- [ ] Keine framework dependencies
- [ ] Direkter mesh route access (no API abstraction layer)
- [ ] Go-native: goroutines for parallel agent execution
- [ ] Schema: Go structs for task results (statt pydantic)
- [ ] Routing: direkt via sortKeysByQuota + bandit
- [ ] Overhead: minimal (no framework overhead)
- [ ] Disadvantages: müssen features selbst bauen (retry, state mgmt, etc.)

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
- [ ] Core orchestration in Go (OpenMesh-native)
- [ ] Optional CrewAI/LangGraph adapter for Python users
- [ ] Adapter als sidecar service (Python process) der with OpenMesh API spricht
- [ ] Overhead: sidecar adds latency but only when used

## Output Format
1. Vergleichs-Matrix ausgefüllt
2. Empfehlung: Custom core + optional adapter? Oder framework?
3. Falls custom: feature list was wir selbst bauen müssen
4. Falls framework: integrations architektur
5. Go-struktur for orchestration (task, agent, role, route mapping)Hier ist die strategische Architekturbewertung for die Multi-Agenten-Orchestrierung innerhalb deines OpenMesh-Ökosystems.1. Vergleichs-MatrixDa OpenMesh nativ in Go geschrieben ist, während die etablierten Frameworks schwere Python-Monolithen sind, sieht das Spielfeld bezüglich Performance and Kontrolle wie folgt from: [1] (https://www.n-ix.com/langgraph-vs-crewai-vs-autogen/)FeatureCrewAILangGraphAutoGen / AG2Custom (OpenMesh-Native)LanguagePythonPython & JS/TSPython (AG2) / .NETGo-nativeFramework DepsHeavy (LangChain/Pydantic)Heavy (LangChain Core)Medium (Microsoft SDK)NoneCustom LLM EndpointJa (via OpenAI-Abstraktion)Ja (via LangChain-ChatOpenAI)Ja (via LiteLLM/OpenAI-Client)Native (direkter In-Process Route-Access)Structured OutputNative PydanticPydantic / JsonSchemaEingeschränkt / JSON-ParsingGo Structs (JSON Tags + jsonschema)Parallel AgentsSequentiell / HierarchischJa (Verzweigte Graph-Knoten)Ja (Group Chat Turn-Taking)Ja (Ultraschnelle Goroutines)State ManagementTask-based (linear)Graph State (Reducers / Checkpoints)Konversations-HistorieMemory-State in Go (Channels/Mutex)StreamingEingeschränktJa (Node- & Token-Streaming)EingeschränktNative Server-Sent Events (SSE)Maintenance RiskMedium (kommerzielle Firma)Hoch (LangChain API-Churn)Hoch (Microsoft im Maintenance Mode)Minimal (voller Code-Besitz)Learning CurveNiedrigHoch (Steile Graph-Logik)MediumNiedrig (Standard Go-Web-Architecture)2. Strategische Empfehlung: Der Hybride AnsatzNutze Custom Core in Go (OpenMesh-native) + Optionale Python-Adapter.Begründung: Ein fremdes Python-Framework als Kernkomponente in ein hochperformantes Go-System (OpenMesh) zu zwingen, bricht deine Performance-Advantages (Latenz, Memory-Footprint). Python-Frameworks wie CrewAI erzeugen pro Agentenschritt massiven Overhead. [1] (https://gurusup.com/blog/best-multi-agent-frameworks-2026), [2] (https://www.n-ix.com/langgraph-vs-crewai-vs-autogen/)Der Core (Go): Übernimmt die latenzkritische and parallele Ausführung von Agenten-Pipelines mithilfe von Goroutines, verwaltet den State and streamt Event-Daten live about SSE an dein R1-Dashboard.Der Python-Adapter (Sidecar): Falls Entwickler explizit bestehende Python CrewAI-Crews or LangGraph-Graphen nutzen wollen, stellt OpenMesh einen leichtgewichtigen API-Endpunkt bereit. Das Framework läuft autark in einem isolierten Python-Prozess (Sidecar) and kommuniziert with OpenMesh als OpenAI-kompatiblem Provider. [1] (https://gurusup.com/blog/best-multi-agent-frameworks-2026)3. Feature-Liste for OpenMesh-Native Orchestration (Go)Da du das Rad not komplett neu erfinden musst, konzentriert sich die Implementation on diese Kern-Features:JSON-Schema Generierung: Nutze Bibliotheken wie invopop/jsonschema, um from nativen Go-Structs zur Laufzeit JSON-Schemas zu erzeugen, die an das LLM via response_format: { type: "json_object", schema: ... } (Structured Outputs) übergeben werden.Retry- & Validierungs-Schleife: Ein Interceptor, der die LLM-Answer gegen das Go-Struct unmarshalt. Schlägt dies fehl, wird ein automatischer Self-Correction Prompt (inkl. Fehlermeldung) for maximal 3 Versuche an das LLM zurückgesendet.State Management (Context-Passing): Ein thread-sicheres Context-Objekt (sync.Map or geschützte Structs), das sequentiell or parallel von Agent-Knoten manipuliert and ausgelesen werden kann.Token- & Event-Broker: Ein zentraler Go-Channel, in den jeder Agent seinen Status (agent:started, agent:thinking, token:generated, agent:completed) pusht, um das Frontend per SSE-Stream in Echtzeit zu füttern.4. Integrations-Architecture for Python-FrameworksWenn ein User ein Python-Framework (z.B. CrewAI) nutzen möchte, agiert OpenMesh rein als intelligenter, lokaler Proxy.+------------------------------------------------------------+

|                       OpenMesh Pod                           |
|                                                            |
|  +------------------------+      +----------------------+  |
|  | Python Sidecar Process |      |  OpenMesh Go Core      |  |
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
5. Go-Datenstrukturen for die OrchestrierungDieses Typsystem bildet das Fundament for deinen OpenMesh-nativen Workflow-Manager:gopackage orchestration

import (
	"context"
	"encoding/json"
	"time"
)

// AgentRole definiert die System-Instruktion and Meta-Daten des Agenten
type AgentRole struct {
	Name         string   `json:"name"`
	Role         string   `json:"role"`         // z.B. "Code Auditor"
	Backstory    string   `json:"backstory"`    // System-Prompt Ergänzung
	AllowedTools []string `json:"allowed_tools"` // IDs registrierter Werkzeuge
}

// RouteMapping verknüpft den Agenten with den Routing-Sperren and Quotas from dem Proxy
type RouteMapping struct {
	TargetModel  string        `json:"target_model"`  // Virtuelle ID from /v1/models
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
	OutputFormat interface{}  `json:"-"`            // Pointer zu einem Go-Struct for Structured Output
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

// WorkflowState orchestriert die parallele Ausführung about den State hinweg
type WorkflowState struct {
	ID        string                `json:"workflow_id"`
	Context   context.Context       `json:"-"`
	Data      map[string]interface{} `json:"data"` // Shared State (Thread-safe kapseln!)
	Results   map[string]TaskResult `json:"results"`
	EventChan chan string           `json:"-"`     // Broadcast Channel for Live SSE-Streaming
}

## Question
Wie bauen wir ein Model-of-Experts pattern for agents? Mehrere spezialisierte agents
with verschiedenen modellen, intelligent routing zwischen ihnen?

## Research Tasks

### 1. Agent-Level MoE verstehen
- [ ] Token-level MoE (im model) vs Agent-level MoE (between models) — unterschied?
- [ ] "Mixture of Experts" for agents:
  - N spezialisierte agents (coder, reviewer, planner, researcher)
  - Gating agent (small model) wählt expert(s)
  - Parallel (voting) or sequential (chain)
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
  - Aggregation: LLM-based synthesis or majority vote or concat
- [ ] **Sequential mode**: expert chain, jeder bekommt output des vorherigen
  - Chain depth limit (max 3-5?)
  - Intermediate results visible to user
- [ ] **Hybrid mode**: parallel for research, sequential for code→review
- [ ] Error handling: expert failure → skip + log? → retry? → use backup expert?

### 5. Result Aggregation
- [ ] Simple concat (alle expert outputs nacheinander)
- [ ] LLM synthesis (extra model aggregiert results → final answer)
- [ ] Majority vote (for factual questions)
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
1. Architecture diagram: gating agent → experts → aggregation
2. Expert schema (Go struct + JSON)
3. Execution mode empfehlung (wann parallel, wann sequential)
4. Aggregation strategy empfehlung
5. DB migration schema
6. DSH plugin mockup (text description)Das Agent-Level MoE (Mixture of Experts) transferiert das Token-Sparsity-Prinzip großer LLM-Modelle (wie Nemotron or DeepSeek V3/V4) on die Anwendungsebene. Statt Token for Token im neuronalen Netz zu routen, steuert ein Gating-Agent (Orchestrator) on Task-Ebene, welche spezialisierten Agenten-Instanzen with welchen zugrundeliegenden Mesh-Modellen aktiviert werden. Das bricht die "Jack-of-all-trades"-Limitation einzelner LLMs on. [1] (https://gurusup.com/blog/moe-vs-multi-agent-systems), [2] (https://medium.com/@sharanharsoor/understanding-mixture-of-experts-moe-the-architecture-powering-next-generation-language-models-49c1d1d467c9), [3] (https://www.mindstudio.ai/blog/multi-agent-orchestration-patterns), [4] (https://a-nikishaev.medium.com/mixture-of-agents-moa-improving-llm-quality-through-multi-agent-collaboration-eb0bcbbdbe9f)Das Design baut on dem bahnbrechenden Mixture-of-Agents (MoA) Ansatz (arXiv:2406.04692) von Together AI on, verfeinert diesen jedoch um agentische Werkzeugnutzung (Tools) and flexible Ausführungsmodi. [1] (https://arxiv.org/abs/2406.04692), [2] (https://docs.together.ai/docs/mixture-of-agents)1. Architecture-Diagramm                           +--------------------+

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
2. Expert Schema (Go-Strukturen)Dieses Datenschema verankert die Experten-Instanzen nativ im OpenMesh Core.gopackage moe

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

// ExpertAgent definiert die Konfiguration and Fähigkeiten eines Spezialisten
type ExpertAgent struct {
	ID           string          `json:"id"`
	Name         string          `json:"name"`
	Type         ExpertType      `json:"type"`
	MeshRouteID  string          `json:"route_id"`      // Verknüpfung zur OpenMesh-Routingklasse (z.B. "smart:coding")
	SystemPrompt string          `json:"system_prompt"` // Rollen-Spezialisierung
	Tools        []string        `json:"tools"`         // Erlaubte CLI/API Werkzeug-IDs
	Enabled      bool            `json:"enabled"`
	CreatedAt    time.Time       `json:"created_at"`
}

// GatingResult hält die Routing-Entscheidung des Gating-Agenten fest
type GatingResult struct {
	SelectedExperts []string `json:"selected_experts"` // IDs der gewählten Experten
	ExecutionMode   string   `json:"mode"`             // "parallel", "sequential", "hybrid"
	Confidence      float64  `json:"confidence"`       // Wert zwischen 0.0 and 1.0
	Reasoning       string   `json:"reasoning"`        // Interne Begründung des Routers
}
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

-- Tabelle for die Protokollierung and das Auditing der Läufe
CREATE TABLE expert_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_description TEXT NOT NULL,
    gating_result JSONB NOT NULL, -- Beinhaltet gewählte IDs, Modus, Confidence
    expert_outputs JSONB NOT NULL, -- JSON-Array with Raw-Outputs and Metriken je Agent
    final_output TEXT NOT NULL,
    tokens_used INT NOT NULL,
    duration_ms INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Initial-Seed for Standard-Experten
INSERT INTO experts (id, name, type, route_id, system_prompt, tools) VALUES
('coder-nemotron', 'NVIDIA Coding Specialist', 'coder', 'smart:coding-free', 'You are an elite software engineer. Output clean, optimal code.', '["file_write"]'),
('reviewer-r1', 'DeepSeek Critic', 'reviewer', 'reasoning:deepseek-r1', 'You are a critical code auditor. Find bugs, edge cases, and security leaks.', '[]'),
('researcher-phi', 'Fast Researcher', 'researcher', 'fast:inline-completion', 'Extract raw facts and document endpoints efficiently.', '["code_search"]');

| 🤖 MIXTURE-OF-EXPERTS AGENT ROUTER                                                |
+-----------------------------------------------------------------------------------+

| Prompt: [ Schreibe einen optimierten Go-Webserver with Rate-Limiting...          ] |
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
