---
id: "R12"
title: "R12 — Agent Browser Control: Utility Model steuert JiMesh Dashboard + Iframes"
type: research
date: 2026-09-06
status: final
tags: [mesh, ssh, playwright, entropy, docker]
license: CC-BY-4.0
---

# R12 — Agent Browser Control: Utility Model steuert JiMesh Dashboard + Iframes

## Die Königsdisziplin
Das utility model und die engine sollen direkt den browser kontrollieren können:
- Dashboard navigieren (tabs, canvas, settings)
- Iframes steuern (DSH chat senden, OpenCode commands, terminal)
- Tasks planen und ausführen über das UI
- Subagents starten, instructor agents koordinieren
- Grenzenlos in einem project arbeiten — gegenseitig kontrollieren

## Recherche-Aufgaben

### 1. Browser Automation Frameworks
- [ ] **Playwright** (Go: playwright-go)
  - Headless + headed mode
  - Can control the JiMesh dashboard itself
  - Can interact with iframes (cross-origin with same-origin tunnel)
  - Click buttons, type text, read DOM state
  - Screenshot for vision models
  - CDP (Chrome DevTools Protocol) integration
- [ ] **Puppeteer** (Node.js only — needs sidecar)
- [ ] **CDP direct** (Chrome DevTools Protocol via WebSocket)
  - Go library: `github.com/chromedp/chromedp`
  - Lower level, more control
  - Can connect to existing browser instance
- [ ] **Selenium/WebDriver** — too heavy, skip
- [ ] Empfehlung: chromedp (Go-native, CDP, connect to existing browser)

### 2. Agent Control Architecture
- [ ] Utility model hat einen "browser tool":
  - `browser_navigate(url)` — navigate to URL
  - `browser_click(selector)` — click element
  - `browser_type(selector, text)` — type text
  - `browser_read(selector)` — read element content
  - `browser_screenshot()` — capture screenshot → vision model
  - `browser_iframe_control(iframe_id, action, ...)` — control iframe content
- [ ] Function calling:
  - Utility model bekommt task → entscheidet welche browser actions nötig
  - Ruft browser tools via function calling
  - Liest results → entscheidet nächste action
  - Loop bis task complete
- [ ] Safety:
  - Whitelist von erlaubten actions (kein delete, keine sensitive settings)
  - Confirmation für destructive actions
  - Audit log: alle browser actions werden geloggt
  - Rate limit: max N actions per minute

### 3. Iframe Control (DSH, OpenCode, Terminal)
- [ ] Problem: iframes sind cross-origin → JS zugriff blockiert
- [ ] Lösung A: SSH tunnel (R11) — Go backend ist same-origin proxy
  - Go backend kann iframe content lesen/schreiben via HTTP
  - Kein browser JS needed — Go macht HTTP requests zum getunnelten target
- [ ] Lösung B: postMessage API
  - JiMesh dashboard ↔ iframe kommunikation via window.postMessage
  - DSH plugin exposet postMessage API (wie R7 DSH plugin)
  - JiMesh sendet commands → DSH plugin führt aus
- [ ] Lösung C: chromedp iframe interaction
  - chromedp kann in iframes navigieren (CDP frame targets)
  - Funktioniert wenn same-origin (via SSH tunnel proxy)
- [ ] Empfehlung: Lösung A (SSH tunnel) für backend control + Lösung B (postMessage) für frontend

### 4. Task Planning + Subagent Coordination
- [ ] Utility model als "orchestrator agent":
  - Bekommt high-level task: "Deploy DSH with mesh routing for my-app"
  - Plant steps: check ports → create deployment → provision mesh → start → verify
  - Führt steps aus via browser tools + API calls
  - Koordiniert subagents (MoE experts) für komplexe sub-tasks
  - Reports progress via SSE
- [ ] Subagent spawning:
  - Utility model kann subagents spawnen (MoE from Sprint 14)
  - Jeder subagent bekommt eine spezifische task
  - Results aggregiert vom utility model
- [ ] Instructor agents:
  - Structured output (JSON schema) für sub-task results
  - Validation + retry on schema mismatch
  - Go structs als schema definition

### 5. Mutual Control (Project ↔ Agent ↔ Dashboard)
- [ ] User kann agent task starten vom dashboard
- [ ] Agent kann dashboard lesen (canvas state, chains, pools)
- [ ] Agent kann dashboard verändern (create pools, add members, deploy)
- [ ] Agent kann andere agents starten (subagent spawning)
- [ ] User kann agent unterbrechen (cancel button)
- [ ] Agent kann user fragen (confirmation dialog via SSE)
- [ ] Bidirectional SSE:
  - Dashboard → Agent: user commands (start, cancel, approve)
  - Agent → Dashboard: progress, results, questions, screenshots

### 6. Integration mit bestehender Architektur
- [ ] Orchestration endpoint (Sprint 13 WP2) erweitern:
  - `POST /api/orchestrate` mit `browser_control: true`
  - Agent bekommt browser tools + API tools
  - Agent kann beide nutzen je nach task
