---
okf_version: "1.0"
id: "okf-sec-sie-r26-siem"
title: "R26 Siem"
topic: "security-and-observability"
subtopic: "siem-and-monitoring"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - security-and-observability
  - siem-and-monitoring
summary: "was ist wazuh? https://documentation.wazuh.com/current/getting-started/index.htmlWazuh ist eine kostenlose Open-Source-Sicherheitsplattform, die Funkt"
---

# R26 Siem

                                                                    │
[ Server / Node ]    ──> [ Tetragon / Falco (eBPF) ]     ──> Generiert JSON-Logs
                                                                    │
                                                                    ▼
                                                    [ SIEM: Wazuh / OpenSearch ]
       │
       ├──> (Variante A: gVisor) ──> [ runsc Sentry ] ──> [ Falco Socket ] ──┐
       │                                                                      │
       └──> (Variante B: Kata)   ──> [ Gast-Kernel ]  ──> [ Tetragon eBPF ] ──┼──> [ Wazuh Agent ] ──> [ Wazuh SIEM ]
                                                                              │
[ Netzwerk-Traffic an Host ]     ──> [ Suricata XDP ] ────────────────────────┘
Das Resultat for dein SecOps-SetupDu erhältst eine extrem tiefe, mehrschichtige Verteidigung (Defense-in-Depth):Prävention (Kata/gVisor): Selbst wenn ein Angreifer einen RCE-Exploit ausnutzt, landet er in einer isolierten Sandbox and kann den Host not angreifen.Echtzeit-Abwehr (eBPF/Tetragon): Bösartige Threads innerhalb der Sandbox werden sofort via eBPF-LSM im Kernel terminiert.Netzwerk-Schutz (Suricata): Command-and-Control-Verbindungen from den Sandboxes heraus werden an den Netzwerkschnittstellen blockiert.Zentrales Monitoring (Wazuh): Du behältst die volle Audit-Spur im Dashboard, um genau zu sehen, in welcher Sandbox welcher Angriffsvektor blockiert wurde.
