---
okf_version: "1.0"
id: "okf-str-aud-r32-claude-handoff-document"
title: "ARCHITECTURAL HANDOFF DOCUMENT FOR CLAUDE (Sprint 34 Transition)"
topic: "strategy-audits-and-decisions"
subtopic: "audits-and-handoffs"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - audits-and-handoffs
summary: "---"
---

# ARCHITECTURAL HANDOFF DOCUMENT FOR CLAUDE (Sprint 34 Transition)

---
**Date:** September 11, 2026
**Status:** System restored, 100% secured, Zero-Port / Zero-Trust architecture fully active.
**Target Node:** `[REDACTED-TS-IP]` (Remote WAN IP: `[REDACTED-WAN-IP]`, User: `[REDACTED-USER]`, Passwordless SSH Key Trust established).

---

## 🎯 1. Executive Summary for Claude
This repository recently went through a series of critical security incidents and major networking overhauls.
The immediate objective is to help the operator **safely deploy Workspaces** (GoTTY, DeepSeek-Harness, VNCs) over SSH to remote hosts **without exposing any host ports to the public internet** or modifying host-level security configurations recursively.

The **Zero-Port Architecture** is now fully coded, compiled, and active.

---

## 🔒 2. Current Active Architecture (Zero-Port Mesh)

### A. The Inbound Security Solution (No Exposed Ports)
*   **The Problem:** Standard Docker `-p` bindings bypass UFW/iptables, exposing container ports to the public internet.
*   **The Fix:** All host-level port publishing flags (`-p`) have been **completely stripped** from all deployment commands in `projects_ssh.go`.
*   **The Flow:**
    1.  When a Workspace is deployed, the container boots on the remote server with **zero published ports**, making it 100% invisible to external port scans.
    2.  The Go backend executes a `docker inspect` command over SSH to query the container's isolated, internal Docker network IP (e.g., `172.x.x.x`).
    3.  This internal IP is parsed and persisted in the database settings (`ssh_<projectID>_internal_ip`).
    4.  When the operator opens the dashboard, the Reverse Proxy Tunnel Pool (`network.Pool`) uses SSH to establish a channel and **direct-dials the container's internal IP and port 3080 directly inside the SSH connection**:
        ```go
        client.Dial("tcp", fmt.Sprintf("%s:%s", internalIP, targetPort))
        ```
    5.  This tunnels the entire HTTP and WebSocket stream securely to the local browser iframe, requiring **zero open ports on the host** other than the standard, protected port 22 (SSH).

### B. The Outbound Security Solution (NAT Isolation)
*   Containers use gVisor's native **Netstack** (Go-based user-space network stack) or standard Docker NAT for outbound egress traffic (to run package managers, curl APIs, or clone repos) while keeping incoming traffic physically blocked at the socket level.

---

## 📁 3. Workspace File Integrity & Recent Core Changes

### A. Backend Code modified and verified:
1.  **`src/backend/internal/deploy/projects_ssh.go`**
    *   Removed all `-p` port mappings from `docker run` statements.
    *   Appended `docker inspect` parsing routines to save the container's internal IP.
    *   **Strict SSH Guard:** Added a defensive filter inside the permissions helper `openmesh_ws_perms` to ensure it completely skips `.ssh` directories and returns `0` immediately when `/root` or `/` is passed, preventing SSH lockout.
2.  **`src/backend/internal/deploy/tunnel.go` & `src/backend/internal/network/tunnel.go`**
    *   Updated the `GetReverseProxy` method to support direct-dialing into the captured internal IP.
    *   Implemented secure token query parameter-based authentication (`?token=...`) to support secure iframe upgrades.
    *   Integrated native Go SSH Agent (`SSH_AUTH_SOCK`) support inside the tunnel pool to query local keys from memory instead of reading cleartext passwords/keys from PostgreSQL.
3.  **`src/frontend/src/views/ProjectsPage.tsx`**
    *   Restored direct iframe loads, querying over the local secure proxy tunnel.
    *   Appended the active Keycloak authentication token as a query parameter.
4.  **`src/frontend/vite.config.ts`**
    *   Enabled **`ws: true`** inside proxy blocks to ensure all WebSocket handshakes are forwarded correctly to the backend, fixing black terminal screens.

---

## 📋 4. Sprints & Next Steps for Claude

We have documented the exact next steps and architectural blueprints in:
*   📄 `docs/research/R31-comprehensive-gvisor-docker-networking-ssh-ufw-security-guide.md`
*   📄 `docs/sprints/SPRINT-34-MESH-TUNNELS-AND-ROUTING.md`

### Nächste To-Dos:
1.  **Global Renaming:** Rename all occurrences of "Projects" to **"Workspaces"** globally (PostgreSQL tables, REST APIs `/api/workspaces`, Go structs, and React pages).
2.  **Network Tab Implementation:** Create a dedicated "Networks" tab in the React sidebar to serve as the visual configurator for future gVisor Netstack networks and shared filesystem volumes (Scanopy).
3.  **NO ROOT SHELLS / SECURE CREDENTIALS:** Do NOT run any recursive chown/chmod scripts on the host, do not disable UFW, and do not unban IPs. Let the Zero-Port SSH Tunnel do all the work securely.
