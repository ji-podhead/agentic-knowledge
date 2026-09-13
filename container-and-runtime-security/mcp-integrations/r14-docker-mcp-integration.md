---
okf_version: "1.0"
id: "okf-con-mcp-r14-docker-mcp-integration"
title: "Docker MCP Integration — Verified Connectors as Bridge"
topic: "container-and-runtime-security"
subtopic: "mcp-integrations"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - container-and-runtime-security
  - mcp-integrations
summary: "Docker announced MCP (Model Context Protocol) support with:"
---

# Docker MCP Integration — Verified Connectors as Bridge

## Docker MCP Toolkit Overview

Docker announced MCP (Model Context Protocol) support with:
1. **Docker MCP Catalog** — marketplace of verified MCP connectors
2. **Docker MCP Toolkit** — run MCP servers in Docker containers, isolated
3. **Docker MCP Gateway** — single gateway that AI tools connect to → get all MCP tools
4. **`docker mcp` CLI** — install, manage, run MCP servers

### How it works
```
AI Agent (DSH, Claude Code, OpenMesh agent)
  ↕ MCP Protocol (JSON-RPC over stdio/SSE)
Docker MCP Gateway
  ├── MCP Server: filesystem     (Docker container, isolated)
  ├── MCP Server: github         (Docker container, OAuth)
  ├── MCP Server: postgres       (Docker container, DB access)
  ├── MCP Server: slack          (Docker container, API)
  ├── MCP Server: docker         (Docker container, Docker API)
  ├── MCP Server: brave-search   (Docker container, web search)
  ├── MCP Server: memory         (Docker container, KV store)
  └── MCP Server: openmesh         (our own — expose OpenMesh API)
```

### Key advantages for OpenMesh
- **Verified connectors**: Docker tests/signs MCP servers in the catalog
- **Isolation**: each MCP server runs in its own container (no host access)
- **Secrets**: Docker manages secrets per MCP server (OAuth tokens, API keys)
- **Discovery**: `docker mcp` lists all installed/running MCP servers
- **Auto-registration**: OpenMesh network discovery finds running MCP servers → auto-register as agent tools
- **User installs**: user runs `docker mcp server add <name>` → OpenMesh detects → exposes to agents

---

## Docker MCP CLI Commands

```bash
# List available MCP servers in the catalog
docker mcp catalog list

# Add/install an MCP server
docker mcp server add github
docker mcp server add filesystem
docker mcp server add postgres

# List installed MCP servers
docker mcp server list

# Run the MCP gateway (agents connect to this)
docker mcp gateway run

# Inspect an MCP server's tools
docker mcp server inspect github

# Remove an MCP server
docker mcp server remove github
```

---

## Docker MCP Catalog — Known Connectors

| Connector | Type | What it provides |
|---|---|---|
| `filesystem` | file access | read/write/list files |
| `github` | git/CI | repos, issues, PRs, commits |
| `gitlab` | git/CI | repos, issues, pipelines |
| `postgres` | database | query, schema, tables |
| `mysql` | database | query, schema, tables |
| `sqlite` | database | query, schema |
| `redis` | cache | get/set/keys |
| `brave-search` | web search | web search results |
| `fetch` | HTTP | fetch URLs, parse HTML |
| `memory` | KV store | key-value storage |
| `time` | utility | time/timezone tools |
| `sequential-thinking` | reasoning | structured thinking |
| `slack` | messaging | send/read messages |
| `puppeteer` | browser | browser automation |
| `docker` | containers | container management |
| **`openmesh`** (ours) | mesh routing | deploy, provision, chains, experts |

---

## OpenMesh + Docker MCP Integration Architecture

