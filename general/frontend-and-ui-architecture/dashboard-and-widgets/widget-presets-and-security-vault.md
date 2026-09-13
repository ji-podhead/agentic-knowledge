---
okf_version: "1.0"
id: "okf-fro-das-widget-presets-and-security-vault"
title: "R16 — Widget Presets, App Categories, Security/SecOps & Vault"
topic: "general/frontend-and-ui-architecture"
subtopic: "dashboard-and-widgets"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - frontend-and-ui-architecture
  - dashboard-and-widgets
summary: "The Multi-Provider Gateway dashboard wird widget-based (wie leobot2 trading bot):"
---

# R16 — Widget Presets, App Categories, Security/SecOps & Vault

## Vision
The Multi-Provider Gateway dashboard wird widget-based (wie leobot2 trading bot):
- Widget Registry with Kategorien (mesh, agents, discovery, security, system)
- Dashboard Presets (vorgefertigte grid layouts)
- App Kategorien als pseudo-layer for sidebar (deployments gruppieren)
- Security/SecOps widgets (traffic debug, network topology, security audit)
- Vault: agents never access secrets directly → gateway proxy

## 1. Widget Registry Pattern (adapted from leobot2)

### Categories
```
mesh:      Mesh Canvas, Chain Graph, Pool Members, Mesh Edges
agents:    Expert Registry, Orchestration, MoE Pipeline, Cost Tracker
discovery: Container Discovery, Port Map, Network Topology, MCP Catalog
security:  Traffic Debug, Security Audit, Vault Access, Secret Scanner
system:    Live Logs, Analytics, Enrichment, Cost Monitor, Settings
deploy:    Deployment Grid, Project Roadmap, E2E Builder, Environment Registry
```

### Widget Registry (The Multi-Provider Gateway-specific)
```typescript
WIDGET_REGISTRY = {
  // mesh
  mesh_canvas:    { label: 'Mesh Canvas',    icon: 'Network',    category: 'mesh',    grid: { w: 12, h: 24 } },
  chain_graph:    { label: 'Chain Graph',    icon: 'GitBranch',  category: 'mesh',    grid: { w: 6, h: 16 } },
  pool_members:   { label: 'Pool Members',   icon: 'Layers',     category: 'mesh',    grid: { w: 4, h: 12 } },
  mesh_edges:     { label: 'Mesh Edges',     icon: 'Share2',     category: 'mesh',    grid: { w: 4, h: 10 } },

  // agents
  expert_registry:   { label: 'Expert Registry', icon: 'Users',     category: 'agents', grid: { w: 4, h: 14 } },
  orchestration:      { label: 'Orchestration',   icon: 'Workflow',  category: 'agents', grid: { w: 8, h: 16 } },
  moe_pipeline:       { label: 'MoE Pipeline',    icon: 'Brain',     category: 'agents', grid: { w: 6, h: 16 } },
  cost_tracker:       { label: 'Cost Tracker',    icon: 'DollarSign',category: 'agents', grid: { w: 4, h: 10 } },

  // discovery
  container_discovery: { label: 'Containers',      icon: 'Container', category: 'discovery', grid: { w: 6, h: 14 } },
  port_map:            { label: 'Port Map',         icon: 'Map',       category: 'discovery', grid: { w: 4, h: 12 } },
  network_topology:    { label: 'Network Topology', icon: 'Share2',    category: 'discovery', grid: { w: 8, h: 16 } },
  mcp_catalog:         { label: 'MCP Catalog',      icon: 'Plug',      category: 'discovery', grid: { w: 6, h: 14 } },

  // security
  traffic_debug:    { label: 'Traffic Debug',    icon: 'Activity',   category: 'security', grid: { w: 8, h: 16 } },
  security_audit:    { label: 'Security Audit',   icon: 'ShieldCheck',category: 'security', grid: { w: 6, h: 14 } },
  vault_access:      { label: 'Vault Access',     icon: 'KeyRound',   category: 'security', grid: { w: 4, h: 12 } },
  secret_scanner:    { label: 'Secret Scanner',   icon: 'ScanSearch', category: 'security', grid: { w: 6, h: 10 } },

  // system
  live_logs:        { label: 'Live Logs',        icon: 'Terminal',     category: 'system', grid: { w: 8, h: 16 } },
  analytics:        { label: 'Analytics',        icon: 'BarChart3',    category: 'system', grid: { w: 6, h: 14 } },
  enrichment:       { label: 'Enrichment',        icon: 'Database',     category: 'system', grid: { w: 6, h: 12 } },
  cost_monitor:     { label: 'Cost Monitor',      icon: 'DollarSign',   category: 'system', grid: { w: 4, h: 10 } },
  settings_panel:   { label: 'Settings',          icon: 'Settings',     category: 'system', grid: { w: 4, h: 16 } },

  // deploy
  deployment_grid:  { label: 'Deployments',       icon: 'Server',      category: 'deploy', grid: { w: 8, h: 14 } },
  project_roadmap:  { label: 'Project Roadmap',  icon: 'Map',          category: 'deploy', grid: { w: 12, h: 20 } },
  e2e_builder:      { label: 'E2E Builder',       icon: 'Wrench',      category: 'deploy', grid: { w: 6, h: 16 } },
  env_registry:     { label: 'Environment Registry', icon: 'Package',  category: 'deploy', grid: { w: 6, h: 12 } },
}
```