- [ ] MoE experts (Sprint 14) erweitern:
  - Expert type: "browser_operator" — kann browser steuern
  - Expert type: "api_operator" — kann JiMesh API calls machen
  - Expert type: "coder" — kann code schreiben
- [ ] Entropy routing (Sprint 13 WP1):
  - Browser actions brauchen kein entropy routing (deterministic)
  - Code generation braucht entropy routing (uncertain → reasoning model)

### 7. xdg-open Fix (Sidebar Issue)
- [ ] Problem: clicking file paths in DSH chat → `spawn xdg-open ENOENT`
- [ ] Ursache: DSH client versucht xdg-open zu nutzen um dateien zu öffnen
- [ ] Fix optionen:
  - A: xdg-open installieren (`apt install xdg-utils`)
  - B: DSH config: file opener command setzen (`BROWSER=cat` oder custom script)
  - C: JiMesh frontend: file path clicks abfangen → in JiMesh editor öffnen statt xdg-open
  - D: Environment variable setzen im deployment
- [ ] Empfehlung: C (frontend abfangen) + B (fallback config)

## Architecture
```
User (Dashboard)
  ↕ SSE (commands + progress)
Utility Model (Orchestrator Agent)
  ├── Browser Tools (chromedp/CDP)
  │   ├── navigate, click, type, read, screenshot
  │   └── iframe control (via SSH tunnel proxy)
  ├── API Tools (JiMesh REST)
  │   ├── create deployment, provision mesh, start/stop
  │   └── list chains, add members, etc.
  ├── Subagent Spawner (MoE from Sprint 14)
  │   └── spawn coder, reviewer, researcher experts
  └── Planning Engine (task decomposition + step execution)
      ↕ SSH Tunnel (R11)
  Remote Target (iframes: DSH, OpenCode, terminal)
```

## Output Format
1. Browser automation library empfehlung (chromedp vs playwright-go)
2. Agent control API (function calling schema for browser tools)
3. Iframe control strategy (SSH tunnel + postMessage)
4. Task planning + subagent coordination design
5. Mutual control protocol (bidirectional SSE)
6. xdg-open fix

---

Hier ist das vollständige, systemübergreifende Design für das Königsdisziplin-Modul R12 — Agent Browser Control. Dieses Modul verwandelt dein Utility-Modell in einen autonomen Operator, der sowohl die JiMesh-API als auch das UI-Dashboard und dessen eingebettete iFrames manipulieren, koordinieren und überwachen kann.1. Browser Automation Library EmpfehlungFür ein hochperformantes Go-basiertes Ökosystem lautet die klare Empfehlung: github.com/chromedp/chromedp.Begründung:Go-Native & Zero-Dependency: Im Gegensatz zu playwright-go (welches im Hintergrund Node.js-Treiber und schwere Binaries nachlädt) kommuniziert chromedp direkt über native Go-Kanäle mit dem Chrome DevTools Protocol (CDP) via WebSockets.Anbindung an bestehende Sessions: chromedp kann sich an eine bereits geöffnete, headless oder headed Browser-Instanz hängen (Remote Allocator). Das Utility-Modell operiert somit im exakt gleichen Context wie der menschliche User.Low-Level Frame Manipulation: CDP erlaubt das direkte Injizieren von JS-Code in isolierte iFrame-Targets, selbst wenn diese über Cross-Origin-Barrieren geschützt sind.2. Agent Control API (Function Calling Schema)Das Utility-Modell steuert den Browser deklarativ über standardisierte JSON-Schemas via Function Calling. Hier sind die drei wichtigsten Werkzeuge des Operators:browser_navigatejson{
  "name": "browser_navigate",
  "description": "Navigates the browser instance to a specific path within the JiMesh dashboard.",
  "parameters": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "example": "http://localhost:9090/projects/proj-abc/canvas" }
    },
    "required": ["url"]
    }
}
browser_clickjson{
  "name": "browser_click",
  "description": "Clicks a DOM element inside the dashboard or main viewport identified by a CSS selector.",
  "parameters": {
    "type": "object",
    "properties": {
      "selector": { "type": "string", "example": "button[data-testid='deploy-btn']" },
      "wait_for_timeout_ms": { "type": "integer", "default": 500 }
    },
    "required": ["selector"]
  }
}
browser_iframe_controljson{
  "name": "browser_iframe_control",
  "description": "Injects an action or string command directly into a specific embedded sub-workspace/iframe (DSH, OpenCode, Terminal).",
  "parameters": {
    "type": "object",
    "properties": {
      "iframe_id": { "type": "string", "enum": ["dsh-chat", "opencode-editor", "web-terminal"] },
      "action": { "type": "string", "enum": ["send_message", "execute_cmd", "read_buffer"] },
      "payload": { "type": "string", "description": "The text, command, or prompt to inject." }
    },
    "required": ["iframe_id", "action", "payload"]
  }
}
3. Iframe Control Strategy (The Same-Origin Bridge)Da iFrames im Browser-DOM standardmäßig der Same-Origin-Policy (SOP) unterliegen, nutzen wir eine duale Architektur, um dem Agenten vollen Lese- und Schreibzugriff zu gewähren:Backend-Ebene (Der SSH-Proxy Tunnel): Wie in R11 definiert, laufen alle iFrame-Assets durch den JiMesh Go Core Proxy. Dadurch nimmt der Browser alle iFrames als Same-Origin (localhost:9090) wahr. chromedp kann somit ohne Sicherheitsblockaden direkt in den DOM-Tree der iFrames (cdp.WithTargetID) eintauchen, um Terminal-Inputs zu simulieren oder Chat-Antworten zu lesen.Frontend-Ebene (Die postMessage API): Für schnelle, nicht-destruktive Interaktionen (z. B. "Bewege den Cursor im Editor auf Zeile 10") nutzt das Dashboard eine deklarative Event-Brücke. Der Go-Core triggert ein Event im Dashboard, welches via window.postMessage an das DSH- oder OpenCode-iFrame gereicht wird.4. Task Planning + Subagent Coordination DesignWenn der Haupt-Orchestrator (Utility Modell) einen komplexen Befehl erhält, erzeugt er eine hierarchische Ausführungskette (Hierarchical Agentic Workflow):                       [ High-Level User Task ]
                                  │
                                  ▼
                     ┌──────────────────────────┐
                     │ Utility Model            │
                     │ (Orchestrator/Planner)   │
                     └────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Browser Operator │    │ API Operator     │    │ MoE Code Expert  │
