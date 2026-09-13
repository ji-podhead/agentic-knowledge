---
okf_version: "1.0"
id: "okf-net-con-ovs-vlan-bridge-isolation"
title: "Open vSwitch (OVS) VLAN Isolation, Libvirt Integration & Automated Network Provisioning"
topic: "general/networking"
subtopic: "container-networking"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - openvswitch
  - ovs
  - vlan
  - libvirt
  - docker-networking
  - networkmanager
summary: "Technical guide for deploying Open vSwitch bridges with tagged VLAN isolation, Ansible automation, NetworkManager persistence, and Libvirt/Docker virtual network integration."
---

# Open vSwitch (OVS) VLAN Isolation, Libvirt Integration & Automated Network Provisioning

## Executive Summary

Standard Linux bridges lack advanced VLAN trunking, per-port isolation primitives, and flexible flow-table controls necessary for multi-tenant hypervisor and container environments. **Open vSwitch (OVS)** delivers high-performance kernel-space switching with programmable flow rules.

This specification details the `ovs-bridge-collection` architecture: configuring an OVS trunk bridge over a single physical network interface (NIC), spawning tagged VLAN interfaces without disrupting active SSH sessions or requiring reboots, and automatically binding Libvirt XML networks and Docker/Podman subnets.

---

## 1. OVS Network Architecture

```
                                  +-----------------------+
                                  | Physical Interface    |
                                  |     eno1 (Trunk)      |
                                  +-----------+-----------+
                                              |
                                  +-----------v-----------+
                                  |    OVS Bridge         |
                                  |      ovs-br0          |
                                  +----+-------------+----+
                                       |             |
                     +-----------------+             +-----------------+
                     |                                                 |
         +-----------v-----------+                         +-----------v-----------+
         | VLAN 10 Port (Internal) |                         | VLAN 20 Port (DMZ)    |
         |  vlan10 (10.10.10.1/24)|                         |  vlan20 (10.20.20.1/24)|
         +-----------+-----------+                         +-----------+-----------+
                     |                                                 |
         +-----------v-----------+                         +-----------v-----------+
         | Libvirt Web VMs       |                         | Docker DMZ Containers |
         +-----------------------+                         +-----------------------+
```

---

## 2. Command-Line & NetworkManager Provisioning Workflow

To ensure configurations persist across host reboots without breaking NetworkManager, OVS connections are managed via `nmcli`.

### 2.1 OVS Bridge & Trunk Interface Setup

```bash
# 1. Create OVS Bridge
nmcli connection add type ovs-bridge conn.interface ovs-br0 con-name ovs-br0

# 2. Attach physical NIC as an OVS port connection
nmcli connection add type ovs-port conn.interface eno1-port master ovs-br0 con-name eno1-port
nmcli connection add type ethernet conn.interface eno1 master eno1-port con-name eno1-if

# 3. Bring up OVS bridge
nmcli connection up ovs-br0
```

### 2.2 Adding Tagged VLAN Interfaces

```bash
# Add VLAN 10 internal interface on ovs-br0
ovs-vsctl add-port ovs-br0 vlan10 tag=10 -- set Interface vlan10 type=internal
ip link set dev vlan10 up
ip addr add 10.10.10.1/24 dev vlan10
```

---

## 3. Libvirt XML Network & Ansible Automation Integration

The `ji_podhead.ovs_bridge` Ansible collection automates the host creation of OVS bridges and generates matching Libvirt network XML definitions.

### 3.1 Libvirt OVS Network XML Template (`vlan10-network.xml`)

```xml
<network>
  <name>ovs-vlan-10</name>
  <forward mode='bridge'/>
  <bridge name='ovs-br0'/>
  <virtualport type='openvswitch'/>
  <portgroup name='vlan-10' default='yes'>
    <vlan>
      <tag id='10'/>
    </vlan>
  </portgroup>
</network>
```

### 3.2 Ansible Playbook Execution

```yaml
- name: Provision OVS Bridges and VLAN Networks
  hosts: hypervisors
  become: true
  roles:
    - role: ji_podhead.ovs_bridge.create_bridge
      vars:
        bridge_name: "ovs-br0"
        physical_nic: "eno1"
    - role: ji_podhead.ovs_bridge.add_vlans
      vars:
        bridge_name: "ovs-br0"
        vlans:
          - id: 10
            name: "vlan10"
            ip_cidr: "10.10.10.1/24"
          - id: 20
            name: "vlan20"
            ip_cidr: "10.20.20.1/24"
    - role: ji_podhead.ovs_bridge.libvirt_virtual_network
      vars:
        network_name: "ovs-vlan-10"
        bridge_name: "ovs-br0"
        vlan_tag: 10
```

---

## 4. Security Verification & Flow Inspections

- [x] **VLAN Tagging Validation**: Verify frame tags using `tcpdump -e -n -i eno1 vlan 10`.
- [x] **Inter-VLAN Leakage**: Confirm packets between `vlan10` and `vlan20` are blocked without explicit routing.
- [x] **OVS Flow Table Inspection**: `ovs-ofctl dump-flows ovs-br0` verified.
