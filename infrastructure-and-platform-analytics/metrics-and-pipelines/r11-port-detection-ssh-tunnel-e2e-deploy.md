---
okf_version: "1.0"
id: "okf-inf-met-r11-port-detection-ssh-tunnel-e2e-deploy"
title: "R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment"
topic: "infrastructure-and-platform-analytics"
subtopic: "metrics-and-pipelines"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - infrastructure-and-platform-analytics
  - metrics-and-pipelines
summary: "Kann der Go backend ports auf dem remote target erkennen, SSH tunnel für"
---

# R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment

## Question
Kann der Go backend ports on dem remote target erkennen, SSH tunnel for
iframe cache + streaming aufbauen (statt browser direkt), and E2E deployments
for agent tools (DSH, Claude Code) automatisch erzeugen (Dockerfiles, compose
files im target path)?

## Research Tasks

### 1. Port Detection via SSH
- [ ] Go backend macht SSH zur remote box
  - `golang.org/x/crypto/ssh` — SSH client in Go
  - Scan for offene ports: `ss -tlnp` or `netstat` via SSH
  - Oder: `nmap` wenn verfügbar, sonst `ss` fallback
  - Parse output → liste der offenen ports + process names
- [ ] API: `GET /api/projects/{id}/ports` — listet offene ports via SSH
  - Returns: `[{ port: 3079, process: "dsh", pid: 12345 }, { port: 9091, process: "openmesh" }]`
- [ ] Frontend: port picker zeigt erkannte ports → pre-fill deployment port
  - Badge: "in use by: dsh" or "free"
  - Auto-detect: welcher port zu welchem deployment type gehört
    (3079 = DSH, 9091 = OpenMesh, 9090 = OpenMesh frontend, etc.)

### 2. SSH Tunnel Bridge (Go als Proxy, not Browser)
- [ ] Statt das der browser direkt zum iframe target connectet:
  - Browser → OpenMesh Go backend → SSH tunnel → remote target
  - Go backend hält SSH session alive (connection pool)
  - HTTP requests werden through den tunnel getunnelt
  - iframe `src` zeigt on OpenMesh endpoint, not on remote target
- [ ] Advantages:
  - Cache: Go backend cached responses (HTTP/3 reverse proxy, R9)
  - Streaming: Go backend kann SSE/WebSocket through den tunnel streamen
  - Security: browser braucht keinen direkten zugriff on remote target
  - Monitoring: Go backend sieht allen traffic → analytics
  - Connection management: SSH session persistent, not pro-request
- [ ] Implementation:
  - `golang.org/x/crypto/ssh` for SSH tunnel
  - `net.Dial` via SSH client → `sshClient.Dial("tcp", "localhost:3079")`
  - HTTP reverse proxy with custom Dialer
  - Connection pool: eine SSH session per project, reused for alle requests
  - Keep-alive: heartbeat alle 30s
  - Reconnect: automatischer reconnect at disconnect

### 3. E2E Deployment (Auto-Generate Dockerfiles + Compose)
- [ ] Statt for jedes projekt den deployment code zu schreiben:
  - User wählt "E2E Deploy" im project → wählt deployment type (DSH, Claude Code, terminal)
  - OpenMesh generiert automatisch:
    1. Dockerfile im target path (basiert on deployment schema + addons)
    2. docker-compose.yml (or erweitert bestehende)
    3. Config files (z.B. opencode.json, vconfig.json) with mesh provision
    4. Environment file (.env) with API keys
  - All via SSH direkt on dem remote target geschrieben
- [ ] Workflow:
  1. User: "Create E2E deployment for DSH in ~/projects/my-app"
  2. Backend: SSH → `ls ~/projects/my-app` → checkt ob compose file existiert
  3. Wenn ja: liest compose, fügt DSH service hinzu, schreibt zurück
  4. Wenn nein: generiert neue docker-compose.yml with DSH service
  5. Generiert Dockerfile basierend on schema (base image + addons)
  6. Generiert config files (vconfig.json with mesh provision)
  7. Schreibt alles via SSH in den target path
  8. Startet: `docker compose up -d` via SSH
  9. Verbindet iframe tunnel zum neuen service port
