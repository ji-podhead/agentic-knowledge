---
okf_version: "1.0"
id: "okf-sec-gua-llm-firewall-landscape"
title: "R19 — LLM-Firewall-Landschaft & Kernel-nahes Injection-Tracking"
topic: "general/security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - security-and-observability
  - guardrails-and-firewalls
summary: "> Source: Nutzer-Research per KI-Suche (September 2026). Sortiert gegen"
---

# R19 — LLM-Firewall-Landschaft & Kernel-nahes Injection-Tracking

> Source: Nutzer-Research per KI-Suche (September 2026). Sortiert gegen
> `Milestone.md`, `K-LAF-ARCHITECTURE.md`, `PRODUCT-ROADMAP.md`.
> Status: Research, no Decision.
> **Update 7.9.2026 — Anbieter verifiziert (O-R1 geschlossen, per Websuche):**
> TigerGate (tigergate.dev — real, CNAPP-Plattform with eBPF-Agent + AI-SPM,
> aber Github-Org fast nur Forks, Claims unverifiziertes Vendor-Marketing),
> Lakera → Check Point (Pressemitteilung 16.9.2025, ~$300M),
> Portkey → Palo Alto Networks (announced 30.4.2026, closed 29.5.2026).
> Vor Produktbezügen weiterhin Leistungsversprechen der Anbieter gegenprüfen.

## 1. Marktkarte

| Klasse | Beispiele (laut Research) | Was sie leisten | Grenze from The Multi-Provider Gateway-Sicht |
|---|---|---|---|
| Gateway/Proxy (OSS) | LiteLLM Proxy | Provider-Vereinheitlichung, Budgets, Key-Management, Rate-Limits | kennt no Session↔Container↔User-Zuordnung, no Freeze |
| In-Process-Scanner (OSS) | LLM Guard (Protect AI), NeMo Guardrails, Guardrails AI | PII/Injection/Toxizität-Scanner, Dialogregeln (Colang), Ausgabe-Validierung | laufen in der App, not am Netzwerk-Punkt; no Netzwerk-Enforcement |
| Kommerzielle Plattformen | Lakera Guard (Check Point, übernommen 9/2025), Prompt Security (SentinelOne), Portkey (Palo Alto, übernommen 5/2026) | Echtzeit-Injection-Abwehr, Shadow-AI-Discovery, Control Plane | closed, fremdes Trust-Muster, no Provisionierung |
| Edge/Netzwerk | Cloudflare Firewall for AI (Llama Guard), Azure AI Content Safety, Microsoft Entra Prompt Injection Protection, Fortinet/Check Point | Endpoint-Schutz, DPI on LLM-/MCP-Traffic | sehen Endpunkte, no Identität, no Freeze |
| Kernel/Runtime | TigerGate (kommerziell, CNAPP with eBPF-Agent), AgentSight (Forschung, OSS) | eBPF an TLS-Grenzen, Enforcement im Kernel | sehen den Host — not die Identitätskette, die The Multi-Provider Gateway provisioniert |

**Einordnung:** Vier der fünf Klassen inspizieren Text or Pakete. Keine Klasse
provisioniert die Umgebung, in der der Agent läuft — genau daraus bezieht The Multi-Provider Gateway die
Identitätskette (Session↔Container↔User) and den Freeze. Siehe `PRODUCT-ROADMAP.md`
§7 and Abschnitt 1.

## 2. Kernel-nahes Injection-Tracking (Mechanik, Work Package-relevant)

Das in der Research beschriebene Muster (so arbeitet AgentSight; TigerGate macht es
kommerziell — Produkt bestätigt, technische Tiefenclaims Vendor-Angabe):

1. **uprobe/uretprobe an `SSL_write`/`SSL_read`** der Krypto-Bibliothek des Prozesses —
   dort liegt der Prompt als Klartext, bevor TLS ihn verschlüsselt.
2. **eBPF Ring Buffer** transportiert den Klartext in einen Userspace-Daemon.
3. **Kleiner Klassifikator statt 8B-Llama-Guard:** Llama Prompt Guard 2 (22M/86M,
   ONNX) im C++/Rust-Sidecar; alternativ Embedding + XGBoost (Sub-Millisekunde, siehe §3).
4. **Verdict zurück in eine eBPF-Map** → Drop/TCP-RST/Freeze im Kernel.

**Passt zu Milestone:**

* Die Research empfiehlt exakt **E1-Option A** (Rust/C++-Sidecar wegen des
  CGO-Konflikts, Mandat 7 `CGO_ENABLED=0`) — externe Bestätigung des gesetzten Defaults.
* Der Work Package-Grundsatz bleibt unangetastet: **eBPF liefert Ereignisse and hier zusätzlich
  den Inhalt an der TLS-Grenze; bewerten tut weiterhin Userspace.** Kein
  Klassifikator im Kernel.

**Harte Grenzen:**

