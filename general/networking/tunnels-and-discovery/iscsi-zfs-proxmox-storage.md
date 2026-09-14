---
okf_version: "1.0"
id: "okf-net-tun-iscsi-zfs-proxmox-storage"
title: "Enterprise Storage Architecture: iSCSI Targets, ZFS Pool Tuning & Proxmox Hypervisor Integration"
topic: "general/networking"
subtopic: "tunnels-and-discovery"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - storage
  - iscsi
  - zfs
  - proxmox
  - tgt
  - linstor
summary: "Technical guide covering iSCSI target daemon (tgt) configuration, ZFS zpool performance tuning, and Proxmox VE shared block storage integration."
---

# Enterprise Storage Architecture: iSCSI Targets, ZFS Pool Tuning & Proxmox Hypervisor Integration

## Executive Summary

High-density virtualized environments (e.g. Proxmox VE clusters) require low-latency, block-level shared storage for VM live migrations and high IOPS database workloads.

This specification details the setup of **iSCSI Targets (`tgt`)**, **ZFS Pool Tuning** (ARC cache optimization, SLOG, L2ARC), and native **Proxmox VE ZFS-over-iSCSI** storage integrations.

---

## 1. iSCSI Target Configuration (`/etc/tgt/conf.d/iscsi.conf`)

```target
<target iqn.2026-09.internal.infra:storage.target01>
    # Expose ZFS zvol block device
    backing-store /dev/zvol/tank/proxmox-vol01

    # Restrict access to Proxmox Initiator IPs
    initiator-address 10.50.0.21
    initiator-address 10.50.0.22

    # Authentication
    incominguser pve_initiator [REDACTED_SECRET]
</target>
```

---

## 2. ZFS Pool Creation & Performance Optimization

```bash
# Create mirrored ZFS pool with dedicated NVMe SLOG (Write Cache) and L2ARC
zpool create -f -o ashift=12 tank mirror \
    /dev/sda /dev/sdb \
    mirror /dev/sdc /dev/sdd \
    log /dev/nvme0n1p1 \
    cache /dev/nvme0n1p2

# Set dataset properties for VM block storage
zfs set compression=lz4 tank
zfs set atime=off tank
zfs set xattr=sa tank
zfs set recordsize=128k tank
```

---

## 3. Proxmox VE ZFS-over-iSCSI Integration (`/etc/pve/storage.cfg`)

```ini
zfe: shared-iscsi-storage
    blocksize 8k
    target iqn.2026-09.internal.infra:storage.target01
    pool tank
    portal 10.50.0.15
    content images
    sparse 1
```

---

## Sources & References

- [https://github.com/ji-podhead/Network-Guides](https://github.com/ji-podhead/Network-Guides)
