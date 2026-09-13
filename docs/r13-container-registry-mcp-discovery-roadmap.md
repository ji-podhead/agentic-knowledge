---
id: "R13"
title: "R13 — Container Registry + MCP + Auto-Discovery + Tool Registry + Roadmap Graph"
type: research
date: 2026-09-06
status: final
tags: [docker, mcp, mesh, redis, ssh]
license: CC-BY-4.0
---

# R13 — Container Registry + MCP + Auto-Discovery + Tool Registry + Roadmap Graph

## Vision
Agents und Humans arbeiten grenzenlos in einem Project:
- Agent öffnet shells, deployed crews (DSH SDK, CrewAI, Python)
- Container/Environments werden einmal composed → registry → wiederverwendet
- Auto-discovery: laufende apps/container werden als deployments + agent tools erkannt
- User deployed Adminer, Datenbanken, eigene container → automatisch agents zur Verfügung
- Project roadmap wird grafisch dargestellt (graph), user wählt sidebar items
- Dev-icons / react-icons für professionelles UI

## Recherche-Aufgaben

### 1. Container/Environment Registry
- [ ] Problem: jedes deployment baut env neu → langsam, redundant
- [ ] Lösung: Environment Registry
  - User compoed ein environment (base image + packages + config)
  - Speichert als template in DB: `environment_templates` table
  - `POST /api/environments` — create template (name, base_image, packages, config)
  - `GET /api/environments` — list templates
  - Deploy = instantiate template (docker build from template → container)
  - Versioning: template v1, v2, rollback
- [ ] Pre-built templates:
  - "Python + CrewAI" (python:3.12 + crewai + pip)
  - "Go + DSH SDK" (golang + dsh-sdk + protoc)
  - "Node + Claude Code" (node:20 + @anthropic-ai/claude-code)
  - "Terminal minimal" (alpine + bash + git + curl)
  - "Database admin" (adminer + php + mysql client)
- [ ] Agent kann template erstellen:
  - Utility model: "I need Python 3.12 with CrewAI for this task"
  - Creates environment template → instantiates → runs crew → destroys
- [ ] Docker library:
  - Go: `github.com/docker/docker/client` — Docker API client
  - Create container, start, stop, exec, logs, remove
  - Volume management for persistent environments

### 2. MCP (Model Context Protocol) Integration
- [ ] Was ist MCP?
  - Standard protocol for LLM ↔ tools/services communication
  - Anthropic's protocol: resources, prompts, tools
  - Server exposes tools, client (LLM) calls them
- [ ] JiMesh als MCP Server:
  - Exposes JiMesh API as MCP tools: deploy, provision, list chains, etc.
  - Agents (DSH, Claude Code) connect to JiMesh MCP server
  - Agent kann: `jimesh.deploy()`, `jimesh.provision()`, `jimesh.list_chains()`
- [ ] JiMesh als MCP Client:
  - JiMesh utility agent kann andere MCP server nutzen
  - z.B. MCP server für filesystem, database, shell
  - Agent: "use filesystem MCP to read files, use jimesh MCP to deploy"
- [ ] MCP tools für agents:
  - `shell_exec(container, command)` — execute in container via SSH/docker exec
  - `crew_spawn(template, task)` — spawn a CrewAI crew in a container
  - `db_query(connection, query)` — query a database
  - `docker_create(image, env)` — create a new container
  - `e2e_deploy(project, type, path)` — full E2E deployment
- [ ] Implementation:
  - Go MCP server: `github.com/mark3labs/mcp-go` or custom
  - JSON-RPC over stdio or HTTP+SSE

### 3. Auto-Discovery (Container + Apps → Deployments + Tools)
- [ ] Scan running containers:
  - Docker API: `docker ps` → list running containers
  - Parse: image name, ports, labels, status
  - Auto-register as deployment: `POST /api/projects/{id}/deployments` (auto-discovered)
  - Mark as `auto_discovered: true`
- [ ] Scan open ports (R11 port detection):
  - SSH: `ss -tlnp` → open ports + process names
  - Match to known patterns: 8080=web, 3306=mysql, 5432=postgres, 6379=redis
  - Auto-create deployment entries
- [ ] App discovery:
  - Scan for: docker-compose.yml, Dockerfile, package.json, go.mod, requirements.txt
  - In known paths: ~/, ~/projects, /opt
  - Via SSH: `find ~/projects -maxdepth 2 -name "docker-compose.yml"`
  - Register as "discovered project" → user can promote to deployment
