---
okf_version: "1.0"
id: "okf-llm-rou-r34-mesh-routing-protocols-research-sprints"
title: "SPRINT-PLANUNG & NETZWERK-RESEARCH: Zero-Trust & Layer-0 Routing"
topic: "llm-routing-and-orchestration"
subtopic: "routing-algorithms"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-routing-and-orchestration
  - routing-algorithms
summary: "---"
---

# SPRINT-PLANUNG & NETZWERK-RESEARCH: Zero-Trust & Layer-0 Routing

---
**Datum:** 11. September 2026
**Fokus:** Comparison moderner Mesh-Routing-Protokolle (Alternativen zu klassischem WireGuard) & Strukturierte Sprint-Aufteilung.
**Speicherpfad:** `docs/research/R34-mesh-routing-protocols-research-sprints.md`

---

## 🌐 1. Technologie-Evaluierung: Wer schlägt klassisches WireGuard?

Klassisches WireGuard baut flache Punkt-zu-Punkt-Tunnel on, besitzt aber no native Identitätsprüfung on Anwendungsebene, no dezentralen Routing-Zentralen and erfordert oft offene Inbound-Ports for die Handshakes.

Für OpenMesh evaluieren wir im kommenden Sprint drei hochmoderne Alternativen, die Dein System **vollständig unsichtbar (Dark Infrastructure)** machen:

### A. Octelium (Der AI- & Identity-First Standard 2026)
Octelium ist das modernste FOSS-System for KI-gestützte Umgebungen:
*   **Warum es WireGuard schlägt:** Es routet not nur IP-Pakete (L3/L4), sondern versteht **Anwendungsprotokolle (L7)**.
*   **AI-Zentrisch:** Es deklariert **KI-Agenten and MCP-Schnittstellen (Model Context Protocol)** als eigenständige Identitäten. Du kannst Regeln schreiben wie: *"Agent DSH darf nur about ein verschlüsseltes QUIC-Tunnel on die Postgres-Datenbank von Host B zugreifen"*.
*   **Clientless Proxies:** Bietet hochsichere Identitäts-Proxies without manuelle Client-Konfiguration.

### B. OpenZiti (Die unhackerbare "Dark" Infrastruktur)
OpenZiti ist das radikalste Zero-Trust-Modell:
*   **Warum es WireGuard schlägt:** Es erfordert **absolut no offenen Inbound-Ports** on Deiner gesamten Infrastruktur (not mal for Handshakes!).
*   **Outbound-Only Tunnels:** Alle Container nutzen interne "Tunneler", die ausschließlich ausgehende Verbindungen zu einem dezentralen Controller aufbauen. Für Portscanner im öffentlichen Internet existiert Deine gesamte Infrastruktur schlichtweg not ("Dark Infrastructure").
*   **Private DNS:** Ermöglicht die Definition privater Domains (z.B. `.openmesh.internal`), die physisch nur innerhalb Deines verschlüsselten Overlays existieren.

### C. Cilium ClusterMesh (eBPF-Kernel-Routing)
Cilium ist das Performance-Monster for containerisierte Multi-Host-Systeme:
*   **Warum es WireGuard schlägt:** Es eliminiert jeglichen "Proxy-Tax" (no Userspace-Proxy-Prozesse). Das gesamte Routing and die Verschlüsselung (about im Kernel integriertes WireGuard/IPsec) werden **direkt about eBPF-Laufzeitprogramme im Linux-Kernel** ausgeführt.
*   **Identität about Labels:** Sicherheitsregeln basieren not on flüchtigen IP-Adressen, sondern on kryptografisch verifizierten Container-Sicherheits-IDs (Label-basiert).

---

## 📋 2. Die Sprint-Roadmap (Phasen & Research-Aufgaben)

Wir teilen die Umsetzung in vier klar strukturierte Sprints on:

### 🚀 SPRINT 34: Globales Renaming & Networks Tab Blueprint (Diese Woche)
*   **Ziel:** Pivot von "Projects" zu "Workspaces" im gesamten Stack (PostgreSQL-Migration, Go-Backend, React-Frontend) and Hinzufügen des neuen "Networks" Tabs in der Sidebar.
*   **Keine Server-Eingriffe:** Reine, isolierte Softwareentwicklung on Deinem Laptop (`workstation`).

### 🧪 SPRINT 35: Deep Research & Prototyping Overlay-Engines (Nächste Woche)
*   **Fokus:** **Internet-Research & Sandbox-Prototyping.**
*   **Research-Aufgaben:**
    1.  Lokales docker-compose Test-Szenario with **OpenZiti-Tunneler** and **Octelium** aufbauen.
    2.  Comparison der Latenzzeiten (RTT in ms), des CPU/RAM-Overheads and der Stabilität von WebSocket-Verbindungen at hoher Last.
    3.  Evaluierung, wie sich die Tunnel-Zuweisung vollautomatisch about unsere Go-SSH-Dialer orchestrieren lässt.
*   *Lieferbares Ergebnis: Ein fertiges, getestetes Netzwerk-Preset-Konzept.*

### 🔒 SPRINT 36: Zero-Port Go-Core & Direct-SSH-Dialing Integration
*   **Ziel:** Vollständige Deaktivierung aller Port-Publishings (`-p`) for Remote-Deployments im Go-Backend.
*   **Features:**
    1.  Implementation des automatischen SSH-internen IP-Lookups (`docker inspect`).
    2.  Anpassung des `network.Pool`-Proxy-Tunnel-Dials directly on die isolierte Container-IP about den SSH-Kanal.
    *Der Iframe lädt sich danach vollautomatisch, without Host-Ports freizulegen.*

### 🛠️ SPRINT 37: Scanopy Filesystem Sharing & Live Networks View
*   **Ziel:** Finale Fertigstellung des "Networks"-Tabs im Dashboard.
*   **Features:**
    1.  Visuelle Steuerung der gVisor-Netstack-Szenarien.
    2.  Konfiguration von **gVisor-Gofer Shared Volume Mount Groups** (Scanopy), about die verschiedene Workspaces sicher and isoliert untereinander Daten on Dateiebene austauschen können.
