---
id: "skill-firewall-deployment"
title: "Firewall-Deployment: Provider-Architektur + Onboarding-Flow"
type: skill
date: 2026-09-15
status: final
tags: [firewall, opnsense, nftables, byof, onboarding, security]
license: CC-BY-4.0
---

# Firewall-Deployment Skill

## Die 4 FirewallProvider-Optionen (Sprint 20 WP6 / TASK-050)

| Provider | Status | Architektur |
|---|---|---|
| NftablesProvider | ✅ implementiert + live | Kernel-Level (nft), Router-Node |
| OPNsense/pfSense | ⬜ interface-ready | Appliance per API: VLANs, DHCP, Unbound, WireGuard |
| Cloud Security Groups | ⬜ geplant | AWS-SG / Hetzner-FW (Sprint-33) |
| BYOF | ⬜ geplant | User bringt eigene Firewall |

## Onboarding-Flow (4 Steps)

1. Welcome → 2. Worker-Node-Registrierung (SSH + gVisor) → 3. Firewall-Auswahl → 4. Erste App deployen

## Architektur-Regeln

- UFW wird NICHT angefasst (Operator-Entscheidung)
- VLANs werden MIT gVisor erstellt (nicht in der Firewall, kein OVS-Bridge)
- Jedes Project braucht eine WAF (Default = Standard-Utility-WAF)
- Third-Party-Firewall braucht ein Interface (Aikido Zen geplant)
