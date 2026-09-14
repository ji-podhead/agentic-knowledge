---
okf_version: "1.0"
id: "okf-infra-prov-foreman-pxe"
title: "Bare-Metal Provisioning with Foreman: PXE, DHCP, TFTP, and Discovery"
topic: "infrastructure-automation"
subtopic: "provisioning"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags: [foreman, pxe, provisioning, katello, infrastructure]
summary: "Complete lifecycle management: PXE boot, DHCP/TFTP, auto-discovery, and bare-metal provisioning."
---

# Bare-Metal Provisioning with Foreman

## Problem
Provisioning physical servers manually (OS install, network config, hostname) doesn't scale and is error-prone.

## Approach
Foreman provides lifecycle management:
- **Provisioning:** PXE boot chain (DHCP → TFTP → Boot Image → OS install)
- **Discovery:** Auto-detect new hosts on the network
- **Configuration:** Puppet for desired-state management
- **Content:** Katello for repository and errata management

## Key Components
- PXE boot process: DHCP offers → TFTP downloads boot image → bootloader runs
- Foreman SmartProxy: handles DHCP, TFTP, DNS for the provisioning network
- OMAPI key (HMAC-MD5): allows DHCP lease sharing between Foreman and external DHCP servers
- RNDC key: allows Foreman to manage external BIND DNS for dynamic updates

## Trade-offs
- Foreman+Katello is heavyweight (~8GB RAM minimum for Katello)
- For smaller setups, plain PXE + Kickstart may suffice
- Proxmox as compute resource adds another layer (nested virtualization)

## References
- [ji-podhead/RHEL_9_Foreman_Guide](https://github.com/ji-podhead/RHEL_9_Foreman_Guide)
- [Foreman Documentation](https://theforeman.org/docs/)
