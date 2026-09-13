---
id: "R36"
title: "R36 — Positionierungs-Entscheidung: JiMesh ist kein Coder-Konkurrent"
type: research
date: 2026-09-12
status: final
tags: [mesh, siem, headscale, failover, ebpf]
license: CC-BY-4.0
---

# R36 — Positionierungs-Entscheidung: JiMesh ist kein Coder-Konkurrent

**Operator-Entscheidung, 13.9.2026** (nach R35-Salvage-Review + Coder-README-
Analyse). Kurzform: „Wir sind nicht Coder. Wir sind eine sichere Environment
für Vibe-Coding und Agents — Security und Networking ist unser Vorteil."

## 1. Die Entscheidung

**Drei Produkt-Pfeiler** (Operator, 13.9.2026):

1. **LLM-Gateway** — Multi-Provider-Routing, Chains, Failover, Keypool,
   Budgets. Kern seit Sprint 1.
2. **Sichere Environment für Vibe-Coding + Agents** — Provisioning über
   SSH-Targets, gVisor-Sandbox, Mesh (Headscale), Service-Accounts
   („no LLM keys in workspaces"), Kosten pro User UND pro App.
3. **LLM-Security-Tool (K-LAF)** — Prompt-Injection-Detection im Prozess
   (E1: purego/ONNX, kleiner Prompt-Guard-Klassifikator 22–86M Params,
   kein Sidecar), **Llama Guard als geroutetes Guard-Modell** über den
   Proxy (NIM/Self-Host — „even your security scanning gets failover and
   cost control for free", llm-mesh-intro:35), **eBPF-Tripwire**
   (WP8: execve/Socket-Öffnen/SSL_write·read-Probes → Ring-Buffer →
   Klassifikator), Secret-Pattern-Masking an Responses, Freeze (E5),
   SIEM (Sprint 32). Fundstellen: `docs/K-LAF-ARCHITECTURE.md:20,211`,
   `sprint docs (internal)` WP8 (L.401–408),
   `docs/research/DECISIONS.md` E1, `docs/articles/ebpf/*:35`.

**JiMesh konkurrenziert Coder NICHT im Workspace-Ökosystem.** Wer
Terraform-Template-Marktplatz und ausgereifte Workspace-UX will, kauft Coder
(deren 5-Jahre-Vorsprung, AGPL-Kern + Premium-Enterprise).

**JiMesh baut die integrierte, self-hostete Security- und Governance-
Environment für AI-Coding und Agents.** Diese Kombination existiert als
Produkt nicht (Stand 13.9.2026, s. §2).

## 2. Warum das kein Wunschdenken ist — verifizierte Lücken bei Coder

| Baustein | Coder (Fundstellen: R35 §2/§10, GitHub-Repo-Baum) | JiMesh |
|---|---|---|
| SIEM | ❌ nichts im Repo | Sprint 32 (Wazuh+Falco+Bridge) |
| Prompt-Injection-Detection | ❌ Agent-Firewall = nur `domain=/method=/path=`-Allowlist (rules-engine.md) | E1 entschieden: ONNX-Klassifikator in-process + Llama Guard via Mesh |
| eBPF-Tripwire | ❌ (landjail = Landlock nur für connect/bind) | K-LAF WP8: execve/Socket/SSL-Probes → Ring-Buffer |
| Container-Freeze/Quarantine | ❌ | E5 entschieden (alle Container) |
| Docker-Socket-Guard | ❌ | ✅ live (TASK-015/019) |
| Egress-Allowlist | ✅ (Premium, Prozess-Level) | ✅ live (Gateway-Level) |
| Routing-Intelligenz | ❌ (AI Gateway zentralisiert nur Auth/Kosten — keine Chains, kein Failover, kein Bandit, kein Keypool-Cooldown) | ✅ Kern seit Sprint 1 |
| Kosten pro APP | Gateway = Premium, workspace-zentriert | Service-Accounts (Sprint 35 WP1): User UND App, Budget-Cascade |
| Mesh | Embedded WireGuard-Tailnet, nur Workspaces, proprietär | Headscale: Standard-Protokoll für GESAMTE Infra (Targets, DBs, Apps) |
| DB/CDC-Utility-Layer | ❌ | Sprint 26 |
| Workspace-UX/Terraform-Ökosystem | ✅✅ | ❌ (bewusst nicht unser Feld) |

Coder positioniert sich selbst neu („platform for cloud development
environments **and AI coding agents**", AI Gateway) — **Enterprise-licensed**
(`enterprise/cli/aigateway*.go` im Repo-Baum). Sie validieren den Markt für
„no API keys in workspaces, identity on every action, centralized cost
control" — genau die Architektur, die TASK-011 + Keypool + Budgets schon
bauen. Aber sie koppeln es an ihre Workspaces; JiMesh koppelt es an
**beliebige Agents + jede Infra**.

## 3. Der Burggraben (ehrlich, nicht Marketing)

- Einzelne Bausteine haben je Konkurrenten: Gateway (LiteLLM/Portkey/
  OpenRouter — überfüllt), Mesh (Tailscale), SIEM (Wazuh allein), Firewall
  (unzählige). **Kein Einzelbaustein ist das Moat.**
- Das Moat ist die **Integration für Self-Hoster**: LLM-Gateway mit Routing +
  Budgets pro User UND pro App + Freeze + Injection-Detection + SIEM +
  Standard-Mesh über alle SSH-Targets + Provisioning/DB-Layer — **ein
  Stack, eine Instanz, self-hosted, nicht Premium-gated.**
- Schwäche, die wir akzeptieren: Workspace-UX/Templates 1–2 Jahre hinter
  Coder, wenn überhaupt. Kein Template-Marktplatz. Das ist OK — anderes
  Produktzentrum.

## 4. Konsequenzen für die Sprints

1. **Nicht bauen:** eigener Template-Marktplatz, IDE-Plugin-Suite,
   Workspace-Cosmetics („schöner als Coder"-Spielen).
2. **Bauen (Priorität):** Sprint 35 WP1 — User-Proxy-Keys +
   Service-Accounts („Kosten pro App"), WP3 Headscale-Enrollment
   (Mesh-First, „keine komischen Tunnel"), K-LAF WP2–4, SIEM (Sprint 32).
3. **Preset-Muster aus Coder übernehmen (Muster, kein Code):** deklarative
   YAML-Templates für Framework-Presets (R35 §10.3).
4. **AGPL-Realität:** Coder ist als Basis für die Kommerz-Pläne
   (PolyForm-NC) ohnehin gesperrt — die Build-vs-Fork-Frage stellt sich
   nie.

**Verweise:** `docs/research/R35-code-salvage-review.md` (Lizenzen,
Fundstellen), `sprint docs (internal)`
(Umsetzung), `docs/PRODUCT-ROADMAP.md` (§2 Access Policy).