### 1. OpenMesh as MCP Server
OpenMesh exposes its own API as MCP tools:
- `openmesh.deploy(project, type, path)` — E2E deployment
- `openmesh.provision(project, chainId)` — auto-provision mesh endpoints
- `openmesh.list_chains()` — list mesh routers
- `openmesh.list_experts()` — list registered experts
- `openmesh.execute_experts(task)` — run MoE pipeline
- `openmesh.orchestrate(task)` — orchestration endpoint
- `openmesh.enrich_model(modelId)` — enrichment pipeline
- `openmesh.get_analytics()` — request analytics
- `openmesh.create_environment(template)` — container from template

### 2. OpenMesh as MCP Client
OpenMesh utility agent can use other MCP servers:
- `filesystem.read(path)` — read files via filesystem MCP
- `postgres.query(sql)` — query DB via postgres MCP
- `github.create_pr(repo, ...)` — create PR via github MCP
- `brave_search.search(query)` — web search via brave MCP
- `puppeteer.navigate(url)` — browser via puppeteer MCP
- `docker.create(image, env)` — create container via docker MCP

### 3. Network Discovery → MCP Auto-Detection
```
OpenMesh SSH → docker mcp server list
  → parse output: [filesystem, github, postgres, brave-search]
  → for each running MCP server:
    → auto-register as agent tool
    → expose to utility agent + MoE experts
    → show in Discovery tab with MCP badge
```

### 4. User Flow
1. User: `docker mcp server add postgres` (on remote box via SSH)
2. OpenMesh network discovery detects new MCP server
3. OpenMesh auto-registers `postgres.query` as agent tool
4. User sees in Discovery tab: "MCP: postgres (queries, schema)"
5. User clicks "Add to sidebar" → tool appears in agent tool list
6. Utility agent can now use `postgres.query()` in its planning

---

## Go Implementation

### MCP Server (Go)
Use `github.com/mark3labs/mcp-go`:
```go
import "github.com/mark3labs/mcp-go/mcp"

server := mcp.NewServer("openmesh", "1.0.0")
server.RegisterTool("deploy", "Deploy a project", deployHandler)
server.RegisterTool("provision", "Provision mesh endpoints", provisionHandler)
server.RegisterTool("list_chains", "List mesh routers", listChainsHandler)
server.RegisterTool("execute_experts", "Run MoE expert pipeline", executeExpertsHandler)
// Run as Docker container: docker mcp server add openmesh
```

### MCP Client (Go)
Use `github.com/mark3labs/mcp-go/mcp` client:
```go
client := mcp.NewClient("unix:///var/run/docker-mcp-gateway.sock")
tools, _ := client.ListTools()
// tools = [{name: "filesystem.read", ...}, {name: "postgres.query", ...}]
result, _ := client.CallTool("postgres.query", map[string]any{"sql": "SELECT 1"})
```

### Discovery via Docker CLI
```go
func (s *Server) discoverMCPServers() ([]MCPServerInfo, error) {
    // SSH: docker mcp server list --format json
    output, err := s.sshExec("docker mcp server list --format json")
    // Parse: [{name: "filesystem", status: "running"}, ...]
    // Auto-register each as agent tool
}
```

### Dockerfile for OpenMesh MCP Server
```dockerfile
FROM golang:1.22 AS builder
COPY . /src
WORKDIR /src
RUN CGO_ENABLED=0 go build -o /openmesh-mcp ./cmd/mcp-server

FROM alpine:3.20
COPY --from=builder /openmesh-mcp /openmesh-mcp
ENTRYPOINT ["/openmesh-mcp"]
```

### Docker Compose for MCP Gateway
```yaml
services:
  mcp-gateway:
    image: docker/mcp-gateway:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - mcp-secrets:/secrets
    ports:
      - "8765:8765"

  openmesh-mcp:
    build: ./cmd/mcp-server
    environment:
      - MESH_URL=http://openmesh:9091
      - MESH_API_KEY=${MESH_API_KEY}
    depends_on:
      - mcp-gateway
```

---

## MCP Tool Schema for OpenMesh

Each MCP tool has a JSON schema that agents use for function calling:

