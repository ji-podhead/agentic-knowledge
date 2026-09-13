---
okf_version: "1.0"
id: "okf-con-ter-rhel9-foreman-katello-provisioning"
title: "RHEL 9 Foreman & Katello Automated Bare-Metal Discovery, TFTP/DHCP & PXE Provisioning"
topic: "general/container-runtime-security"
subtopic: "terminal-workspaces"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - foreman
  - katello
  - pxe-boot
  - rhel9
  - dhcp
  - tftp
  - bare-metal
summary: "Comprehensive architecture and deployment blueprint for RHEL 9 Foreman with Katello lifecycle management, TFTP/DHCP SmartProxy orchestration, and automated FDI PXE discovery."
---

# RHEL 9 Foreman & Katello Automated Bare-Metal Discovery, TFTP/DHCP & PXE Provisioning

## Executive Summary

Managing bare-metal infrastructure and hypervisor lifecycles requires centralized discovery, automated OS provisioning, software content management, and configuration enforcement. **Foreman**, coupled with **Katello** and the **Foreman Discovery Plugin**, provides end-to-end lifecycle orchestration.

This document details the architecture, network prerequisites, PXE boot sequence, and SmartProxy orchestration steps for deploying Foreman on Red Hat Enterprise Linux 9 (RHEL 9).

---

## 1. Network Architecture & PXE Boot Flow

```
+------------------+         DHCP Discover        +-------------------+
| Target Bare-Metal| ---------------------------> | Foreman Server    |
| (PXE Client)     | <--------------------------- | (DHCP SmartProxy) |
+--------+---------+    Offer: IP + Opt 66/67     +---------+---------+
         |                                                  |
         | TFTP Get PXELinux / Kernel / Initrd              |
         +------------------------------------------------->| (TFTP SmartProxy)
         |                                                  |
         | Boots FDI (Foreman Discovery Image)              |
         +------------------------------------------------->| Registers Node via
                                                            | REST API (Port 443)
```

### 1.1 PXE Boot Prerequisites
1. **Option 66 (Next-Server)**: Points to the Foreman SmartProxy TFTP IP address (`10.50.0.10`).
2. **Option 67 (Bootfile-Name)**:
   - BIOS systems: `pxelinux.0` / `grub2/bootloader.0`
   - UEFI systems: `grub2/shim.efi`

---

## 2. RHEL 9 Foreman & Katello Installation

### 2.1 Repository & Package Setup

```bash
# Register RHEL 9 system and enable required repositories
subscription-manager register --auto-attach
subscription-manager repos --enable=rhel-9-for-x86_64-baseos-rpms \
                           --enable=rhel-9-for-x86_64-appstream-rpms

# Install Foreman and Katello release RPMs
dnf install -y https://yum.theforeman.org/releases/3.10/el9/x86_64/foreman-release.rpm
dnf install -y https://yum.theforeman.org/katello/4.12/katello/el9/x86_64/katello-ca-consumer-latest.noarch.rpm
```

### 2.2 Unattended Installer Execution

Execute the installer scenario enabling Katello, DHCP, TFTP, and Discovery:

```bash
foreman-installer --scenario katello \
  --initial-organization "Enterprise-Infra" \
  --initial-location "Datacenter-01" \
  --foreman-initial-admin-username admin \
  --foreman-initial-admin-password [REDACTED_SECRET] \
  --module-foreman-proxy-plugin-discovery true \
  --foreman-proxy-dhcp true \
  --foreman-proxy-dhcp-managed true \
  --foreman-proxy-dhcp-interface eth0 \
  --foreman-proxy-dhcp-range "10.50.10.100 10.50.10.250" \
  --foreman-proxy-dhcp-gateway "10.50.0.1" \
  --foreman-proxy-tftp true \
  --foreman-proxy-tftp-managed true \
  --foreman-proxy-dns true
```

---

## 3. Auto-Discovery & Provisioning Rules

When unknown bare-metal nodes boot via PXE, they execute the **Foreman Discovery Image (FDI)** in memory, reporting hardware facts (CPU count, RAM, disk layout, MAC addresses) back to Foreman Core.

### 3.1 Automated Provisioning Rule Example

Create an automated discovery rule matching hosts based on memory and CPU count:

```bash
hammer discovery-rule create \
  --name "Auto-Provision-KVM-Hypervisors" \
  --search "cpu_count >= 16 and memory_mb >= 65536" \
  --hostgroup "Hypervisors/RHEL9" \
  --hostname "kvm-node-\${mac//:/}.infra.internal" \
  --enabled true \
  --priority 10
```

---

## 4. Verification & Diagnostics

- [x] **SmartProxy Health**: `curl -k https://127.0.0.1:9090/features` returns `["dhcp", "dns", "tftp", "discovery"]`.
- [x] **TFTP Verification**: `tftp 10.50.0.10 -c get pxelinux.0` succeeds.
- [x] **Discovered Hosts Ingestion**: Discovered nodes appear under `hammer discovery list`.
