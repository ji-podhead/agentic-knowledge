---
id: "R19"
title: "R19 — LLM-Firewall-Landschaft & Kernel-nahes Injection-Tracking"
type: landscape
date: 2026-09-13
status: final
tags: [ebpf, mesh, gvisor, llama, k8s]
license: CC-BY-4.0
---

# R19 — LLM-Firewall-Landschaft & Kernel-nahes Injection-Tracking

> Quelle: Nutzer-Recherche per KI-Suche (September 2026). Sortiert gegen
> `SPRINT-20-KLAF-FOUNDATION.md`, `K-LAF-ARCHITECTURE.md`, `PRODUCT-ROADMAP.md`.
> Status: Recherche, keine Entscheidung.
> **Update 7.9.2026 — Anbieter verifiziert (O-R1 geschlossen, per Websuche):**
> TigerGate (tigergate.dev — real, CNAPP-Plattform mit eBPF-Agent + AI-SPM,
> aber Github-Org fast nur Forks, Claims unverifiziertes Vendor-Marketing),
> Lakera → Check Point (Pressemitteilung 16.9.2025, ~$300M),
> Portkey → Palo Alto Networks (announced 30.4.2026, closed 29.5.2026).
> Vor Produktbezügen weiterhin Leistungsversprechen der Anbieter gegenprüfen.

## 1. Marktkarte

| Klasse | Beispiele (laut Recherche) | Was sie leisten | Grenze aus JiMesh-Sicht |
|---|---|---|---|
| Gateway/Proxy (OSS) | LiteLLM Proxy | Provider-Vereinheitlichung, Budgets, Key-Management, Rate-Limits | kennt keine Session↔Container↔User-Zuordnung, kein Freeze |
| In-Process-Scanner (OSS) | LLM Guard (Protect AI), NeMo Guardrails, Guardrails AI | PII/Injection/Toxizität-Scanner, Dialogregeln (Colang), Ausgabe-Validierung | laufen in der App, nicht am Netzwerk-Punkt; kein Netzwerk-Enforcement |
| Kommerzielle Plattformen | Lakera Guard (Check Point, übernommen 9/2025), Prompt Security (SentinelOne), Portkey (Palo Alto, übernommen 5/2026) | Echtzeit-Injection-Abwehr, Shadow-AI-Discovery, Control Plane | closed, fremdes Trust-Muster, keine Provisionierung |
| Edge/Netzwerk | Cloudflare Firewall for AI (Llama Guard), Azure AI Content Safety, Microsoft Entra Prompt Injection Protection, Fortinet/Check Point | Endpoint-Schutz, DPI auf LLM-/MCP-Traffic | sehen Endpunkte, keine Identität, kein Freeze |
| Kernel/Runtime | TigerGate (kommerziell, CNAPP mit eBPF-Agent), AgentSight (Forschung, OSS) | eBPF an TLS-Grenzen, Enforcement im Kernel | sehen den Host — nicht die Identitätskette, die JiMesh provisioniert |

**Einordnung:** Vier der fünf Klassen inspizieren Text oder Pakete. Keine Klasse
provisioniert die Umgebung, in der der Agent läuft — genau daraus bezieht JiMesh die
Identitätskette (Session↔Container↔User) und den Freeze. Siehe `PRODUCT-ROADMAP.md`
§7 und Abschnitt 1.

## 2. Kernel-nahes Injection-Tracking (Mechanik, WP8-relevant)

Das in der Recherche beschriebene Muster (so arbeitet AgentSight; TigerGate macht es
kommerziell — Produkt bestätigt, technische Tiefenclaims Vendor-Angabe):

1. **uprobe/uretprobe an `SSL_write`/`SSL_read`** der Krypto-Bibliothek des Prozesses —
   dort liegt der Prompt als Klartext, bevor TLS ihn verschlüsselt.
2. **eBPF Ring Buffer** transportiert den Klartext in einen Userspace-Daemon.
3. **Kleiner Klassifikator statt 8B-Llama-Guard:** Llama Prompt Guard 2 (22M/86M,
   ONNX) im C++/Rust-Sidecar; alternativ Embedding + XGBoost (Sub-Millisekunde, siehe §3).
4. **Verdict zurück in eine eBPF-Map** → Drop/TCP-RST/Freeze im Kernel.

**Passt zu Sprint 20:**

* Die Recherche empfiehlt exakt **E1-Option A** (Rust/C++-Sidecar wegen des
  CGO-Konflikts, Mandat 7 `CGO_ENABLED=0`) — externe Bestätigung des gesetzten Defaults.
* Der WP8-Grundsatz bleibt unangetastet: **eBPF liefert Ereignisse und hier zusätzlich
  den Inhalt an der TLS-Grenze; bewerten tut weiterhin Userspace.** Kein
  Klassifikator im Kernel.

**Harte Grenzen:**

