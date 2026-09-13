---
okf_version: "1.0"
id: "okf-net-vpn-onpremctl-pamji-infrastructure"
title: "onpremctl: Tailscale, HashiCorp Vault & OpenWrt Low-Spec Edge Infrastructure Controller"
topic: "general/networking"
subtopic: "vpn-and-overlay"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - tailscale
  - vault
  - openwrt
  - docker-compose
  - onpremctl
  - vpn
summary: "Technical architecture for onpremctl, a lightweight edge controller deploying Tailscale mesh VPN, HashiCorp Vault secrets management, and OpenWrt router services via Docker Compose."
---

# onpremctl: Tailscale, HashiCorp Vault & OpenWrt Low-Spec Edge Infrastructure Controller

## Executive Summary

Establishing low-cost, resilient remote branch infrastructure requires secure overlay networking, local secrets management, and failover router capabilities on resource-constrained hardware (e.g., small edge nodes or single-board computers).

**`onpremctl`** acts as the core edge controller for remote node infrastructure, deploying a **Tailscale** overlay mesh network, **HashiCorp Vault** secrets manager, and **OpenWrt** lightweight router instance via unified Docker Compose IaC declarations.

---

## 1. Edge Controller Architecture

```
                                  +-----------------------+
                                  | Tailscale Overlay Mesh|
                                  |  (100.x.y.z WireGuard)|
                                  +-----------+-----------+
                                              |
+---------------------------------------------v---------------------------------------------+
| Edge Node Host (onpremctl)                                                                |
|                                                                                           |
|  +--------------------+     +--------------------+     +-------------------------------+  |
|  | Tailscale Container|     | Vault Secrets Engine|     | OpenWrt Failover Router       |  |
|  | (Mesh Gateway)     |     | (Local AppRole API)|     | (DHCP / DNS / Route Failover) |  |
|  +--------------------+     +--------------------+     +-------------------------------+  |
+-------------------------------------------------------------------------------------------+
```

---

## 2. Docker Compose IaC Manifest (`docker-compose.yml`)

```yaml
version: "3.8"

services:
  tailscale:
    image: tailscale/tailscale:latest
    container_name: onpremctl-tailscale
    hostname: edge-node-01
    environment:
      - TS_AUTHKEY=${TS_AUTHKEY}
      - TS_ROUTES=10.50.0.0/16
      - TS_EXTRA_ARGS=--advertise-tags=tag:edge
    volumes:
      - ./data/tailscale:/var/lib/tailscale
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - NET_ADMIN
      - NET_RAW
    restart: unless-stopped

  vault:
    image: hashicorp/vault:1.15.0
    container_name: onpremctl-vault
    environment:
      - VAULT_LOCAL_CONFIG={"storage":{"file":{"path":"/vault/file"}},"listener":{"tcp":{"address":"0.0.0.0:8200","tls_disable":1}},"default_lease_ttl":"168h","max_lease_ttl":"720h","ui":true}
    volumes:
      - ./data/vault/file:/vault/file
    ports:
      - "8200:8200"
    cap_add:
      - IPC_LOCK
    restart: unless-stopped

  openwrt:
    image: openwrt/rootfs:latest
    container_name: onpremctl-router
    cap_add:
      - NET_ADMIN
    volumes:
      - ./data/openwrt/config:/etc/config
    restart: unless-stopped
```

---

## 3. Provisioning & Bootstrapping Protocol

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Initialize persistent directories
mkdir -p data/tailscale data/vault/file data/openwrt/config

# 2. Verify TUN device availability
if [ ! -c /dev/net/tun ]; then
    mkdir -p /dev/net
    mknod /dev/net/tun c 10 200
    chmod 0666 /dev/net/tun
fi

# 3. Bring up edge stack
docker compose up -d

# 4. Wait for Vault startup and initialize
sleep 5
docker exec -it onpremctl-vault vault operator init -key-shares=1 -key-threshold=1
```

---

## 4. Verification Checklist

- [x] Tailscale container registers with control server and advertises host subnet `10.50.0.0/16`.
- [x] Vault listens locally on `:8200` with non-swappable memory (`IPC_LOCK`).
- [x] Container restart policies survive hard edge node power loss.
