---
id: "R34"
title: "SPRINT-PLANUNG & NETZWERK-RESEARCH: Zero-Trust & Layer-0 Routing"
type: research
date: 2026-09-12
status: final
tags: [mesh, ssh, gvisor, ebpf, docker]
license: CC-BY-4.0
---

# SPRINT-PLANUNG & NETZWERK-RESEARCH: Zero-Trust & Layer-0 Routing

---
**Datum:** 11. September 2026  
**Fokus:** Vergleich moderner Mesh-Routing-Protokolle (Alternativen zu klassischem WireGuard) & Strukturierte Sprint-Aufteilung.  
**Speicherpfad:** `docs/research/R34-mesh-routing-protocols-research-sprints.md`  

---

## 🌐 1. Technologie-Evaluierung: Wer schlägt klassisches WireGuard?

Klassisches WireGuard baut flache Punkt-zu-Punkt-Tunnel auf, besitzt aber keine native Identitätsprüfung auf Anwendungsebene, keine dezentralen Routing-Zentralen und erfordert oft offene Inbound-Ports für die Handshakes. 

Für JiMesh evaluieren wir im kommenden Sprint drei hochmoderne Alternativen, die Dein System **vollständig unsichtbar (Dark Infrastructure)** machen:

### A. Octelium (Der AI- & Identity-First Standard 2026)
Octelium ist das modernste FOSS-System für KI-gestützte Umgebungen:
*   **Warum es WireGuard schlägt:** Es routet nicht nur IP-Pakete (L3/L4), sondern versteht **Anwendungsprotokolle (L7)**.
*   **AI-Zentrisch:** Es deklariert **KI-Agenten und MCP-Schnittstellen (Model Context Protocol)** als eigenständige Identitäten. Du kannst Regeln schreiben wie: *"Agent DSH darf nur über ein verschlüsseltes QUIC-Tunnel auf die Postgres-Datenbank von Host B zugreifen"*.
*   **Clientless Proxies:** Bietet hochsichere Identitäts-Proxies ohne manuelle Client-Konfiguration.

### B. OpenZiti (Die unhackerbare "Dark" Infrastruktur)
OpenZiti ist das radikalste Zero-Trust-Modell:
*   **Warum es WireGuard schlägt:** Es erfordert **absolut keine offenen Inbound-Ports** auf Deiner gesamten Infrastruktur (nicht mal für Handshakes!).
*   **Outbound-Only Tunnels:** Alle Container nutzen interne "Tunneler", die ausschließlich ausgehende Verbindungen zu einem dezentralen Controller aufbauen. Für Portscanner im öffentlichen Internet existiert Deine gesamte Infrastruktur schlichtweg nicht ("Dark Infrastructure").
*   **Private DNS:** Ermöglicht die Definition privater Domains (z.B. `.jimesh.internal`), die physisch nur innerhalb Deines verschlüsselten Overlays existieren.

### C. Cilium ClusterMesh (eBPF-Kernel-Routing)
Cilium ist das Performance-Monster für containerisierte Multi-Host-Systeme:
*   **Warum es WireGuard schlägt:** Es eliminiert jeglichen "Proxy-Tax" (keine Userspace-Proxy-Prozesse). Das gesamte Routing und die Verschlüsselung (über im Kernel integriertes WireGuard/IPsec) werden **direkt über eBPF-Laufzeitprogramme im Linux-Kernel** ausgeführt.
*   **Identität über Labels:** Sicherheitsregeln basieren nicht auf flüchtigen IP-Adressen, sondern auf kryptografisch verifizierten Container-Sicherheits-IDs (Label-basiert).

---

## 📋 2. Die Sprint-Roadmap (Phasen & Research-Aufgaben)

Wir teilen die Umsetzung in vier klar strukturierte Sprints auf:

### 🚀 SPRINT 34: Globales Renaming & Networks Tab Blueprint (Diese Woche)
*   **Ziel:** Pivot von "Projects" zu "Workspaces" im gesamten Stack (PostgreSQL-Migration, Go-Backend, React-Frontend) und Hinzufügen des neuen "Networks" Tabs in der Sidebar.
*   **Keine Server-Eingriffe:** Reine, isolierte Softwareentwicklung auf Deinem Laptop (`workstation`).

### 🧪 SPRINT 35: Deep Research & Prototyping Overlay-Engines (Nächste Woche)
*   **Fokus:** **Internet-Research & Sandbox-Prototyping.**
*   **Research-Aufgaben:**
    1.  Lokales docker-compose Test-Szenario mit **OpenZiti-Tunneler** und **Octelium** aufbauen.
    2.  Vergleich der Latenzzeiten (RTT in ms), des CPU/RAM-Overheads und der Stabilität von WebSocket-Verbindungen bei hoher Last.
    3.  Evaluierung, wie sich die Tunnel-Zuweisung vollautomatisch über unsere Go-SSH-Dialer orchestrieren lässt.
*   *Lieferbares Ergebnis: Ein fertiges, getestetes Netzwerk-Preset-Konzept.*

### 🔒 SPRINT 36: Zero-Port Go-Core & Direct-SSH-Dialing Integration
*   **Ziel:** Vollständige Deaktivierung aller Port-Publishings (`-p`) für Remote-Deployments im Go-Backend.
*   **Features:**
    1.  Implementierung des automatischen SSH-internen IP-Lookups (`docker inspect`).
    2.  Anpassung des `network.Pool`-Proxy-Tunnel-Dials directly auf die isolierte Container-IP über den SSH-Kanal.
    *Der Iframe lädt sich danach vollautomatisch, ohne Host-Ports freizulegen.*

### 🛠️ SPRINT 37: Scanopy Filesystem Sharing & Live Networks View
*   **Ziel:** Finale Fertigstellung des "Networks"-Tabs im Dashboard.
*   **Features:**
    1.  Visuelle Steuerung der gVisor-Netstack-Szenarien.
    2.  Konfiguration von **gVisor-Gofer Shared Volume Mount Groups** (Scanopy), über die verschiedene Workspaces sicher und isoliert untereinander Daten auf Dateiebene austauschen können.
