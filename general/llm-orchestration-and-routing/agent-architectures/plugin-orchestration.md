---
okf_version: "1.0"
id: "okf-llm-age-plugin-orchestration"
title: "R7 — DeepSeek Harness Plugin: Orchestration Mode Architecture"
topic: "general/llm-orchestration-and-routing"
subtopic: "agent-architectures"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-orchestration-and-routing
  - agent-architectures
summary: "Wie bauen wir ein DSH (DeepSeek Harness) plugin das The Multi-Provider Gateway mesh routes for agent"
---

# R7 — DeepSeek Harness Plugin: Orchestration Mode Architecture

## Architectural Question
Wie bauen wir ein DSH (DeepSeek Harness) plugin das The Multi-Provider Gateway mesh routes for agent
roles nutzt? Wie sieht die plugin architektur from?

## Research Objectives

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
  - Plan display: welche experts/models for welche sub-tasks
  - Execution progress: live SSE updates
  - Results panel: aggregated + per-expert attribution
  - History: previous orchestration runs

### 3. Mesh Route Integration
- [ ] Wie liest das plugin die mesh routes?
  - `GET /api/chains` → liste aller chains
  - `GET /api/chains/{id}/graph` → nodes + members
  - Plugin cached routes or fresh fetch?
- [ ] Route selection im plugin:
  - User kann route per dropdown wählen
  - Oder: orchestration mode auto-selects basierend on task type
  - Rolle → route mapping: planner→fast pool, coder→coding pool, etc.
- [ ] Auth: wie authentifiziert sich DSH gegen The Multi-Provider Gateway?
  - Deploy token? API key? Session cookie?
  - Brauchen wir einen neuen auth mechanism for plugins?

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
- [ ] Dependencies: darf das plugin The Multi-Provider Gateway API client nutzen?
- [ ] Build: muss das plugin with DSH gebaut werden or zur laufzeit geladen?
- [ ] Config: plugin settings (The Multi-Provider Gateway URL, token, default routes)

### 6. Security & Isolation
- [ ] Plugin läuft in DSH context — hat es access zum filesystem?
- [ ] Brauchen wir sandbox for plugin code execution?
- [ ] Rate limiting: orchestration kann viele LLM calls auslösen — limit?
- [ ] Cost tracking: pro orchestration run → total tokens × cost

## Output Format
1. DSH plugin architecture diagram
2. Plugin file structure (tree)
3. Orchestration API spec (request/response schema)
4. SSE event schema
5. Plugin config schema
6. Auth mechanism empfehlung
7. Build/load mechanism

---

Hier ist die vollständige Systemarchitektur and Implementierungsspezifikation for das DSH (DeepSeek Harness) Orchestration Mode Plugin, das deine The Multi-Provider Gateway Mesh Routes nativ in den Agenten-Workflow einbindet.1. DSH Plugin-ArchitekturdiagrammDas DSH-Plugin-System nutzt eine Hybrid-Architektur. Der Client-Teil injiziert sich in die React/Vue-App von DSH (Frontend-Hooks), während der Server-Teil Express/Fastify-Routen im DSH-Node-Core registriert, um als Proxy zum Go-basierten The Multi-Provider Gateway-Core zu agieren.+-----------------------------------------------------------------------------+

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

                                              |       The Multi-Provider Gateway Go Core       |
                                              |                            |
                                              |  [ Orchestrator / Engine ] |
                                              +----------------------------+
2. Plugin Dateistruktur (Tree)DSH lädt Plugins dynamisch zur Laufzeit from dem Verzeichnis /usr/local/lib/node_modules/@deepseek-ai/dsh/plugins/ (or einem konfigurierten Custom-Pfad).textdsh-plugin-llm-mesh-gateway-orchestration/
├── package.json
├── tsconfig.json
├── vite.config.ts          # Bundelt das Frontend-Asset als ESM-Modul
├── config.schema.json      # Deklarative Konfigurationsvorgaben for DSH
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
│           └── meshClient.ts
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
Response / Cancel HTTP Status CodesPOST /api/orchestrate -> 200 OK with Header Content-Type: text/event-stream (Initiiert SSE).POST /api/orchestrate/cancel -> 202 Accepted { "status": "canceling", "active_run_id": "uuid" } (Sendet Abbruchsignal an The Multi-Provider Gateway).4. SSE (Server-Sent Events) SchemaDer Stream versorgt das DSH Frontend in Echtzeit with Fortschrittsdaten:developmentevent: plan
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
    "gateway_url": {
      "type": "string",
      "format": "uri",
      "default": "http://localhost:9091"
    },
    "gateway_api_key": {
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
  "required": ["gateway_url", "gateway_api_key"]
}
6. Empfohlener AuthentifizierungsmechanismusNutze einen dedizierten, kryptografisch sicheren Pre-Shared Bearer Key (The Multi-Provider Gateway Deploy Token) in Kombination with einer erzwungenen TLS-Validierung zwischen DSH and The Multi-Provider Gateway.Vorgehen:Im The Multi-Provider Gateway Core wird ein Token with eingeschränkten ACL-Rechten generiert (token_scope: ["orchestrate", "chains:read"]).Das DSH-Plugin speichert dieses Token verschlüsselt in den DSH-System-Settings ab.Jeder API-Aufruf des Plugins injiziert den Header Authorization: Bearer jm_live_tkn_.... Da das Plugin im DSH-Node-Backend läuft, bleibt das Token before Endbenutzern im Browser vollständig verborgen (no Leak about Client-Side Network-Inspectors).7. Build- and Lade-Mechanismus (Build & Load)Kompilierung: Das Plugin wird als eigenständiges Projekt via Vite + esbuild vorkompiliert. Das Frontend wird in ein einzelnes, hochoptimiertes ESM-Modul (client.js) kompiliert, das serverseitige Backend in ein Node-kompatibles CJS/ESM-Modul (index.js).Manifest-Registrierung: DSH scannt beim Start sein Plugin-Verzeichnis. Über eine standardisierte Export-Struktur meldet sich das Plugin beim Core an:typescript// server entrypoint index.ts
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
Laufzeit-Isolation: Während der Client direkten Zugriff on den DOM-Tree des Chat-Fensters erhält, um die UI zu rendern, wird der Backend-Part about DSH-interne Express-Middlewares bezüglich Dateisystemzugriffen restriktiv isoliert.Möchtest du als Nächstes die React-Implementation der OrchestrationPanel-Komponente sehen, die den SSE-Datenstrom live visualisiert, or sollen wir den Node.js-Controller schreiben, welcher die SSE-Events formatiert and an den Client pusht?