- [ ] Auto-tool registration:
  - Discovered database (port 5432) → register as `db_query` tool for agents
  - Discovered adminer (port 8080) → register as `browser_navigate` target
  - Discovered redis (port 6379) → register as `cache_get/set` tool
- [ ] UI: "Network Discovery" tab
  - Graph view of all discovered services + connections
  - Click service → details (ports, image, status, health)
  - "Promote to Deployment" button
  - "Add as Agent Tool" button

### 4. Agent Tool Registry
- [ ] Agents brauchen tools: shells, databases, E2E, docker API, browser, etc.
- [ ] Tool registry:
  - `agent_tools` table: id, name, type, config (JSONB), enabled, source
  - Types: shell, database, docker, browser, api, filesystem, custom
  - Auto-registered from discovery (R3 above)
  - Manually registered by user
  - Each tool has a config schema → frontend form generator
- [ ] Built-in tools:
  - `shell_exec` — execute command in container/SSH
  - `db_query` — query database (postgres/mysql/redis)
  - `docker_create` — create container
  - `docker_logs` — tail container logs
  - `e2e_deploy` — full deployment via templates
  - `browser_navigate` — browser automation (R12)
  - `jimesh_api` — JiMesh REST API access
  - `filesystem` — read/write files (SSH or local)
- [ ] Agent tool selection:
  - Utility model (orchestrator) knows available tools
  - Selects appropriate tool for each step
  - Tools exposed via MCP or function calling

### 5. Project Roadmap Visualization
- [ ] Graph view:
  - Nodes: projects, deployments, chains, environments, discovered services
  - Edges: dependencies (project → deployment → chain → models)
  - Interactive: click node → details panel
  - Filter: by type, status, category
- [ ] React Flow (bereits in JiMesh frontend):
  - Wiederverwendung der existing canvas
  - New "Roadmap" view: project graph instead of chain graph
  - Auto-layout: dagre or ELK.js
- [ ] Sidebar customization:
  - User wählt welche projects/deployments in der sidebar sind
  - `project_sidebar_items` table: user_id, project_id, order
  - Andere items sichtbar im graph aber nicht in sidebar
- [ ] Tabs:
  - "Mesh Canvas" (existing — chains/pools/edges)
  - "Projects" (project graph — deployments/dependencies)
  - "Discovery" (auto-discovered services graph)
  - "Agents" (expert registry + runs)

### 6. Icon System (dev-icons / react-icons)
- [ ] **react-icons** (`react-icons` npm package):
  - Includes: FaDocker, FaPython, SiGo, SiTypescript, SiPostgresql, SiRedis
  - Simple Icons set (Si*): brands, technologies, languages
  - Font Awesome (Fa*): general UI icons
  - Lucide (already used in JiMesh): UI icons
- [ ] **devicons** (`@devicons/core` or `devicons-react`):
  - Technology-specific icons (Go, Python, Docker, PostgreSQL, Redis, Node)
  - Colored versions
- [ ] Usage in JiMesh:
  - Deployment cards: icon based on type (Docker=FaDocker, DSH=Cpu, Claude=SiAnthropic)
  - Environment templates: icon based on base image
  - Discovered services: icon based on detected type
  - Agent tools: icon based on tool type
- [ ] Mapping table:
  | Type | Icon | Package |
  |---|---|---|
  | Docker | FaDocker | react-icons/fa |
  | Python | FaPython | react-icons/fa |
  | Go | SiGo | react-icons/si |
  | TypeScript | SiTypescript | react-icons/si |
  | PostgreSQL | SiPostgresql | react-icons/si |
  | Redis | SiRedis | react-icons/si |
  | Node.js | SiNodedotjs | react-icons/si |
  | DSH | Cpu | lucide-react |
  | Claude Code | SiAnthropic | react-icons/si (custom fallback) |
  | Terminal | Terminal | lucide-react |
  | Adminer | SiPhp | react-icons/si |
  | CrewAI | SiPython | react-icons/si |
  | MCP | Network | lucide-react |

### 7. Was fehlt zur Vision?
- [ ] **Multi-user / Team**: mehrere user auf einer JiMesh instance
  - RBAC, project ownership, shared deployments
  - Agent runs scoped to user
- [ ] **GitOps**: deployments aus git repo → auto-deploy on push
  - Webhook → JiMesh pulls → rebuilds → redeploys
- [ ] **Cost tracking per project**: tokens × cost → budget alerts
  - Per project, per deployment, per agent run
  - Dashboard widget
- [ ] **Audit trail**: who (human or agent) did what when
  - All actions logged: deployment changes, config edits, agent runs
  - Searchable, exportable
