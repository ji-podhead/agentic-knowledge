---
okf_version: "1.0"
id: "okf-age-ski-clean-agent-harness-dap-protocol"
title: "Clean Agent Harness & Dynamic Agent Protocol (DAP v1.0) Architecture Specification"
topic: "general/agent-systems-and-browser-automation"
subtopic: "skills-and-memory"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - agent-harness
  - dap-protocol
  - tool-discovery
  - multi-agent
  - json-rpc
summary: "Technical specification for the Clean Agent Harness and Dynamic Agent Protocol (DAP v1.0), defining dynamic L1-L3 tool discovery and decoupled multi-agent execution."
---

# Clean Agent Harness & Dynamic Agent Protocol (DAP v1.0) Architecture Specification

## Executive Summary

Existing LLM agent frameworks often embed full JSON schemas for dozens of tools directly into system prompts, causing severe token bloat, high latency, and vulnerability to prompt injection or decoy tool sabotage.

The **Clean Agent Harness** coupled with the **Dynamic Agent Protocol (DAP v1.0)** decouples tool declarations from model context windows. DAP provides a standardized, three-layer dynamic tool discovery and execution architecture, enabling agents to dynamically discover, inspect, and execute remote tools on demand.

---

## 1. Three-Layer DAP Protocol Taxonomy

```
+-------------------------------------------------------------------+
| Layer 3: Application & IDE Interfaces                             |
| (VS Code Extensions, Coding Agents, DAP IDE)                      |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Layer 2: DAPNet Distributed Tool Network                          |
| (P2P Discovery, Capability Registry, Security Signatures)         |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| Layer 1: DAP Protocol Engine & Clean Agent Harness                |
| (JSON-RPC 2.0 Transport, Dynamic Resolution, Execution Sandbox)   |
+-------------------------------------------------------------------+
```

---

## 2. Dynamic Tool Discovery & Execution Loop

Instead of dumping static tool definitions into the prompt, DAP dynamically streams available tool namespaces based on the agent's active execution context.

```python
import json
import requests

class DAPClient:
    def __init__(self, dap_endpoint: str):
        self.endpoint = dap_endpoint
        self.request_id = 1

    def discover_tools(self, category: str) -> list[dict]:
        payload = {
            "jsonrpc": "2.0",
            "method": "dap.tools.discover",
            "params": {"category": category},
            "id": self.request_id
        }
        self.request_id += 1
        res = requests.post(self.endpoint, json=payload).json()
        return res.get("result", {}).get("tools", [])

    def invoke_tool(self, tool_name: str, arguments: dict) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": "dap.tools.invoke",
            "params": {"name": tool_name, "arguments": arguments},
            "id": self.request_id
        }
        self.request_id += 1
        return requests.post(self.endpoint, json=payload).json()
```

---

## 3. Comparative Architecture & Security Advantages

| Feature | Standard Static Agent Harness | Clean Agent Harness + DAP v1.0 |
|---|---|---|
| Tool Schema Ingestion | Embedded full schemas in system prompt | Dynamic discovery on demand via JSON-RPC |
| Context Token Overhead | High (5k-20k tokens per request) | Microscopic (< 200 tokens) |
| Decoy Tool Sabotage | Vulnerable to decoy tool poisoning | Cryptographically signed capability discovery |
| Runtime Sandboxing | In-process execution | Isolated RPC execution boundary |

---

## Sources & References

- [https://github.com/ji-podhead/clean-agent-harness](https://github.com/ji-podhead/clean-agent-harness)
- [https://github.com/ji-podhead/dap-docs](https://github.com/ji-podhead/dap-docs)
