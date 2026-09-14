---
okf_version: "1.0"
id: "okf-gen-master-entity-and-relation-index"
title: "Master Entity & Relation Knowledge Graph Index"
topic: "general"
subtopic: "taxonomy-index"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - knowledge-graph
  - entities
  - relations
  - okf-index
summary: "Comprehensive Master Entity and Relation Index cataloging technical systems, protocols, repositories, and architectural dependencies across the Open Knowledge Base."
---

# Master Entity & Relation Knowledge Graph Index

## Executive Summary

This Master Entity and Relation Index maps all key technical entities, software libraries, network protocols, security frameworks, and public repository projects across the **Open Knowledge Base (OKF v1.0)**. It serves as a structural GraphRAG entity extraction matrix and cross-reference catalog.

---

## 1. Domain Taxonomy & Document Catalog

```
knowledge/general/
├── agent-systems-and-browser-automation/
│   ├── browser-automation/
│   ├── framework-evaluations/
│   └── skills-and-memory/
├── analytics-and-telemetry/
│   ├── mesh-endpoints/
│   └── metrics-and-pipelines/
├── container-runtime-security/
│   ├── mcp-integrations/
│   ├── sandboxing/
│   └── terminal-workspaces/
├── frontend-and-ui-architecture/
│   ├── dashboard-and-widgets/
│   └── performance-and-rendering/
├── identity-and-access-control/
│   └── idp-integration/
├── llm-orchestration-and-routing/
│   ├── agent-architectures/
│   ├── cdc-and-synthesis/
│   └── routing-algorithms/
├── networking/
│   ├── container-networking/
│   ├── security-and-firewalls/
│   ├── tunnels-and-discovery/
│   └── vpn-and-overlay/
└── security-and-observability/
    ├── guardrails-and-firewalls/
    └── siem-and-monitoring/
```

---

## 2. Primary Entity Registry

| Entity Name | Category / Type | Scope & Description | Source Repositories / References |
|---|---|---|---|
| **OPNsense** | Network Appliance | Open-source firewall platform with REST API and Kea DHCP | `opnsense-api-client`, `opnsense-helper`, `opnsense-scripts-autodocs` |
| **Open vSwitch (OVS)** | Network Virtualization | Programmable multilayer virtual switch for VLAN isolation | `ovs-bridge-collection` |
| **Foreman & Katello** | Bare-Metal Provisioning | Systems lifecycle management, TFTP/DHCP, and PXE discovery | `RHEL_9_Foreman_Guide` |
| **HashiCorp Vault** | Secrets Management | Zero-Trust secret storage and AppRole authentication | `DevOps`, `onpremctl` |
| **Tailscale** | VPN / Overlay Mesh | WireGuard-based zero-config mesh overlay network | `onpremctl` |
| **BIND9 & Kea DHCP** | IPAM / DNS Services | Enterprise DNS with TSIG dynamic updates and Kea DHCP | `Network-Guides` |
| **gVisor** | Container Sandbox | Application kernel sandbox emulating Linux syscalls | `general/container-runtime-security/sandboxing/` |
| **eBPF (Tetragon/Falco)**| Kernel Observability | Boundary tracing, uprobes on SSL, and syscall filtering | `general/security-and-observability/guardrails-and-firewalls/` |
| **SharkGuard** | LLM Guardrail | Sub-millisecond regex sanitizer & ONNX DistilBERT sandbox | `SharkGuard` |
| **S-ANFIS** | Neuro-Fuzzy ML | State-Adaptive Neuro-Fuzzy Inference System in PyTorch | `S-ANFIS-PyTorch`, `anfis-pytorch` |
| **Proof of Thought** | Neurosymbolic Reasoning| Z3 SMT solver program synthesis for verifiable reasoning | `proofofthought` |
| **DAP (Dynamic Agent Protocol)**| Agent Protocol | Decoupled 3-layer dynamic tool discovery and execution | `clean-agent-harness`, `dap-docs` |
| **ji_ui** | UI Framework | gRPC-driven binary stream UI framework for React and Web | `ji_ui`, `ji_ui_react_example` |
| **ji-GPU-Particles** | WebGL Rendering | Three.js GPU-driven particle system using GLSL instancing | `ji-GPU-Particles` |
| **kooljs** | Web Animation | Multithreaded Web Worker animation engine | `kooljs`, `kooljs-website` |
| **Kubyplexer & Kubehistory**| Kubernetes Tools | In-IDE mouse cluster navigation and shell execution | `kubyplexer`, `kubehistory` |
| **Model Context Protocol (MCP)**| AI Tool Standard | Open standard for connecting LLMs to external tools | `Gmail-MCP-Server`, `pinecone-bridged-mcp`, `ollama-mcp-client` |
| **Google TabFM** | Tabular AI Model | Zero-shot tabular foundation model with 2D attention | `https://github.com/google-research/tabfm` |
| **CropPulse** | Satellite Remote Sensing | Sentinel-2 vegetation index extraction with LightGBM | `CropPulse-Hackathon1` |

---

## 3. Entity Architectural Relations

```
+-----------------------------------------------------------------------------------+
| Architectural Dependency Graph                                                    |
+-----------------------------------------------------------------------------------+
| [User / Client] ---> [Identity Proxy / Tailscale Overlay]                         |
|                           |                                                       |
|                           v                                                       |
| [OPNsense / OVS Bridge] ---> [gVisor Container Sandbox]                            |
|                                    |                                              |
|                                    v                                              |
| [Clean Agent Harness / DAP] ---> [SharkGuard / eBPF Kernel Guard]                 |
|                                    |                                              |
|                                    v                                              |
| [LLM Routing / S-ANFIS] ---> [Proof of Thought (Z3 Solver)]                       |
|                                    |                                              |
|                                    v                                              |
| [OpenSearch / SIEM Engine] <--- [Suricata EVE / Vector Log Pipeline]              |
+-----------------------------------------------------------------------------------+
```

---

## Sources & References

- All specifications under `general/` and `skills/` directories in this knowledge base.
