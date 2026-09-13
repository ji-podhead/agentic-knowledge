---
id: "R29"
title: "R29: gVisor Networking, NAT Control, and SSH Agent Forwarding Overhaul"
type: research
date: 2026-09-11
status: final
tags: [ssh, mesh, gvisor, docker]
license: CC-BY-4.0
---

# R29: gVisor Networking, NAT Control, and SSH Agent Forwarding Overhaul

## 1. Executive Summary
The user requested a massive architectural change to resolve ongoing Docker networking isolation issues (where workspace containers could not reach the `jimesh` gateway) and SSH authentication issues (where the backend required direct access to private key files).

The goal is to:
1. **Implement gVisor (`runsc`)** for granular network isolation and NAT control.
2. **Introduce a "Network" Tab** in the UI to let operators define network topologies per project.
3. **Migrate to SSH Agent Forwarding** to remove the dangerous `/home/ji/.ssh` volume mount, ensuring private keys never enter the Docker container.

## 2. Database Schema Updates
To support dynamic networking, the `projects` table must be expanded in `src/backend/internal/store/store.go`:
```sql
ALTER TABLE projects ADD COLUMN network_mode TEXT DEFAULT 'isolated'
ALTER TABLE projects ADD COLUMN enable_nat INTEGER DEFAULT 1
```

*   `network_mode`: `isolated` (creates a dedicated bridge), `jimesh-net` (attaches to the gateway's network), `none` (total isolation).
*   `enable_nat`: If 0, the container is deployed without outbound NAT (enforced via gVisor or Docker `--internal`).

## 3. SSH Agent Forwarding (Docker Compose)
Currently, `docker-compose.yml` mounts the host's `.ssh` directory. This violates zero-trust principles. We will transition to SSH Agent forwarding:

**Changes to `docker-compose.yml` (`jimesh` service):**
*   Remove: `- /home/ji/.ssh:/root/.ssh:ro`
*   Add Volume: `- ${SSH_AUTH_SOCK:-/tmp/ssh-agent}:/ssh-agent`
*   Add Env: `SSH_AUTH_SOCK=/ssh-agent`

This allows the Go `ssh.Dial` client to automatically request signatures from the host's running SSH Agent, without ever seeing the private keys.

## 4. Deployment Logic Updates (`projects_ssh.go`)
The Go deployment pipeline must parse the new `network_mode` and `enable_nat` flags, utilizing the mechanisms outlined in `docs/reference/gvisor/networking.md`:
1.  **Network Attachment:** 
    *   If `network_mode == "jimesh-net"`, append `--network jimesh_jimesh-net` to the `docker run` command.
    *   If `network_mode == "none"`, append `--network none` (which gVisor handles natively per `networking.md`).
    *   If `network_mode == "host"`, append `--network host` (requires gVisor runtime configuration adjustments for host passthrough).
2.  **gVisor Integration:** Append `--runtime=runsc` to all workspace containers. 
3.  **NAT Control:** If `enable_nat == 0`, we will isolate the container completely or use `--network none` combined with gVisor's native isolation, ensuring absolute containment.
4.  **Universal JiMesh Access:** The `jimesh` gateway container stays securely on `jimesh-net`. It will act as the single proxy/gateway for all projects attached to this network.

## 5. Frontend Updates (`ProjectsPage.tsx`)
A new "Network" tab will be added to the project creation and edit modals.
*   **Tabs Array:** Expand the existing `Pane Tabs` to include a `Network` tab.
*   **Controls:**
    *   Dropdown: Network Mode (Isolated Bridge, JiMesh Shared Network, Airgapped/None).
    *   Toggle: Enable Outbound NAT.

## Next Steps
Once this plan is acknowledged and finalized, we will exit plan mode and execute these changes surgically across the `docker-compose.yml`, Go backend (`store.go`, `projects_ssh.go`), and React frontend.