* **Chunking/Streaming:** eBPF liest pro Aufruf nur wenige KB. Gestreamte Prompts müssen
  im Userspace reassembliert werden; reine Kernel-Erkennung ist bei HTTP-Streaming
  praktisch ausgeschlossen. (Bestätigt die Recherche selbst — und WP8's Design.)
* ⚠️ **Eigener Einwand, fehlt in der Recherche:** uprobes hängen an konkrete
  Bibliothekssymbole. Node-Stacks (DSH, Claude Code, Gemini CLI — OpenSSL/BoringSSL)
  sind greifbar. **Go-Binaries nutzen `crypto/tls`** — keine stabilen C-Symbole,
  Inlining, GC — dort greift der Trick nicht ohne Weiteres. Auf Node-lastigen
  Workspaces funktioniert es; als universeller Mechanismus taugt es nicht.
  „Zero Instrumentation" ist ein Anspruch, keine Garantie (static linking, rustls,
  eigene TLS-Stacks).
* Enforcement im Kernel (Drop/RST) kollidiert mit WP2's Fail-open-Debatte (E2): ein
  Kernel-Drop ist per Definition fail-closed. Bis E2 geklärt ist, gehört das
  Enforcement-Ergebnis ins Threat-Event, nicht in die Kernel-Map.

## 3. Leichtgewichtige Alternativen zum Modell-Scanner

* Embedding-basierter Klassifikator + XGBoost/Random Forest
  (`AhsanAyub/malicious-prompt-detection` ⚠️ unverifiziert): Sub-Millisekunde.
  Denkbar als Kaskadenstufe vor Prompt Guard: Regex (WP2, <1 ms) → heuristisch → Modell.
* Bleibt konsistent mit WP2: Regex-Scanner zuerst, Modell-Scanner als eigene Chain
  über das Mesh (Failover, Budget-Check) — der Sidecar ist nur die Niedriglatenz-Variante.

## 4. Bereits entschieden — keine Änderung nötig

* **gVisor in VM:** Systrap-Plattform (kein KVM nötig, läuft auf jeder Cloud-VM) vs.
  KVM-Plattform (Nested-Virt nötig) — deckt K-LAF-ARCHITECTURE §5 und das duale
  Onboarding-Modell aus Sprint 19 ab (gVisor/Systrap lokal, Kata/KubeVirt im
  Enterprise-Pfad). Die Recherche widerspricht dem nicht.
* **Kata + gVisor nicht verschachteln**, sondern als RuntimeClasses nebeneinander —
  konsistent mit der Spec. Für JiMesh (Docker + SSH, kein Kubernetes) derzeit
  irrelevant; das K8s-SIG-Projekt „Agent Sandbox" (⚠️ unverifiziert) ist ein
  Beobachtungspunkt, falls ein K8s-Deploy-Pfad kommt.
* **„BPFJailer (von Meta)" — erneut falsch zugeordnet.** Es ist die eigenständige
  Implementierung von Wisehart, Nga, El Khoury und Chadha (Team bei Meta); Metas
  eigenes BpfJailer ist nicht öffentlich. Das Enforcement-Loch decken bei JiMesh
  nftables (Netz) und gVisor (Syscalls); BPF-LSM bleibt Tier-3-Wiedervorlage
  (Enterprise auf eigener Hardware).
* **LiteLLM ist Python**, nicht „Asynchrones Go/Python" (ungenau in der Vergleichstabelle
  der Recherche).
* **„Apalachee" als Observability-Tool ist eine KI-Verwechslung** (Apalachee ist ein
  TLA+-Model-Checker). Gemeint ist die OpenLLMetry/OpenTelemetry-Klasse — Traffic-
  Aufzeichnung für Audit, kein Enforcement. JiMesh hat diese Rolle intern
  (`request_log`, `traffic_inspector`, Tracing).
* **JiMesh braucht LiteLLM nicht:** Der eigene Go-Gateway ist bereits der
  OpenAI-kompatible Eintrittspunkt mit Budgets, Failover und Chains. LiteLLM höchstens
  als Vergleichsmaßstab für Feature-Parität, nicht als Abhängigkeit.

## 5. Offene Fragen

* **O-R1 — Anbieter verifizieren** — ✅ **erledigt 7.9.2026** (Websuche, siehe Header-Update oben): TigerGate real (CNAPP + eBPF-Agent, Marketing-Claims ungeprüft), Lakera→Check Point bestätigt, Portkey→Palo Alto bestätigt. K8s-„Agent Sandbox"-SIG bleibt offen.
* **O-R2 — uprobe-Feasibility-Spike** bei WP8-Start: Klartext-Abgriff an SSL_write auf
  dem realen Agenten-Mix (Node ✓, Go ✗) messen; Alternativpfad OTLP von AgentSight
  statt eigener eBPF-Arbeit bewerten.
* **O-R3 — Kaskadenarchitektur des Scanner-Pfads:** Regex → heuristisch (Embedding/
  XGBoost) → Prompt Guard im Sidecar — Latenzziele pro Stufe festlegen (gehört zu E1/E2).
