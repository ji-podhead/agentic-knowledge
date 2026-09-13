---
okf_version: "1.0"
id: "okf-con-mcp-r13-container-registry-mcp-discovery-roadmap"
title: "R13 — Container Registry + MCP + Auto-Discovery + Tool Registry + Roadmap Graph"
topic: "container-and-runtime-security"
subtopic: "mcp-integrations"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - container-and-runtime-security
  - mcp-integrations
summary: "Agents und Humans arbeiten grenzenlos in einem Project:"
---

# R13 — Container Registry + MCP + Auto-Discovery + Tool Registry + Roadmap Graph

## Vision
Agents and Humans arbeiten grenzenlos in einem Project:
- Agent öffnet shells, deployed crews (DSH SDK, CrewAI, Python)
- Container/Environments werden einmal composed → registry → wiederverwendet
- Auto-discovery: laufende apps/container werden als deployments + agent tools erkannt
- User deployed Adminer, Datenbanken, eigene container → automatisch agents zur Verfügung
- Project roadmap wird grafisch dargestellt (graph), user wählt sidebar items
- Dev-icons / react-icons for professionelles UI

## Research Tasks

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
- [ ] OpenMesh als MCP Server:
  - Exposes OpenMesh API as MCP tools: deploy, provision, list chains, etc.
  - Agents (DSH, Claude Code) connect to OpenMesh MCP server
  - Agent kann: `openmesh.deploy()`, `openmesh.provision()`, `openmesh.list_chains()`
- [ ] OpenMesh als MCP Client:
  - OpenMesh utility agent kann andere MCP server nutzen
  - z.B. MCP server for filesystem, database, shell
  - Agent: "use filesystem MCP to read files, use openmesh MCP to deploy"
- [ ] MCP tools for agents:
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
  - `openmesh_api` — OpenMesh REST API access
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
- [ ] React Flow (bereits in OpenMesh frontend):
  - Wiederverwendung der existing canvas
  - New "Roadmap" view: project graph instead of chain graph
  - Auto-layout: dagre or ELK.js
- [ ] Sidebar customization:
  - User wählt welche projects/deployments in der sidebar sind
  - `project_sidebar_items` table: user_id, project_id, order
  - Andere items sichtbar im graph aber not in sidebar
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
  - Lucide (already used in OpenMesh): UI icons
- [ ] **devicons** (`@devicons/core` or `devicons-react`):
  - Technology-specific icons (Go, Python, Docker, PostgreSQL, Redis, Node)
  - Colored versions
- [ ] Usage in OpenMesh:
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
- [ ] **Multi-user / Team**: mehrere user on einer OpenMesh instance
  - RBAC, project ownership, shared deployments
  - Agent runs scoped to user
- [ ] **GitOps**: deployments from git repo → auto-deploy on push
  - Webhook → OpenMesh pulls → rebuilds → redeploys
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
- [ ] **Plugin marketplace**: community plugins for OpenMesh
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

Die OpenMesh R13 Core-Architecture vereint Container-Laufzeiten on dem Zielsystem, standardisiert die Agenten-Werkzeugausführung about das Model Context Protocol (MCP) and führt eine autonome Network Auto-Discovery ein. Dadurch entsteht eine grenzenlose Sandbox, in der menschliche Entwickler and KI-Agenten denselben Workspace manipulieren, orchestrieren and überwachen können.1. Container / Environment Registry (Docker Go SDK)Um redundante Build-Zeiten zu eliminieren, entkoppelt R13 die Definition von Laufzeiten von den konkreten Deployments. Über das offizielle Go Docker SDK (github.com/docker/docker/client) verwaltet der OpenMesh-Core ein transientes Image-Management.Environment Templates: Kompositionen (z. B. golang + dsh-sdk) werden als Rezepte in PostgreSQL hinterlegt.Agentic Instantiation: Erkennt das Utility-Modell, dass for eine Teilaufgabe eine isolierte Python-Umgebung benötigt wird, triggert es about das SDK einen unbenannten Container, führt die CrewAI-Crew from, persistiert Key Findings in einem geteilten Docker-Volume and zerstört die Instanz automatisch.go// Database Schema for wiederverwendbare Umgebungen
type EnvironmentTemplate struct {
	ID        string          `json:"id" db:"id"`
	Name      string          `json:"name" db:"name"`
	BaseImage string          `json:"base_image" db:"base_image"`
	Packages  []string        `json:"packages" db:"packages"` // ["pip install crewai", "apt install curl"]
	Config    json.RawMessage `json:"config" db:"config"`     // Volumes, Envs, Limits
	Version   int             `json:"version" db:"version"`
}
│  AI Agent (Claude Code / DSH SDK)    │
└──────────────────┬───────────────────┘
                   │
                   ▼ MCP Client Protocol (JSON-RPC)
┌──────────────────────────────────────────────────────┐
│  OpenMesh Go Core (MCP Server Role)                    │
│  ├─ Tool: openmesh.deploy(project_id, layer_config)    │
│  ├─ Tool: openmesh.provision_mesh(chain_id, port)      │
│  └─ Tool: shell_exec(container_id, command)          │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼ MCP Server Protocol (Downstream Gateway)
┌──────────────────────────────────────────────────────┐
│  External MCP Servers (Filesystem, Postgres-DB)      │
└──────────────────────────────────────────────────────┘
OpenMesh als MCP Server: Exponiert den gesamten Core-Funktionsumfang an externe Agenten-CLIs. Claude Code kann nativ about MCP-Befehle Infrastruktur-Deployments on dem Host anfordern.OpenMesh als MCP Client: Das interne Utility-Modell nutzt spezialisierte Host-MCP-Server (z. B. for sicheren Dateisystem-Zugriff), um Dateioperationen standardisiert zu bündeln.3. Auto-Discovery PipelineDer Go-Core führt im Background eine kontinuierliche Kaskaden-Erkennung about die Docker-Socket-API and SSH-Sitzungen from, um Schatten-Infrastrukturen automatisiert zu erfassen.Container Scan: Liest docker ps from and analysiert Labels and Ports.Port-to-Process Matching: Kombiniert SSH ss -tlnp (R11), um offene Sockets bekannten Mustern zuzuordnen (z. B. Port 5432 = PostgreSQL).Workspace Crawling: Sucht im Remote-Dateisystem after Mustern wie docker-compose.yml, package.json or go.mod.Promotion Workflow: Entdeckte Services werden im Dashboard unter dem Tab "Network Discovery" visualisiert. Mit einem Klick befördert der User diese zu einem offiziellen Dashboard-Deployment or registriert sie direkt als Live-Werkzeug for Agenten.4. Agent Tool Registry DesignDie Tool Registry ist das Bindeglied, about das Agenten wissen, welche Fähigkeiten im Cluster aktiv sind.sqlCREATE TABLE agent_tools (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(32) NOT NULL, -- 'shell', 'database', 'browser', 'filesystem'
    config JSONB NOT NULL DEFAULT '{}'::jsonb, -- Verbindungsdaten, Ports, Container-IDs
    enabled BOOLEAN DEFAULT TRUE,
    auto_discovered BOOLEAN DEFAULT FALSE,
    config_schema JSONB NOT NULL -- Erzeugt dynamisch die UI-Eingabemaske im Frontend
);
