---
id: "R11"
title: "R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment"
type: research
date: 2026-09-06
status: final
tags: [ssh, mesh, docker, opa]
license: CC-BY-4.0
---

# R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment

## Frage
Kann der Go backend ports auf dem remote target erkennen, SSH tunnel für
iframe cache + streaming aufbauen (statt browser direkt), und E2E deployments
für agent tools (DSH, Claude Code) automatisch erzeugen (Dockerfiles, compose
files im target path)?

## Recherche-Aufgaben

### 1. Port Detection via SSH
- [ ] Go backend macht SSH zur remote box
  - `golang.org/x/crypto/ssh` — SSH client in Go
  - Scan für offene ports: `ss -tlnp` oder `netstat` via SSH
  - Oder: `nmap` wenn verfügbar, sonst `ss` fallback
  - Parse output → liste der offenen ports + process names
- [ ] API: `GET /api/projects/{id}/ports` — listet offene ports via SSH
  - Returns: `[{ port: 3079, process: "dsh", pid: 12345 }, { port: 9091, process: "jimesh" }]`
- [ ] Frontend: port picker zeigt erkannte ports → pre-fill deployment port
  - Badge: "in use by: dsh" oder "free"
  - Auto-detect: welcher port zu welchem deployment type gehört
    (3079 = DSH, 9091 = JiMesh, 9090 = JiMesh frontend, etc.)

### 2. SSH Tunnel Bridge (Go als Proxy, nicht Browser)
- [ ] Statt das der browser direkt zum iframe target connectet:
  - Browser → JiMesh Go backend → SSH tunnel → remote target
  - Go backend hält SSH session alive (connection pool)
  - HTTP requests werden durch den tunnel getunnelt
  - iframe `src` zeigt auf JiMesh endpoint, nicht auf remote target
- [ ] Vorteile:
  - Cache: Go backend cached responses (HTTP/3 reverse proxy, R9)
  - Streaming: Go backend kann SSE/WebSocket durch den tunnel streamen
  - Security: browser braucht keinen direkten zugriff auf remote target
  - Monitoring: Go backend sieht allen traffic → analytics
  - Connection management: SSH session persistent, nicht pro-request
- [ ] Implementation:
  - `golang.org/x/crypto/ssh` für SSH tunnel
  - `net.Dial` via SSH client → `sshClient.Dial("tcp", "localhost:3079")`
  - HTTP reverse proxy mit custom Dialer
  - Connection pool: eine SSH session per project, reused für alle requests
  - Keep-alive: heartbeat alle 30s
  - Reconnect: automatischer reconnect bei disconnect

### 3. E2E Deployment (Auto-Generate Dockerfiles + Compose)
- [ ] Statt für jedes projekt den deployment code zu schreiben:
  - User wählt "E2E Deploy" im project → wählt deployment type (DSH, Claude Code, terminal)
  - JiMesh generiert automatisch:
    1. Dockerfile im target path (basiert auf deployment schema + addons)
    2. docker-compose.yml (oder erweitert bestehende)
    3. Config files (z.B. opencode.json, vconfig.json) mit mesh provision
    4. Environment file (.env) mit API keys
  - All via SSH direkt auf dem remote target geschrieben
- [ ] Workflow:
  1. User: "Create E2E deployment for DSH in ~/projects/my-app"
  2. Backend: SSH → `ls ~/projects/my-app` → checkt ob compose file existiert
  3. Wenn ja: liest compose, fügt DSH service hinzu, schreibt zurück
  4. Wenn nein: generiert neue docker-compose.yml mit DSH service
  5. Generiert Dockerfile basierend auf schema (base image + addons)
  6. Generiert config files (vconfig.json mit mesh provision)
  7. Schreibt alles via SSH in den target path
  8. Startet: `docker compose up -d` via SSH
  9. Verbindet iframe tunnel zum neuen service port
- [ ] Schema-driven generation:
  - Base medium schema (terminal/dsh/opencode) → base Dockerfile
  - Addon schemas (claude-code, aider) → additional packages + config
  - User overrides → env vars, custom packages
  - Template engine: Go text/template oder embedded templates
- [ ] Templates:
  - `templates/dockerfile/dsh.tmpl`
  - `templates/dockerfile/terminal.tmpl`
  - `templates/compose/service.tmpl` (fügt service block in compose ein)
  - `templates/config/opencode.json.tmpl`
  - `templates/config/vconfig.json.tmpl`
  - Variablen: `{{.ProjectID}}`, `{{.Port}}`, `{{.RemotePath}}`, `{{.MeshEndpoint}}`, `{{.APIKey}}`