- [ ] Schema-driven generation:
  - Base medium schema (terminal/dsh/opencode) → base Dockerfile
  - Addon schemas (claude-code, aider) → additional packages + config
  - User overrides → env vars, custom packages
  - Template engine: Go text/template or embedded templates
- [ ] Templates:
  - `templates/dockerfile/dsh.tmpl`
  - `templates/dockerfile/terminal.tmpl`
  - `templates/compose/service.tmpl` (fügt service block in compose ein)
  - `templates/config/opencode.json.tmpl`
  - `templates/config/vconfig.json.tmpl`
  - Variablen: `{{.ProjectID}}`, `{{.Port}}`, `{{.RemotePath}}`, `{{.MeshEndpoint}}`, `{{.APIKey}}`

### 4. OpenMesh als Bridge for Connectors + Monitoring
- [ ] OpenMesh backend ist die zentrale bridge:
  - SSH tunnel for iframe content (port detection + forwarding)
  - SSH tunnel for agent tool traffic (OpenAI API proxy through tunnel)
  - Monitoring: alle requests through den tunnel werden geloggt
  - Auto-provision: mesh endpoints werden in config files geschrieben
  - E2E deployment: docker files werden generiert and deployed
  - Health check: periodic SSH health check for deployments
- [ ] Connector registry:
  - OpenMesh kennt connectors: DSH, Claude Code, OpenCode, Aider, terminal
  - Jeder connector hat: deploy template, config template, port mapping
  - User registriert neuen connector → OpenMesh generiert templates
- [ ] Monitoring bridge:
  - `GET /api/projects/{id}/monitoring` — live stats vom remote target
  - CPU, memory, disk via SSH (`top`, `df`, `free`)
  - Container stats via SSH (`docker stats --no-stream`)
  - Log tail via SSH (`docker compose logs --tail 100`)
  - SSE stream for live updates

### 5. Streaming through SSH Tunnel
- [ ] WebSocket support through SSH tunnel:
  - Go backend upgrade zu WebSocket → tunnel via SSH → remote target
  - Bidirectional: browser ↔ Go ↔ SSH ↔ remote
  - Use case: terminal (xterm.js), DSH chat, live logs
- [ ] SSE support:
  - Go backend fetched SSE vom remote → re-streamed to browser
  - Cache: Go backend cached chunks for iframe resume (R9 HTTP/3)
- [ ] HTTP/3 (QUIC):
  - Browser ↔ Go backend about HTTP/3 (0-RTT, multiplexing)
  - Go backend ↔ remote target about SSH tunnel (TCP)
  - Best of both: fast client connection + secure tunnel

## Architecture Overview
```
Browser (iframe + xterm.js)
    ↕ HTTP/3 (0-RTT, QUIC)
OpenMesh Go Backend
    ├── Port Scanner (SSH: ss -tlnp)
    ├── SSH Tunnel Pool (persistent per project)
    ├── Reverse Proxy Cache (iframe content)
    ├── E2E Deploy Engine (template generation)
    ├── Connector Registry (DSH, Claude Code, ...)
    ├── Monitoring Bridge (CPU/mem/disk/logs via SSH)
    └── Mesh Provision (writes config files via SSH)
    ↕ SSH Tunnel
Remote Target Box
    ├── Docker Compose (DSH, Claude Code, terminal)
    ├── Config files (opencode.json, vconfig.json)
    └── Mesh endpoints (OpenMesh proxy :9091)
```

## Output Format
1. SSH tunnel architecture (Go als proxy, connection pool, keep-alive)
2. Port detection API + frontend integration
3. E2E deployment flow (schema → templates → SSH write → docker compose up)
4. Connector registry design
5. Monitoring bridge (live stats via SSH)
6. WebSocket/SSE through tunnel

---

Hier ist die vollständige Systemspezifikation and das Architecture-Design for das Modul R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment. Dieses Modul macht den OpenMesh Go Core zur zentralen, sicheren Netzwerk- and Deployment-Brücke zwischen dem Browser-Frontend and den Remote-Target-Boxen.1. SSH Tunnel Bridge Architecture (Go als Proxy)Anstatt dass der Browser iFrames or WebSockets direkt vom Remote-Ziel lädt, terminiert der OpenMesh Go Core alle Client-Verbindungen about HTTP/3 (QUIC) and leitet den Traffic about einen langlebigen, multiplexierten SSH-Tunnel-Pool (golang.org/x/crypto/ssh) weiter [2601.13671].┌──────────────────────────────┐
│  Browser (iFrame / xterm.js) │
└──────────────┬───────────────┘
               │
               ▼ HTTP/3 QUIC (0-RTT, Multi-Streaming, R9)