│ (chromedp Click) │    │ (REST Trigger)   │    │ (Reasoning/R6)   │
└──────────────────┘    └──────────────────┘    └──────────────────┘
Deterministische vs. Kognitive Tasks: Das System splittet die Pipeline auf. UI-Interaktionen (Klicken, Navigieren) sind deterministisch und erfordern kein teures Reasoning. Die Inhaltserstellung (Code-Generierung) wird sofort an die MoE Expert Engine (R6) eskaliert.Instructor Validation (Structured Outputs): Ergebnisse von Sub-Agenten werden zwingend über Go-Struct-Validatoren geschleift. Liefert ein Sub-Agent Code im falschen Format, triggert der Haupt-Orchestrator autark eine Self-Correction-Schleife (max. 3 Retries), bevor der Schritt im UI als "erfolgreich" markiert wird.5. Mutual Control Protocol (Bidirektionales SSE)Die Interaktion zwischen Mensch und Maschine läuft über einen langlebigen Vollduplex-Kommunikationskanal, gesteuert via Server-Sent Events (SSE) und HTTP-POST Mutationen.📡 Event Ströme (Agent ──► Dashboard UI):event: agent_status -> data: { "step": "Analyzing Canvas state...", "progress": 20 }event: agent_screenshot -> data: { "b64_img": "iVBORw0KG..." } (Ermöglicht dem User Live-Monitoring des headless Browsers).event: agent_question -> data: { "type": "confirm_destructive", "message": "Agent wants to deploy project B which will auto-stop project A. Approve?" }📥 Interrupts (User ──► Agent Core):Klickt der User auf [ CANCEL ], sendet das UI ein POST /api/orchestrate/cancel. Der Go-Core bricht den aktuellen context.WithCancel des chromedp-Laufs sofort ab, schließt den virtuellen Browser-Tab und versetzt die Agenten-Engine in den Ruhezustand.6. xdg-open Fix (Sidebar Issue)Ursache:Klickt man im DSH-Chat auf einen Dateipfad, versucht der unmodifizierte DSH-Core-Code, das System-Utility xdg-open aufzurufen, um die Datei im Host-OS anzuzeigen. Da DSH jedoch isoliert im Docker-Container läuft, schlägt der Prozess mit spawn xdg-open ENOENT fehl.🛠️ Die duale Behebungs-Strategie:Lösung 1 (Frontend Interception - Primär):Im DSH-Frontend-Plugin (R7) klinken wir uns in den Click-Handler von Dateilink-Komponenten ein:typescript// client/index.tsx
window.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;
  if (target.matches('.dsh-file-link')) {
    e.preventDefault();
    const filePath = target.getAttribute('data-path');
    // Sende Event an das Haupt-Dashboard, um die Datei nativ im JiMesh-Editor zu öffnen
    window.parent.postMessage({ type: 'JIMESH_OPEN_FILE', path: filePath }, '*');
  }
});
Lösung 2 (Environment Fallback - Server-Side Shell Wrapper):Für CLI-Tools, die blind auf xdg-open vertrauen, legen wir während des E2E-Deployments (R11) ein leichtgewichtiges Mock-Skript im Container-Pfad /usr/local/bin/xdg-open ab:bash#!/bin/bash
# xdg-open Mock-Skript im Container
# Sendet den Pfad per cURL an den lokalen JiMesh-Proxy statt ein Host-Fenster zu öffnen
curl -X POST -H "Content-Type: application/json" \
     -d "{\"path\":\"$1\"}" \
     http://localhost:9091/api/projects/active/open-in-editor
Möchtest du als Nächstes die Go-Implementierung des chromedp-Tasks sehen, der einen vollwertigen iFrame-Klick inkl. Target-Fokus ausführt, oder sollen wir das vollständige JSON-Schema für das bidirektionale Bestätigungsprotokoll (SSE-Questions) spezifizieren?