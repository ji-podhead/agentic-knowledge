---
okf_version: "1.0"
id: "okf-net-tun-dns-dhcp-drbd-infrastructure"
title: "Enterprise BIND9 DNS, Kea DHCP, RNDC Dynamic Updates & DRBD High Availability"
topic: "general/networking"
subtopic: "tunnels-and-discovery"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - dns
  - bind9
  - dhcp
  - drbd
  - high-availability
  - dynamic-dns
summary: "Comprehensive engineering guide for deploying BIND9 DNS with RNDC TSIG dynamic updates, Kea DHCP subnets, and DRBD block-level storage replication for HA infrastructure."
---

# Enterprise BIND9 DNS, Kea DHCP, RNDC Dynamic Updates & DRBD High Availability

## Executive Summary

Core network infrastructure relies heavily on high availability, low latency, and secure dynamic updates for Name Resolution (DNS) and IP Address Management (IPAM/DHCP). This specification outlines the deployment architecture for **BIND9 DNS** featuring **TSIG-authenticated RNDC dynamic updates**, **Kea DHCP** multi-subnet pooling, and block-level active-passive state replication via **DRBD (Distributed Replicated Block Device)** for zero-data-loss failover.

---

## 1. BIND9 DNS & RNDC Dynamic Update Configuration

Dynamic DNS (DDNS) allows authorized DHCP servers or orchestration agents to dynamically inject forward (`A`/`AAAA`) and reverse (`PTR`) records into authoritative BIND9 zones.

### 1.1 Generating TSIG Keys & BIND Configuration

```bash
# Generate HMAC-SHA256 TSIG key for dynamic updates
tsig-keygen -a hmac-sha256 rndc-dhcp-key > /etc/bind/rndc-dhcp-key.key
```

Include the generated key in `/etc/bind/named.conf.local` and define zone update permissions:

```named
include "/etc/bind/rndc-dhcp-key.key";

zone "infra.internal" {
    type master;
    file "/var/lib/bind/db.infra.internal";
    allow-update { key "rndc-dhcp-key"; };
};

zone "10.in-addr.arpa" {
    type master;
    file "/var/lib/bind/db.10.in-addr.arpa";
    allow-update { key "rndc-dhcp-key"; };
};
```

### 1.2 Programmatic NSUpdate Ingestion

```bash
# Execute authenticated dynamic update test
nsupdate -k /etc/bind/rndc-dhcp-key.key <<EOF
server 127.0.0.1
zone infra.internal
update add node-01.infra.internal. 86400 A 10.50.10.15
send
EOF
```

---

## 2. Kea DHCP Subnet & DDNS Hook Architecture

Kea DHCP replaces legacy ISC DHCP with a high-performance modular daemon.

```json
{
  "Dhcp4": {
    "interfaces-config": {
      "interfaces": ["eth0/10.50.0.1"]
    },
    "lease-database": {
      "type": "memfile",
      "persist": true,
      "name": "/var/lib/kea/kea-leases4.csv"
    },
    "subnet4": [
      {
        "subnet": "10.50.0.0/16",
        "pools": [{ "pool": "10.50.100.10 - 10.50.100.250" }],
        "option-data": [
          { "name": "routers", "data": "10.50.0.1" },
          { "name": "domain-name-servers", "data": "10.50.0.2, 10.50.0.3" }
        ]
      }
    ],
    "dhcp-ddns": {
      "enable-updates": true,
      "server-ip": "127.0.0.1",
      "server-port": 53001
    }
  }
}
```

---

## 3. High Availability via DRBD Block Storage Replication

To maintain state sync for BIND zone database journals (`.jnl`) and Kea lease storage without complex SAN hardware, **DRBD v9** provides synchronous L2/L3 kernel block replication.

```
+-------------------+                      +-------------------+
|   Primary Node    |                      |  Secondary Node   |
|   (Active DNS)    |                      |   (Standby DNS)   |
| /dev/drbd0 (RW)   |  === Synchronous === | /dev/drbd0 (RO)   |
|   /var/lib/bind   |      Replication     |   /var/lib/bind   |
+-------------------+                      +-------------------+
```

### 3.1 Resource Configuration (`/etc/drbd.d/dns_state.res`)

```drbd
resource dns_state {
    protocol C;
    net {
        verify-alg sha256;
    }
    on node1.infra.internal {
        device    /dev/drbd0;
        disk      /dev/vg0/lv_bind;
        address   10.50.0.11:7788;
        meta-disk internal;
    }
    on node2.infra.internal {
        device    /dev/drbd0;
        disk      /dev/vg0/lv_bind;
        address   10.50.0.12:7788;
        meta-disk internal;
    }
}
```

---

## 4. Verification & Diagnostics

- [x] **DNS Resolution**: `dig @10.50.0.2 node-01.infra.internal +short +dnssec`
- [x] **Dynamic Journaling**: Inspect `/var/lib/bind/db.infra.internal.jnl` using `named-checkzone`.
- [x] **DRBD Sync Status**: `drbdadm status dns_state` verified in `Established` / `SyncSource` / `SyncTarget` modes.

## Sources & References

- [https://github.com/ji-podhead/Network-Guides](https://github.com/ji-podhead/Network-Guides)
