---
id: "skill-utility-dependencies"
title: "Utility-Project-Dependencies: WAF, Firewall, Networks, Vault, SIEM, RBAC"
type: skill
date: 2026-09-15
status: final
tags: [utility, dependencies, waf, firewall, networks, vault, siem, rbac, onboarding]
license: CC-BY-4.0
---

# Utility-Project-Dependencies Skill

## Das Schema: welche Bausteine braucht jedes User-Project?

| Baustein | Utility | User-Project braucht | Wann erstellt |
|---|---|---|---|
| WAF | Utility (Coraza) | ✅ immer | Project-Init |
| Firewall | Utility (nftables) | ✅ immer | Project-Init |
| Networks | Project-Parent | ✅ immer | Project-Init |
| Network (App) | App-Child | App kann 1 Parent-Network | App-Erstellung |
| Vault | Project | ✅ immer | Project-Init |
| gVisor | Workspace-Runtime | ✅ als Runtime | Workspace-Setup |
| OPA/RBAC | Workspace | ✅ immer | Workspace-Setup |
| SIEM | Utility | ✅ immer | Project-Init |
| CI/CD | Utility | ✅ immer | Project-Init |

## Network-Ownership

- Project = der Haupt-Parent für Networks
- App kann GENAU EIN Parent-Network haben (erbt vom Project-Network)
- Workspace hat ALLE Networks (aggregiert von Projects + Apps)
- VLANs werden MIT gVisor erstellt (macvlan/ipvlan + gVisor als Runtime)
- VLANs werden NICHT in der Firewall erstellt, KEIN OVS-Bridge