### 4. JiMesh als Bridge für Connectors + Monitoring
- [ ] JiMesh backend ist die zentrale bridge:
  - SSH tunnel für iframe content (port detection + forwarding)
  - SSH tunnel für agent tool traffic (OpenAI API proxy durch tunnel)
  - Monitoring: alle requests durch den tunnel werden geloggt
  - Auto-provision: mesh endpoints werden in config files geschrieben
  - E2E deployment: docker files werden generiert und deployed
  - Health check: periodic SSH health check für deployments
- [ ] Connector registry:
  - JiMesh kennt connectors: DSH, Claude Code, OpenCode, Aider, terminal
  - Jeder connector hat: deploy template, config template, port mapping
  - User registriert neuen connector → JiMesh generiert templates
- [ ] Monitoring bridge:
  - `GET /api/projects/{id}/monitoring` — live stats vom remote target
  - CPU, memory, disk via SSH (`top`, `df`, `free`)
  - Container stats via SSH (`docker stats --no-stream`)
  - Log tail via SSH (`docker compose logs --tail 100`)
  - SSE stream für live updates

### 5. Streaming durch SSH Tunnel
- [ ] WebSocket support durch SSH tunnel:
  - Go backend upgrade zu WebSocket → tunnel via SSH → remote target
  - Bidirectional: browser ↔ Go ↔ SSH ↔ remote
  - Use case: terminal (xterm.js), DSH chat, live logs
- [ ] SSE support:
  - Go backend fetched SSE vom remote → re-streamed to browser
  - Cache: Go backend cached chunks für iframe resume (R9 HTTP/3)
- [ ] HTTP/3 (QUIC):
  - Browser ↔ Go backend über HTTP/3 (0-RTT, multiplexing)
  - Go backend ↔ remote target über SSH tunnel (TCP)
  - Best of both: fast client connection + secure tunnel

## Architecture Overview
```
Browser (iframe + xterm.js)
    ↕ HTTP/3 (0-RTT, QUIC)
JiMesh Go Backend
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
    └── Mesh endpoints (JiMesh proxy :9091)
```

## Output Format
1. SSH tunnel architecture (Go als proxy, connection pool, keep-alive)
2. Port detection API + frontend integration
3. E2E deployment flow (schema → templates → SSH write → docker compose up)
4. Connector registry design
5. Monitoring bridge (live stats via SSH)
6. WebSocket/SSE through tunnel

---

Hier ist die vollständige Systemspezifikation und das Architektur-Design für das Modul R11 — Port Detection + SSH Tunnel Bridge + E2E Deployment. Dieses Modul macht den JiMesh Go Core zur zentralen, sicheren Netzwerk- und Deployment-Brücke zwischen dem Browser-Frontend und den Remote-Target-Boxen.1. SSH Tunnel Bridge Architecture (Go als Proxy)Anstatt dass der Browser iFrames oder WebSockets direkt vom Remote-Ziel lädt, terminiert der JiMesh Go Core alle Client-Verbindungen über HTTP/3 (QUIC) und leitet den Traffic über einen langlebigen, multiplexierten SSH-Tunnel-Pool (golang.org/x/crypto/ssh) weiter [2601.13671].┌──────────────────────────────┐
│  Browser (iFrame / xterm.js) │
└──────────────┬───────────────┘
               │
               ▼ HTTP/3 QUIC (0-RTT, Multi-Streaming, R9)