### Dashboard Presets (The Multi-Provider Gateway)
```typescript
DASHBOARD_PRESETS = {
  mesh_overview: {
    name: 'Mesh Overview',
    gridLayout: [mesh_canvas(w12,h24)]
  },
  agent_ops: {
    name: 'Agent Operations',
    gridLayout: [expert_registry(w4), orchestration(w8), moe_pipeline(w6), cost_tracker(w4)]
  },
  discovery_security: {
    name: 'Discovery & Security',
    gridLayout: [container_discovery(w6), network_topology(w8), security_audit(w6), traffic_debug(w8)]
  },
  secops_console: {
    name: 'SecOps Console',
    gridLayout: [traffic_debug(w8), security_audit(w6), vault_access(w4), secret_scanner(w6)]
  },
  full_control: {
    name: 'Full Control',
    gridLayout: [mesh_canvas(w8), deployment_grid(w4), live_logs(w8), analytics(w4), cost_monitor(w4)]
  },
}
```

## 2. App Categories (Pseudo-Layer for Sidebar)

Deployments are grouped by category in the sidebar:
```
Sidebar:
  📂 Databases
    ├── PostgreSQL (project-a) → :5432
    └── Redis (project-b) → :6379
  📂 Coding Tools
    ├── DSH (project-a) → :3079
    └── OpenCode (project-b) → :3080
  📂 Admin UIs
    └── Adminer (auto-suggested) → :8080
  📂 Terminals
    └── ttyd (project-a) → :7681
  📂 Monitoring
    └── The Multi-Provider Gateway Backend → :9091
```

### Smart Suggestions
When a database is deployed, The Multi-Provider Gateway suggests complementary apps:
- PostgreSQL deployed → suggest Adminer (DB admin UI)
- Redis deployed → suggest Redis Commander
- MySQL deployed → suggest phpMyAdmin
- MongoDB deployed → suggest Mongo Express
- Any app deployed → suggest monitoring sidecar

### DB Schema
```sql
CREATE TABLE app_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,         -- "Databases", "Coding Tools", "Admin UIs"
    icon TEXT DEFAULT 'Server',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE deployment_categories (
    deployment_id INTEGER REFERENCES deployments(id),
    category_id INTEGER REFERENCES app_categories(id),
    PRIMARY KEY (deployment_id, category_id)
);
```

### Auto-Categorization
Based on detected deployment type:
```go
var TypeToCategory = map[string]string{
    "postgresql": "Databases",
    "mysql":      "Databases",
    "redis":      "Databases",
    "mongodb":    "Databases",
    "dsh":        "Coding Tools",
    "opencode":   "Coding Tools",
    "claude-code":"Coding Tools",
    "aider":      "Coding Tools",
    "terminal":   "Terminals",
    "ttyd":       "Terminals",
    "adminer":    "Admin UIs",
    "redis-commander": "Admin UIs",
    "mongo-express": "Admin UIs",
    "llm-mesh-gateway":     "Monitoring",
}
```

## 3. Security/SecOps Widgets

### Traffic Debug Widget
- Live HTTP request/response stream through the proxy
- Filter by: chain, model, status code, entropy, escalated
- Wireframe view: shows request flow: client → The Multi-Provider Gateway → model → response
- JSON inspector: expand/collapse request/response bodies
- Timeline: request duration, TTFB, token count

### Network Topology Widget
- React Flow graph of all services + connections
- Nodes: The Multi-Provider Gateway proxy, chains, models, deployments, discovered services
- Edges: traffic flow, dependencies
- Real-time: edge thickness = request volume
- Security overlay: highlight insecure connections (no TLS)

