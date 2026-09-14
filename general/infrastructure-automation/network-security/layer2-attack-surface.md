---
okf_version: "1.0"
id: "okf-infra-netsec-layer2"
title: "Layer-2 Attack Surface in Multi-VM Environments: DNS, DHCP, MAC, SSH"
topic: "infrastructure-automation"
subtopic: "network-security"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags: [network-security, layer2, dns, dhcp, suricata, ids, segmentation]
summary: "Why VMs on the same host share a Layer-2 attack surface and how to segment, detect, and protect."
---

# Layer-2 Attack Surface in Multi-VM Environments

## Problem
VMs/containers on the same physical machine share the same NIC. Even with different subnets, they can still communicate over Layer 2. A container breakout gives the attacker access to every VM on the host.

## Attack Vectors

| Vector | Attack | Impact |
|---|---|---|
| **DNS** | Cache poisoning, zone transfer, D(Do)S + IP spoofing, MITM | Phishing, credential theft, traffic redirection |
| **DHCP** | Server DDoS + spoofing, lease manipulation, rogue lease to Vault | Redirect to phishing site, MITM via HTTP router |
| **MAC Spoofing** | Bypass MAC filtering, lease exhaustion, duplicate IPs | Network breakdown, connectivity loss, overheating |
| **SSH** | Brute force, credential stuffing | Host compromise |

## Defense: Network Segmentation
- Create separate bridges for VM segments
- Forward traffic to the router, **DROP inter-bridge connections** (iptables)
- MAC-based filtering on DHCP (though spoofable, raises the bar)

## Defense: IDS with Suricata
- Multi-threaded with GPU support — handles large traffic volumes
- Signature-based + anomaly-based detection
- eBPF/XDP for kernelspace filtering, load balancing, routing
- Available as OPNsense plugin
- **Recommendation:** Use multi-WAN for IDS instead of inline routing (inline slows traffic)

## References
- [ji-podhead/DevOps](https://github.com/ji-podhead/DevOps)
- [ji-podhead/Network-Guides](https://github.com/ji-podhead/Network-Guides)
- [Suricata](https://suricata.io/)