```json
{
  "openmesh.deploy": {
    "description": "Deploy a project with E2E pipeline",
    "inputSchema": {
      "type": "object",
      "properties": {
        "projectId": {"type": "string"},
        "type": {"type": "string", "enum": ["dsh", "opencode", "terminal", "custom"]},
        "remotePath": {"type": "string"},
        "chainId": {"type": "string"}
      },
      "required": ["projectId", "type", "remotePath"]
    }
  },
  "openmesh.provision": {
    "description": "Auto-provision mesh endpoints into a deployment config",
    "inputSchema": {
      "type": "object",
      "properties": {
        "projectId": {"type": "string"},
        "deploymentId": {"type": "integer"},
        "chainId": {"type": "string"},
        "format": {"type": "string", "enum": ["opencode", "dsh", "cursor"]}
      },
      "required": ["projectId", "deploymentId", "chainId", "format"]
    }
  },
  "openmesh.execute_experts": {
    "description": "Run MoE expert pipeline for a task",
    "inputSchema": {
      "type": "object",
      "properties": {
        "task": {"type": "string"},
        "mode": {"type": "string", "enum": ["auto", "parallel", "sequential"]},
        "chainId": {"type": "string"}
      },
      "required": ["task"]
    }
  },
  "openmesh.orchestrate": {
    "description": "Run orchestration pipeline with role-based routing",
    "inputSchema": {
      "type": "object",
      "properties": {
        "task": {"type": "string"},
        "mode": {"type": "string"},
        "chainId": {"type": "string"}
      },
      "required": ["task"]
    }
  },
  "openmesh.create_environment": {
    "description": "Create container from environment template",
    "inputSchema": {
      "type": "object",
      "properties": {
        "template": {"type": "string"},
        "name": {"type": "string"}
      },
      "required": ["template", "name"]
    }
  },
  "openmesh.enrich_model": {
    "description": "Enrich model metadata via pipeline",
    "inputSchema": {
      "type": "object",
      "properties": {
        "modelId": {"type": "string"}
      },
      "required": ["modelId"]
    }
  }
}
```

---

## Network Discovery with MCP Detection

### Discovery Flow
```
1. OpenMesh SSH → docker ps --format json
   → parse: [container1, container2, ...]
   → for each container: check if MCP server (labels: mcp=true)

2. OpenMesh SSH → docker mcp server list --format json
   → parse: [filesystem, github, postgres, brave-search]
   → for each MCP server:
     → query tools: docker mcp server inspect <name> --format json
     → auto-register as agent tool
     → add to Discovery tab with MCP badge + tool list

3. OpenMesh SSH → ss -tlnp
   → parse: [port 5432: postgres, port 6379: redis, ...]
   → match to known patterns
   → auto-register as deployment + potential MCP server

4. OpenMesh SSH → find ~/projects -maxdepth 2 -name "docker-compose.yml"
   → parse: services, ports, images
   → auto-register as discovered project
```