### Security Audit Widget
- Scan for:
  - Secrets in plaintext in DB (check all settings)
  - Unencrypted API keys
  - Open ports without authentication
  - Containers running as root
  - SSH keys without passphrase
- Score: 0-100 security score
- Recommendations: "Enable encryption", "Set MESH_ENCRYPTION_KEY"

### Vault Access Widget
- List all secrets (names only, values masked)
- Create/update/delete secrets
- Access log: who (human/agent) accessed what when
- Time-limited tokens for agents

## 4. Vault (Gateway-Based Secret Access)

### Architecture
```
Agent (MoE expert, orchestration)
  ↕ MCP tool call: vault.get_secret("openrouter_api_key")
The Multi-Provider Gateway Gateway (Go backend)
  ├── Vault Layer (AES-GCM-256, already built in R15)
  ├── Access Control (RBAC: which agents can access which secrets)
  ├── Audit Log (all access logged)
  ├── Token Generator (time-limited access tokens)
  └── Secret Store (PostgreSQL encrypted)
```

### Rules
1. Agents NEVER access secrets directly (no raw DB, no env vars)
2. All secret access goes through gateway MCP tool: `vault.get_secret(key)`
3. Gateway validates agent identity + permission
4. Gateway logs every access (audit trail)
5. Gateway can issue time-limited tokens (e.g., 5 min access to one secret)
6. If agent is compromised → revoke token → access blocked

### Vault API
```
GET  /api/vault/secrets              — list (names only, values masked)
POST /api/vault/secrets              — create { name, value, allowedAgents[] }
GET  /api/vault/secrets/{name}        — get value (requires auth)
PUT  /api/vault/secrets/{name}        — update
DELETE /api/vault/secrets/{name}      — delete
GET  /api/vault/audit                 — access log
POST /api/vault/tokens                 — issue time-limited token { secretName, ttl, agentId }
POST /api/vault/tokens/{id}/revoke     — revoke token
```

### MCP Tool
```json
{
  "vault.get_secret": {
    "description": "Retrieve a secret value from the vault. Access is logged.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "token": { "type": "string", "description": "Time-limited access token" }
      },
      "required": ["name", "token"]
    }
  }
}
```

### DB Schema
```sql
CREATE TABLE vault_secrets (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    encrypted_value TEXT NOT NULL,    -- AES-GCM-256 encrypted
    allowed_agents TEXT DEFAULT '[]',  -- JSON array of agent IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vault_audit_log (
    id BIGSERIAL PRIMARY KEY,
    secret_name TEXT NOT NULL,
    accessor_type TEXT NOT NULL,       -- "human", "agent", "mcp"
    accessor_id TEXT,                  -- user ID or agent ID
    action TEXT NOT NULL,              -- "read", "create", "update", "delete"
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vault_tokens (
    id TEXT PRIMARY KEY,               -- UUID token
    secret_name TEXT NOT NULL,
    agent_id TEXT,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 5. Environment Tracking

### Environment Registry (from R13, now with Vault integration)
```
Environment Template = base image + packages + config + SECRETS
  → secrets stored in vault, not in template
  → on instantiation: gateway fetches secrets from vault → injects as env vars
  → agent never sees the raw secret
```

## Build Priority
1. Vault backend (vault_secrets + audit_log + tokens tables, API, MCP tool)
2. App categories (categorization, smart suggestions, sidebar grouping)
3. Widget registry backend (store layouts, presets per user)
4. SecOps widgets backend (traffic debug data, security audit scan)

## 6. Tech Ontology (Static Knowledge Base)

### Scientific Foundation
- Ontology-based Data Access (OBDA)
- Context Engineering
- arXiv:2305.04055 — Science and Technology Ontology
- Fraunhofer — Ontology conversion from relational databases
- SNIK — Ontology as data model for data aggregation

### Implementation
File: the Backend Gateway Core
- 40+ technologies mapped: ports, icons, categories, descriptions
- Sidecar suggestions: PostgreSQL → Adminer, Redis → Redis Commander
- Cascading match: port → image name substring → generic fallback
- 0ms latency, no LLM/API needed for known services
- Iconify string IDs: logos:postgresql, logos:redis, lucide:box

### API: `GET /api/ontology?port=5432` or `?image=postgres` or `?category=Databases`

### Stale-While-Revalidate
- DB cache with last_updated timestamp
- 7-day TTL for enrichment data
- Background cron job refreshes stale entries (24h interval)
- Live operations never block on external API calls