┌────────────────────────────────────────────────────────┐
│  OpenMesh Go Backend Proxy                               │
│  ├─ Connection Pool (1 SSH Session per Project)         │
│  ├─ Keep-Alive Worker (Heartbeat every 30s)             │
│  └─ Reverse Proxy w/ Custom Dialer (sshClient.Dial)     │
└──────────────┬─────────────────────────────────────────┘
               │
               ▼ Secure SSH Tunnel (TCP Forwarding via golang.org/x/crypto/ssh)
┌────────────────────────────────────────────────────────┐
│  Remote Target Box                                     │
│  └─ Docker Containers (DSH, Claude Code, Runtimes)     │
└────────────────────────────────────────────────────────┘
Engine-Implementation: Connection Pool & Custom DialerDer Go-Core hält pro Projekt genau eine ssh.Client-Verbindung offen. Der HTTP-Reverse-Proxy überschreibt den DialContext des Standard-Transports, um Datenströme direkt in den SSH-Kanal zu injizieren:gopackage network

import (
	"context"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sync"
	"golang.org/x/crypto/ssh"
)

type TunnelPool struct {
	mu       sync.RWMutex
	sessions map[string]*ssh.Client // Key: ProjectID
}

func (tp *TunnelPool) GetReverseProxy(projectID string, targetPort string) (*httputil.ReverseProxy, error) {
	tp.mu.RLock()
	sshClient := tp.sessions[projectID]
	tp.mu.RUnlock()

	targetURL, _ := url.Parse("http://127.0.0.1:" + targetPort)

	proxy := httputil.NewSingleHostReverseProxy(targetURL)
	proxy.Transport = &http.Transport{
		DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
			// Leitet den HTTP-Traffic direkt through den SSH-Tunnel on localhost des Targets
			return sshClient.Dial("tcp", "127.0.0.1:"+targetPort)
		},
	}
	return proxy, nil
}
  { "port": 3079, "process": "dsh", "pid": 89412, "status": "in_use" },
  { "port": 7681, "process": "ttyd", "pid": 89500, "status": "in_use" },
  { "port": 8080, "process": "node", "pid": 0, "status": "free" }
]
           │
           ▼
[Fetch Base + Addon Schemas] ──► [Compile Go text/template Files]
                                              │
                                              ▼
[Run Remote Check via SSH] ◄─── [Connect to Remote Box via SSH]
   ├─ If compose exists: Patch Service
   └─ If not: Create docker-compose.yml
                                              │
                                              ▼
                        [Write Configs & Secrets (.env) to Target Path]
                                              │
                                              ▼
                        [Execute: docker compose up -d via SSH Session]
                                              │
                                              ▼
                        [Establish HTTP/3 iFrame Tunnel Bridge to New Port]
Go-Template-Beispiel for ein geschichtetes Dockerfile (templates/dockerfile.tmpl):dockerfile# Base Medium Selection
{{if eq .BaseMedium "terminal"}}
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y curl git tmux nodejs npm
{{else if eq .BaseMedium "dsh"}}
FROM deepseek-ai/dsh-core:latest
{{end}}

# Addon Layer: Claude Code
{{if .HasAddon "claude-code"}}
RUN npm install -g @anthropic-ai/claude-code
{{end}}

# Addon Layer: OpenMesh Auto-Provision Config Invalidation
{{if .HasAddon "openmesh-mesh"}}
COPY openmesh-provision.json /root/.config/openmesh/config.json
{{end}}

EXPOSE {{.Port}}
CMD ["/bin/bash"]
	ID             string            `json:"id"`           // "claude-code", "dsh", "aider"
	Name           string            `json:"name"`         // "Claude Code CLI"
	DefaultPort    int               `json:"default_port"` // 7681
	DockerfileTmpl string            `json:"-"`            // Eingebettetes Go-Template
	ConfigTmpl     string            `json:"-"`            // z.B. vconfig.json Template
	EnvPresets     map[string]string `json:"env_presets"`  // Standard-ENVs
}