- [ ] **Secret management**: API keys, SSH keys, DB passwords
  - Encrypted in DB
  - Vault integration (optional)
  - Agent tools can access secrets via MCP with permission
- [ ] **Backup/Restore**: project + deployment config backup
  - Already have export/import (Sprint 11) — extend to environments + tools
- [ ] **Plugin marketplace**: community plugins for JiMesh
  - Custom connectors, tools, environment templates
  - Install via npm/git

## Output Format
1. Container/environment registry design (DB schema, templates, API)
2. MCP integration architecture (server + client, tool schema)
3. Auto-discovery flow (docker ps + port scan → register → agent tools)
4. Agent tool registry schema
5. Project roadmap graph view (React Flow, tabs, sidebar customization)
6. Icon mapping table (react-icons)
7. Vision gap analysis (multi-user, GitOps, cost, audit, secrets, plugins)

---

Die JiMesh R13 Core-Architektur vereint Container-Laufzeiten auf dem Zielsystem, standardisiert die Agenten-Werkzeugausführung über das Model Context Protocol (MCP) und führt eine autonome Network Auto-Discovery ein. Dadurch entsteht eine grenzenlose Sandbox, in der menschliche Entwickler und KI-Agenten denselben Workspace manipulieren, orchestrieren und überwachen können.1. Container / Environment Registry (Docker Go SDK)Um redundante Build-Zeiten zu eliminieren, entkoppelt R13 die Definition von Laufzeiten von den konkreten Deployments. Über das offizielle Go Docker SDK (github.com/docker/docker/client) verwaltet der JiMesh-Core ein transientes Image-Management.Environment Templates: Kompositionen (z. B. golang + dsh-sdk) werden als Rezepte in PostgreSQL hinterlegt.Agentic Instantiation: Erkennt das Utility-Modell, dass für eine Teilaufgabe eine isolierte Python-Umgebung benötigt wird, triggert es über das SDK einen unbenannten Container, führt die CrewAI-Crew aus, persistiert Ergebnisse in einem geteilten Docker-Volume und zerstört die Instanz automatisch.go// Database Schema für wiederverwendbare Umgebungen
type EnvironmentTemplate struct {
	ID        string          `json:"id" db:"id"`
	Name      string          `json:"name" db:"name"`
	BaseImage string          `json:"base_image" db:"base_image"`
	Packages  []string        `json:"packages" db:"packages"` // ["pip install crewai", "apt install curl"]
	Config    json.RawMessage `json:"config" db:"config"`     // Volumes, Envs, Limits
	Version   int             `json:"version" db:"version"`
}
2. MCP (Model Context Protocol) IntegrationJiMesh implementiert das von Anthropic spezifizierte Model Context Protocol (MCP) über JSON-RPC transportiert via stdio/SSE unter Verwendung von github.com/mark3labs/mcp-go [2601.13671].┌──────────────────────────────────────┐
│  AI Agent (Claude Code / DSH SDK)    │
└──────────────────┬───────────────────┘
                   │
                   ▼ MCP Client Protocol (JSON-RPC)
