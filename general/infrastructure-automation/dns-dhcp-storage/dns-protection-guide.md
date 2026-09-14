---
okf_version: "1.0"
id: "okf-infra-dns-protection"
title: "DNS Protection: TSIG, DNSSEC, and Dynamic Updates with RNDC"
topic: "infrastructure-automation"
subtopic: "dns-dhcp-storage"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags: [dns, bind9, dnssec, tsig, rndc, dhcp, storage, zfs, iscsi]
summary: "Running and protecting a private DNS: knowledge base, install, debug, dynamic updates, attack vectors, and defense."
---

# DNS Protection: A Complete Guide

## Problem
A private DNS server is a high-value target — cache poisoning, zone transfers, and D(Do)S attacks can redirect all traffic.

## Approach: Layered DNS Defense

1. **Install:** bind9 on Debian, configured to resolve private dashboard domains
2. **Debug:** dig, nameserver logs, query tracing
3. **Dynamic Updates:** RNDC key + DHCP integration — DHCP shares leases via OMAPI (HMAC-MD5) key and NFS
4. **Attack Vectors:** Zone transfers, cache poisoning, D(Do)S + IP spoofing, MITM
5. **Protection:** TSIG for authenticated transfers, DNSSEC for integrity, firewall rules

## Storage Layer
- ZFS Pools in Proxmox (NFS-mounted)
- iSCSI with SCST-Project synced to Proxmox
- DRBD for distributed replicated storage

## References
- [ji-podhead/Network-Guides](https://github.com/ji-podhead/Network-Guides)