* **Chunking/Streaming:** eBPF liest pro Aufruf nur wenige KB. Gestreamte Prompts müssen
  im Userspace reassembliert werden; reine Kernel-Erkennung ist at HTTP-Streaming
  praktisch ausgeschlossen. (Bestätigt die Research selbst — and Work Package's Design.)
* ⚠️ **Eigener Einwand, fehlt in der Research:** uprobes hängen an konkrete
  Bibliothekssymbole. Node-Stacks (DSH, Claude Code, Gemini CLI — OpenSSL/BoringSSL)
  sind greifbar. **Go-Binaries nutzen `crypto/tls`** — no stabilen C-Symbole,
  Inlining, GC — dort greift der Trick not without Weiteres. Auf Node-lastigen
  Workspaces funktioniert es; als universeller Mechanismus taugt es not.
  „Zero Instrumentation" ist ein Anspruch, no Garantie (static linking, rustls,
  own TLS-Stacks).
* Enforcement im Kernel (Drop/RST) kollidiert with Work Package's Fail-open-Debatte (E2): ein
  Kernel-Drop ist per Definition fail-closed. Bis E2 geklärt ist, gehört das
  Enforcement-Ergebnis ins Threat-Event, not in die Kernel-Map.

## 3. Leichtgewichtige Alternativen zum Modell-Scanner

* Embedding-basierter Klassifikator + XGBoost/Random Forest
  (`AhsanAyub/malicious-prompt-detection` ⚠️ unverifiziert): Sub-Millisekunde.
  Denkbar als Kaskadenstufe before Prompt Guard: Regex (Work Package, <1 ms) → heuristisch → Modell.
* Bleibt konsistent with Work Package: Regex-Scanner zuerst, Modell-Scanner als own Chain
  about das Mesh (Failover, Budget-Check) — der Sidecar ist nur die Niedriglatenz-Variante.

## 4. Bereits entschieden — no Änderung nötig

* **gVisor in VM:** Systrap-Plattform (no KVM nötig, läuft on jeder Cloud-VM) vs.
  KVM-Plattform (Nested-Virt nötig) — deckt K-LAF-ARCHITECTURE §5 and das duale
  Onboarding-Modell from Milestone ab (gVisor/Systrap lokal, Kata/KubeVirt im
  Enterprise-Pfad). Die Research widerspricht dem not.
* **Kata + gVisor not verschachteln**, sondern als RuntimeClasses nebeneinander —
  konsistent with der Spec. Für The Multi-Provider Gateway (Docker + SSH, no Kubernetes) derzeit
  irrelevant; das K8s-SIG-Projekt „Agent Sandbox" (⚠️ unverifiziert) ist ein
  Beobachtungspunkt, falls ein K8s-Deploy-Pfad kommt.
* **„BPFJailer (von Meta)" — erneut falsch zugeordnet.** Es ist die eigenständige
  Implementation von Wisehart, Nga, El Khoury and Chadha (Team at Meta); Metas
  eigenes BpfJailer ist not öffentlich. Das Enforcement-Loch decken at The Multi-Provider Gateway
  nftables (Netz) and gVisor (Syscalls); BPF-LSM bleibt Tier-3-Wiedervorlage
  (Enterprise on eigener Hardware).
* **LiteLLM ist Python**, not „Asynchrones Go/Python" (ungenau in der Vergleichstabelle
  der Research).
* **„Apalachee" als Observability-Tool ist eine KI-Verwechslung** (Apalachee ist ein
  TLA+-Model-Checker). Gemeint ist die OpenLLMetry/OpenTelemetry-Klasse — Traffic-
  Aufzeichnung for Audit, no Enforcement. The Multi-Provider Gateway hat diese Rolle intern
  (`request_log`, `traffic_inspector`, Tracing).
* **The Multi-Provider Gateway braucht LiteLLM not:** Der own Go-Gateway ist bereits der
  OpenAI-kompatible Eintrittspunkt with Budgets, Failover and Chains. LiteLLM höchstens
  als Vergleichsmaßstab for Feature-Parität, not als Abhängigkeit.

## 5. Offene Fragen

* **O-R1 — Anbieter verifizieren** — ✅ **erledigt 7.9.2026** (Websuche, siehe Header-Update oben): TigerGate real (CNAPP + eBPF-Agent, Marketing-Claims ungeprüft), Lakera→Check Point bestätigt, Portkey→Palo Alto bestätigt. K8s-„Agent Sandbox"-SIG bleibt offen.
* **O-R2 — uprobe-Feasibility-Spike** at Work Package-Start: Klartext-Abgriff an SSL_write on
  dem realen Agenten-Mix (Node ✓, Go ✗) messen; Alternativpfad OTLP von AgentSight
  statt eigener eBPF-Arbeit bewerten.
* **O-R3 — Kaskadenarchitektur des Scanner-Pfads:** Regex → heuristisch (Embedding/
  XGBoost) → Prompt Guard im Sidecar — Latenzziele pro Stufe festlegen (gehört zu E1/E2).