### Discovery DB Schema
```sql
CREATE TABLE discovered_services (
    id SERIAL PRIMARY KEY,
    project_id TEXT,
    name TEXT NOT NULL,
    type TEXT,              -- 'container', 'mcp_server', 'port', 'app'
    image TEXT,             -- docker image if container
    port INTEGER,
    process TEXT,           -- process name from ss
    mcp_tools TEXT DEFAULT '[]',  -- JSON array of MCP tool names
    status TEXT DEFAULT 'discovered',  -- discovered, promoted, ignored
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Discovery → Promotion Flow
1. Discovery finds `postgres` on port 5432
2. Auto-registers in `discovered_services` (status: discovered)
3. User sees in Discovery tab: "PostgreSQL on :5432 (MCP: query, schema)"
4. User clicks "Promote to Deployment"
5. Status → promoted, creates deployment entry
6. User clicks "Add as Agent Tool"
7. Registers `db_query` in `agent_tools` table
8. Utility agent can now use `db_query` in its planning

---

## Complete Connector Registry

OpenMesh knows these connector types. Each can be auto-discovered or manually added:

| Connector | Detection Method | MCP Server | Agent Tools |
|---|---|---|---|
| DSH | port 3079, docker label | `openmesh` (our MCP) | deploy, provision, orchestrate |
| Claude Code | npm package, docker | filesystem MCP | shell, file read/write |
| OpenCode | port 3080, config file | filesystem MCP | shell, file read/write |
| Terminal | port 7681 (ttyd/xterm) | shell MCP | shell_exec |
| PostgreSQL | port 5432 | docker mcp: postgres | db_query, schema |
| MySQL | port 3306 | docker mcp: mysql | db_query, schema |
| Redis | port 6379 | docker mcp: redis | cache_get, cache_set |
| Adminer | port 8080 | (browser only) | browser_navigate |
| GitHub | docker mcp: github | docker mcp: github | create_pr, list_repos |
| Brave Search | docker mcp: brave | docker mcp: brave-search | web_search |
| Filesystem | docker mcp: filesystem | docker mcp: filesystem | read, write, list |
| Puppeteer | docker mcp: puppeteer | docker mcp: puppeteer | browser automation |
| Docker | docker.sock access | docker mcp: docker | container mgmt |
| OpenMesh | (self) | `openmesh` MCP server | all OpenMesh API as tools |

---

Hier ist die vollständige Systemspezifikation and das Architecture-Design for das Modul R14 — Docker MCP Integration. Dieses Modul nutzt das native Docker Model Context Protocol (MCP) Toolkit, um verifizierte, isolierte Agenten-Werkzeuge nahtlos in den OpenMesh Go Core and die MoE-Inferenz-Pipeline zu integrieren [2601.13671].1. Docker MCP Gateway & Network Discovery ArchitectureDurch die Integration des Docker MCP Gateways entfällt das manuelle Verwalten einzelner Werkzeug-Sockets. Der OpenMesh Go Core fungiert synchron als MCP Client (konsumiert verifizierte Konnektoren) and als MCP Server (stellt OpenMesh Core-Features via JSON-RPC for externe Agenten wie Claude Code bereit) [2601.13671].┌─────────────────────────────────────────────────────────────────────────┐
│ JI-MESH AGENT ENVIRONMENT (DSH, Claude Code, MoE Core Engine)           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼ MCP Protocol (JSON-RPC over UNIX Socket / SSE)
┌─────────────────────────────────────────────────────────────────────────┐
│ Docker MCP Gateway (docker/mcp-gateway)                                 │
│ ├─ Verified Connector Pool (Sandboxed via Docker API)                  │
│ ├─ Token & Secret Manager (/secrets Mount)                              │
│ └─ Central Dynamic Discovery Hub                                        │
└────────────┬───────────────────────┬───────────────────────┬────────────┘
             │                       │                       │
             ▼ Isolated Container    ▼ Isolated Container    ▼ Isolated Container
   ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
   │ mcp/filesystem    │   │ mcp/postgres      │   │ mcp/openmesh        │
   │ (Host Path Mount) │   │ (DB Auth Connect) │   │ (Our Go Binary)   │
   └───────────────────┘   └───────────────────┘   └───────────────────┘
🔄 Autonome MCP Discovery-Pipeline:Das OpenMesh-Background-Parsing führt periodisch about den SSH-Kanal (R11) den Befehl docker mcp server list --format json from.Erkannte Konnektoren (z. B. postgres, github) werden ausgelesen and im Dashboard-Tab "Discovery" with einem exklusiven MCP Blue-Badge versehen.Der Go-Core fragt about das Gateway die verfügbaren Werkzeug-Signaturen ab and injiziert sie direkt in die Function-Calling-Ebene des utility-Modells.2. Implementation: Go MCP Server & Client CoreUnter Verwendung von github.com/mark3labs/mcp-go implementiert OpenMesh die bidirektionale Registrierung nativ [2601.13671].A. OpenMesh als MCP Server (Bereitstellung unserer API for Agenten)gopackage mcp_server

import (
	"context"
	"fmt"
	"github.com/mark3labs/mcp-go/mcp"
	"://github.com"
)

func InitOpenMeshMCPServer() *server.MCPServer {
	s := server.NewMCPServer("openmesh", "1.0.0")

	// 1. Tool-Registrierung: E2E Deployment
	s.AddTool(mcp.Tool{
		Name:        "openmesh_deploy",
		Description: "Deploys a multi-window coding workspace or project runtime using layered schemas.",
		InputSchema: mcp.ParameterSchema{
			Type: "object",
			Properties: map[string]mcp.PropertySchema{
				"projectId":  {Type: "string", Description: "Unique targeted project identifier"},
				"deployType": {Type: "string", Description: "Runtime medium type", Enum: []string{"dsh", "opencode", "terminal"}},
				"remotePath": {Type: "string", Description: "Target absolute directory path"},
			},
			Required: []string{"projectId", "deployType", "remotePath"},
		},
	}, handleDeploy)

	return s
}

func handleDeploy(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	projID := request.Arguments["projectId"].(string)
	// Hier folgt der direkte Aufruf der R11 E2E-Deployment-Engine
	return mcp.NewToolResultText(fmt.Sprintf("Deployment successfully initiated for project %s", projID)), nil
}

import (
	"context"
	"://github.com"
)

type MCPBridge struct {
	gatewayClient *client.MCPClient
}

func NewMCPBridge(socketPath string) (*MCPBridge, error) {
	// Erzeugt eine langlebige Client-Verbindung zum Docker MCP Gateway
	c, err := client.NewClient(socketPath)
	if err != nil {
		return nil, err
	}
	return &MCPBridge{gatewayClient: c}, nil
}

func (bridge *MCPBridge) InvokeDatabaseQuery(ctx context.Context, sql string) (string, error) {
	// Dynamischer Aufruf des isolierten Docker-Postgres-Konnektors
	resp, err := bridge.gatewayClient.CallTool(ctx, "postgres.query", map[string]interface{}{
		"sql": sql,
	})
	if err != nil {
		return "", err
	}
	return resp.Content[0].Text, nil
}
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /openmesh-mcp-engine ./cmd/mcp-server/main.go

FROM alpine:3.20
RUN apt-get update && apt-get install -y ca-certificates
COPY --from=builder /openmesh-mcp-engine /openmesh-mcp-engine
EXPOSE 8765
ENTRYPOINT ["/openmesh-mcp-engine"]
  mcp-gateway:
    image: docker/mcp-gateway:latest
    container_name: openmesh-mcp-gateway
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - openmesh-mcp-secrets:/secrets:ro # Isolierter Lesezugriff for OAuth/API-Keys
    ports:
      - "8765:8765"

  openmesh-mcp:
    build:
      context: .
      dockerfile: ./cmd/mcp-server/Dockerfile
    container_name: openmesh-mcp-server
    environment:
      - MESH_CORE_URL=http://openmesh-core:9091
      - MESH_API_KEY=${MESH_API_KEY}
    depends_on:
      - mcp-gateway
    networks:
      - openmesh-network

volumes:
  openmesh-mcp-secrets:
    external: true
  "description": "Auto-provisions local mesh endpoint fallback configurations into target workspace configurations.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "projectId": { "type": "string" },
      "chainId": { "type": "string" },
      "format": { "type": "string", "enum": ["opencode", "dsh", "cursor"] }
    },
    "required": ["projectId", "chainId", "format"]
  }
}
  "description": "Routes the task prompt through the Agentic Mixture-of-Experts pipeline utilizing entropy metrics.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task": { "type": "string", "description": "The high-level coding or analytical problem." },
      "mode": { "type": "string", "enum": ["auto", "parallel", "sequential"] }
    },
    "required": ["task", "mode"]
  }
}
