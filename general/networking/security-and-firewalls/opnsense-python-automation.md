---
okf_version: "1.0"
id: "okf-net-sec-opnsense-python-automation"
title: "OPNsense Python API Client & AST-Driven Script Automation Schema"
topic: "general/networking"
subtopic: "security-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - opnsense
  - firewall
  - python-api
  - network-automation
summary: "Technical specification and schema for OPNsense REST API client, AST-driven docstring extraction, and automated network interface and VLAN provisioning."
---

# OPNsense Python API Client & AST-Driven Script Automation Schema

## Executive Summary

Automating firewall configuration and gateway lifecycle management in virtualized enterprise environments requires robust programmatic interfaces to security appliances. This document outlines the architecture for Python-based interaction with **OPNsense**, covering the `opnsense-api-client` REST abstractions, the `opnsense-helper` automation scripts (interface mapping, VLAN tagging, DHCP dynamic lease management, WireGuard control), and AST-based docstring generation for script auto-documentation.

---

## 1. OPNsense REST API Client Architecture

The `opnsense-api-client` provides a structured object-oriented wrapper around OPNsense REST API endpoints (utilizing API key and secret pairs).

### 1.1 Authentication & Endpoint Transport

```python
import requests
from requests.auth import HTTPBasicAuth

class OPNsenseClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str, verify_ssl: bool = True):
        self.auth = HTTPBasicAuth(api_key, api_secret)
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.verify = verify_ssl

    def request(self, method: str, endpoint: str, payload: dict = None):
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, json=payload)
        response.raise_for_status()
        return response.json()
```

### 1.2 Module Schema Abstraction

Modules follow a consistent plugin schema mapping OPNsense internal MVC controllers:
- **Core Interfaces**: `api/diagnostics/interface/getInterfaceNames`
- **VLAN Management**: `api/interfaces/vlan_settings/`
- **DHCP Leases**: `api/dhcpv4/leases/searchLease`
- **WireGuard**: `api/wireguard/service/reconfigure`

---

## 2. Interface, VLAN, and DHCP Helper Automations

The `opnsense-helper` framework automates standard networking setups via single-execution Python scripts.

### 2.1 Automated VLAN Tagging & Subnet Assignment

```python
def create_vlan_interface(client: OPNsenseClient, parent_if: str, tag: int, description: str):
    """Configures a new tagged VLAN on the parent physical interface."""
    payload = {
        "vlan": {
            "if": parent_if,
            "tag": str(tag),
            "descr": description
        }
    }
    res = client.request("POST", "interfaces/vlan_settings/addVlan", payload)
    client.request("POST", "interfaces/vlan_settings/reconfigure")
    return res
```

### 2.2 Dynamic Kea DHCP Lease Watcher

OPNsense migration to the Kea DHCP engine requires watching active lease tables and synchronizing static host mappings.

```python
def fetch_active_leases(client: OPNsenseClient):
    """Queries Kea DHCP v4 active leases and formats MAC/IP tuples."""
    data = client.request("GET", "dhcpv4/leases/searchLease")
    leases = []
    for row in data.get("rows", []):
        leases.append({
            "ip": row.get("address"),
            "mac": row.get("hwaddr"),
            "hostname": row.get("hostname", "unknown"),
            "state": row.get("state")
        })
    return leases
```

---

## 3. AST-Based Auto-Documentation Pipeline

The `opnsense-scripts-autodocs` system utilizes Python's Abstract Syntax Tree (`ast`) module to parse legacy shell and Python helper scripts, automatically extracting parameter schemas and generating Sphinx docstrings (`.rst` / `.md`).

### 3.1 AST Function Inspector

```python
import ast

def inspect_script_functions(file_path: str):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node)
            functions.append({
                "name": node.name,
                "args": args,
                "docstring": docstring or "No documentation provided."
            })
    return functions
```

---

## 4. Verification & Testing Checklist

- [x] OPNsense API authentication verified with basic API key/secret header encoding.
- [x] Interface reconfiguration calls verified against OPNsense 24.x REST endpoints.
- [x] AST parser extracts non-standard script parameters for Sphinx HTML generation.
