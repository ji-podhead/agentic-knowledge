---
okf_version: "1.0"
id: "okf-llm-age-r7-dsh-plugin-orchestration"
title: "R7 — DeepSeek Harness Plugin: Orchestration Mode Architecture"
topic: "llm-routing-and-orchestration"
subtopic: "agent-architectures"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-routing-and-orchestration
  - agent-architectures
summary: "Wie bauen wir ein DSH (DeepSeek Harness) plugin das OpenMesh mesh routes für agent"
---

# R7 — DeepSeek Harness Plugin: Orchestration Mode Architecture

## Question
Wie bauen wir ein DSH (DeepSeek Harness) plugin das OpenMesh mesh routes for agent
roles nutzt? Wie sieht die plugin architektur from?

## Research Tasks

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
- [ ] Auth: wie authentifiziert sich DSH gegen OpenMesh?
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
- [ ] Dependencies: darf das plugin OpenMesh API client nutzen?
- [ ] Build: muss das plugin with DSH gebaut werden or zur laufzeit geladen?
- [ ] Config: plugin settings (OpenMesh URL, token, default routes)

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

Hier ist die vollständige Systemarchitektur and Implementierungsspezifikation for das DSH (DeepSeek Harness) Orchestration Mode Plugin, das deine OpenMesh Mesh Routes nativ in den Agenten-Workflow einbindet.1. DSH Plugin-ArchitekturdiagrammDas DSH-Plugin-System nutzt eine Hybrid-Architecture. Der Client-Teil injiziert sich in die React/Vue-App von DSH (Frontend-Hooks), während der Server-Teil Express/Fastify-Routen im DSH-Node-Core registriert, um als Proxy zum Go-basierten OpenMesh-Core zu agieren.+-----------------------------------------------------------------------------+

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

                                              |       OpenMesh Go Core       |
                                              |                            |
                                              |  [ Orchestrator / Engine ] |
                                              +----------------------------+
2. Plugin Dateistruktur (Tree)DSH lädt Plugins dynamisch zur Laufzeit from dem Verzeichnis /usr/local/lib/node_modules/@deepseek-ai/dsh/plugins/ (or einem konfigurierten Custom-Pfad).textdsh-plugin-openmesh-orchestration/
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
│           └── openmeshClient.ts
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
data: { "run_id": "a9b8c7-...", "classification": "coding", "sub_tasks": ["write_server", "audit_code"], "routes": { "coder": "smart:coding-free", "reviewer": "reasoning:deepseek-r1" } }

event: expert_start
data: { "expert": "coder-nemotron", "route": "smart:coding-free", "timestamp": 1717545601 }

event: expert_output
data: { "expert": "coder-nemotron", "chunk": "package main\n\nimport (\n\t\"net/http\"\n)" }

event: expert_done
data: { "expert": "coder-nemotron", "tokens": 420, "latency_ms": 1850 }

event: complete
data: { "final_output": "...", "experts_used": ["coder-nemotron", "reviewer-r1"], "total_tokens": 1150, "total_cost_usd": 0.0023 }
  "type": "object",
  "properties": {
    "openmesh_url": {
      "type": "string",
      "format": "uri",
      "default": "http://localhost:9091"
    },
    "openmesh_api_key": {
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
  "required": ["openmesh_url", "openmesh_api_key"]
}
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