┌──────────────────────────────────────────────────────┐
│  JiMesh Go Core (MCP Server Role)                    │
│  ├─ Tool: jimesh.deploy(project_id, layer_config)    │
│  ├─ Tool: jimesh.provision_mesh(chain_id, port)      │
│  └─ Tool: shell_exec(container_id, command)          │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼ MCP Server Protocol (Downstream Gateway)
┌──────────────────────────────────────────────────────┐
│  External MCP Servers (Filesystem, Postgres-DB)      │
└──────────────────────────────────────────────────────┘
JiMesh als MCP Server: Exponiert den gesamten Core-Funktionsumfang an externe Agenten-CLIs. Claude Code kann nativ über MCP-Befehle Infrastruktur-Deployments auf dem Host anfordern.JiMesh als MCP Client: Das interne Utility-Modell nutzt spezialisierte Host-MCP-Server (z. B. für sicheren Dateisystem-Zugriff), um Dateioperationen standardisiert zu bündeln.3. Auto-Discovery PipelineDer Go-Core führt im Hintergrund eine kontinuierliche Kaskaden-Erkennung über die Docker-Socket-API und SSH-Sitzungen aus, um Schatten-Infrastrukturen automatisiert zu erfassen.Container Scan: Liest docker ps aus und analysiert Labels und Ports.Port-to-Process Matching: Kombiniert SSH ss -tlnp (R11), um offene Sockets bekannten Mustern zuzuordnen (z. B. Port 5432 = PostgreSQL).Workspace Crawling: Sucht im Remote-Dateisystem nach Mustern wie docker-compose.yml, package.json oder go.mod.Promotion Workflow: Entdeckte Services werden im Dashboard unter dem Tab "Network Discovery" visualisiert. Mit einem Klick befördert der User diese zu einem offiziellen Dashboard-Deployment oder registriert sie direkt als Live-Werkzeug für Agenten.4. Agent Tool Registry DesignDie Tool Registry ist das Bindeglied, über das Agenten wissen, welche Fähigkeiten im Cluster aktiv sind.sqlCREATE TABLE agent_tools (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(32) NOT NULL, -- 'shell', 'database', 'browser', 'filesystem'
    config JSONB NOT NULL DEFAULT '{}'::jsonb, -- Verbindungsdaten, Ports, Container-IDs
    enabled BOOLEAN DEFAULT TRUE,
    auto_discovered BOOLEAN DEFAULT FALSE,
    config_schema JSONB NOT NULL -- Erzeugt dynamisch die UI-Eingabemaske im Frontend
);
Built-in Tools: shell_exec (führt isolierte Befehle via Docker-Exec aus), db_query (führt SQL-Befehle direkt auf auto-entdeckten Datenbanken aus), browser_navigate (steuert die R12-Chromedp-Instanz).5. Project Roadmap Visualization (React Flow Canvas)Das bestehende Canvas-System wird um eine makroskopische Roadmap-Ansicht erweitert, um Abhängigkeiten visuell aufzulösen.Node-Typen: project (blau), deployment (grün), mesh_chain (indigo), discovered_service (grau, gestrichelt).Edge-Typen: Gerichtete Linien definieren funktionale Abhängigkeiten (z. B. Deployment X benötigt Database Y).Sidebar-State: Die Tabellenstruktur project_sidebar_items speichert benutzerspezifisch, welche Knoten als Schnellzugriff permanent in der linken Navigation verankert sind, während komplexe Graphen-Cluster auf das Haupt-Canvas ausgelagert werden.6. Developer Icon Mapping-MatrixUm dem Dashboard eine professionelle visuelle Identität zu geben, werden Technologien über ein dediziertes UI-Mapping-System mit nativen Markenfarben gerendert.Deployment / Tool TypIcon KomponenteNPM PackageVisueller Kontext / FarbeDocker / ComposeFaDockerreact-icons/fa#2496ED (Docker Blau)Python RuntimesFaPythonreact-icons/fa#3776AB (Python Gelb/Blau)Go BinariesSiGoreact-icons/si#00ADD8 (Gopher Cyan)PostgreSQLSiPostgresqlreact-icons/si#4169E1 (Elephant Blau)Redis CacheSiRedisreact-icons/si#DC382D (Redis Rot)Node.js EnvironmentSiNodedotjsreact-icons/si#339933 (Node Grün)Claude Code CLISiAnthropicreact-icons/si#D97706 (Clay Orange Fallback)Model Context ProtocolLuNetworklucide-react#94A3B8 (Slate Grey Mesh-Knoten)DeepSeek Harness (DSH)LuCpulucide-react#3B82F6 (DeepSeek Elektro-Blau)7. Was fehlt zur ultimativen Vision? (Gaps & Next Milestones)Multi-User Isolation (RBAC): Scoping von Agenten-Ausführungen auf Benutzerebene, um zu verhindern, dass ein Sub-Agent von User A die Infrastruktur von User B modifiziert.GitOps-Schnittstelle: Ein interner Webhook-Listener im Go-Core, der bei einem git push auf das Ziel-Repository automatisiert Container-Rebuilds und iFrame-Cache-Invalidierungen auslöst.Echtzeit-Token-Budgetierung: Ein In-Memory-Kosten-Aggregator im Proxy, der bei Überschreiten eines projektspezifischen Dollar-Limits (z. B. 0.50 $ pro MoE-Lauf) harte Abbruch-Signale (context.Cancel) an alle MCP-Tools sendet.Kryptografischer Secret-Vault: Integration einer AES-GCM-256 Verschlüsselungsschicht für API-Schlüssel direkt in der PostgreSQL-Datenbank, auf die Agenten-Tools nur nach expliziter Bestätigung im UI (R12-SSE-Question) Zugriff erhalten.Sollen wir für das anstehende Implementierungsmodul den vollständigen Go-Code für den MCP-Server (github.com/mark3labs/mcp-go) inklusive des shell_exec-Werkzeugs schreiben, oder möchtest du das React-Flow Komponenten-Mapping für den neuen Roadmap-Graph-Tab entwerfen?