┌────────────────────────────────────────────────────────┐
│  JiMesh Go Backend Proxy                               │
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
Engine-Implementierung: Connection Pool & Custom DialerDer Go-Core hält pro Projekt genau eine ssh.Client-Verbindung offen. Der HTTP-Reverse-Proxy überschreibt den DialContext des Standard-Transports, um Datenströme direkt in den SSH-Kanal zu injizieren:gopackage network

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
			// Leitet den HTTP-Traffic direkt durch den SSH-Tunnel auf localhost des Targets
			return sshClient.Dial("tcp", "127.0.0.1:"+targetPort)
		},
	}
	return proxy, nil
}
2. Port Detection via SSHDer Go-Core führt über den SSH-Kanal ein leichtgewichtiges Parsing nativer Linux-Netzwerktools aus, um offene Ports und die dahinterliegenden Prozesse zu identifizieren, ohne dass nmap installiert sein muss.Ausgeführter Befehl: ss -tlnp || netstat -tlnpAPI-Schnittstelle (GET /api/projects/{id}/ports):json[
  { "port": 3079, "process": "dsh", "pid": 89412, "status": "in_use" },
  { "port": 7681, "process": "ttyd", "pid": 89500, "status": "in_use" },
  { "port": 8080, "process": "node", "pid": 0, "status": "free" }
]
Frontend-Integration:Im Deployment-Konfigurations-Panel rendert das Dashboard einen Port-Picker. Erkennt die Pipeline bekannte Ports (z. B. 3079 für DSH), wird der Deployment-Typ automatisch vorausgewählt. Belegte Ports erhalten ein visuelles Warn-Badge (In Use by: DSH), freie Ports werden grün markiert.3. E2E Deployment Flow (Schema-Driven)JiMesh automatisiert das Erzeugen von Infrastruktur-Code auf dem Remote-Ziel basierend auf der in R9 definierten hierarchischen Schichten-Komposition (Base Medium + Addons).[User triggers E2E Deploy]
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
Go-Template-Beispiel für ein geschichtetes Dockerfile (templates/dockerfile.tmpl):dockerfile# Base Medium Selection
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

# Addon Layer: JiMesh Auto-Provision Config Invalidation
{{if .HasAddon "jimesh-mesh"}}
COPY jimesh-provision.json /root/.config/jimesh/config.json
{{end}}

EXPOSE {{.Port}}
CMD ["/bin/bash"]
4. Connector Registry DesignDie Connector Registry ist die Single Source of Truth im Go-Core, die definiert, wie spezifische Applikationen gebaut, provisioniert und überwacht werden.gotype Connector struct {
	ID             string            `json:"id"`           // "claude-code", "dsh", "aider"
	Name           string            `json:"name"`         // "Claude Code CLI"
	DefaultPort    int               `json:"default_port"` // 7681
	DockerfileTmpl string            `json:"-"`            // Eingebettetes Go-Template
	ConfigTmpl     string            `json:"-"`            // z.B. vconfig.json Template
	EnvPresets     map[string]string `json:"env_presets"`  // Standard-ENVs
}
5. Monitoring BridgeDie Monitoring-Schnittstelle aggregiert Systemdaten der Remote-Box über periodische, nicht-interaktive SSH-Befehle und streamt diese per Server-Sent Events (SSE) an das DSH-Frontend, um R1-Dashboard-Widgets ohne Agenten-Overhead auf dem Zielsystem zu füttern.Host-Metriken: free -m (Memory), df -h (Disk), top -bn1 | grep "Cpu(s)" (CPU)Container-Metriken: docker stats --no-stream --format '{"container":"{{.Name}}","cpu":"{{.CPUPerc}}","mem":"{{.MemPerc}}"}'Log-Streaming: docker compose logs --tail=100 -f wird direkt in den SSE-Kanal geschleift.6. WebSocket & SSE Streaming durch den TunnelDa WebSockets und Server-Sent Events (SSE) für die interaktive Nutzung von Terminals (xterm.js) und Live-Chats zwingend erforderlich sind, unterstützt der SSH-Dialer volles Verbindungs-Upgrading:WebSocket-Upgrade: Kommt ein HTTP-Request mit Upgrade: websocket am JiMesh-Proxy an, führt der Go-Core das Hijacking der HTTP-Verbindung lokal durch.TCP-Tunneling: Die Rohdaten-Pakete des WebSockets werden byte-genau über den bestehenden SSH-Kanal (sshClient.Dial) an den Remote-Port (z. B. ttyd auf Port 7681) gestreamt.HTTP/3-Vorteil: Clientseitig profitiert die WebSocket-Verbindung vom schnellen HTTP/3-Multiplexing. Bricht die Browser-Verbindung kurz ein (iFrame-Verschiebung im Grid), fängt der JiMesh-Proxy den HTTP/3-Stream-Reset ab, während die dahinterliegende SSH-Verbindung zum Remote-Ziel vollkommen stabil und unangetastet bleibt (Session Preservation).Möchtest du als Nächstes die vollständige Go-Implementierung des WebSocket-Connection-Hijackers (TASK-3.6) sehen, der die Datenströme zwischen HTTP/3 und dem SSH-Kanal vermittelt, oder sollen wir die Go-Unit-Tests für den SSH-Port-Parser schreiben?