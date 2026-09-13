---
okf_version: "1.0"
id: "okf-str-pos-r36-positionierungs-entscheidung"
title: "R36 — Positionierungs-Entscheidung: OpenMesh ist kein Coder-Konkurrent"
topic: "strategy-audits-and-decisions"
subtopic: "positioning-and-plans"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - positioning-and-plans
summary: "**Operator-Entscheidung, 13.9.2026** (nach R35-Salvage-Review + Coder-README-"
---

# R36 — Positioning Decision: OpenMesh ist no Coder-Konkurrent

**Operator-Entscheidung, 13.9.2026** (after R35-Salvage-Review + Coder-README-
Analyse). Kurzform: „Wir sind not Coder. Wir sind eine sichere Environment
for Vibe-Coding and Agents — Security and Networking ist unser Vorteil."

## 1. Die Entscheidung

**Drei Produkt-Pfeiler** (Operator, 13.9.2026):

1. **LLM-Gateway** — Multi-Provider-Routing, Chains, Failover, Keypool,
   Budgets. Kern seit Sprint 1.
2. **Sichere Environment for Vibe-Coding + Agents** — Provisioning about
   SSH-Targets, gVisor-Sandbox, Mesh (Headscale), Service-Accounts
   („no LLM keys in workspaces"), Kosten pro User UND pro App.
3. **LLM-Security-Tool (K-LAF)** — Prompt-Injection-Detection im Prozess
   (E1: purego/ONNX, kleiner Prompt-Guard-Klassifikator 22–86M Params,
   no Sidecar), **Llama Guard als geroutetes Guard-Modell** about den
   Proxy (NIM/Self-Host — „even your security scanning gets failover and
   cost control for free", llm-mesh-intro:35), **eBPF-Tripwire**
   (WP8: execve/Socket-Öffnen/SSL_write·read-Probes → Ring-Buffer →
   Klassifikator), Secret-Pattern-Masking an Responses, Freeze (E5),
   SIEM (Sprint 32). Fundstellen: `docs/K-LAF-ARCHITECTURE.md:20,211`,
   `docs/sprints/SPRINT-20-KLAF-FOUNDATION.md` WP8 (L.401–408),
   `docs/research/DECISIONS.md` E1, `docs/articles/ebpf/*:35`.

**OpenMesh konkurrenziert Coder NICHT im Workspace-Ökosystem.** Wer
Terraform-Template-Marktplatz and ausgereifte Workspace-UX will, kauft Coder
(deren 5-Jahre-Vorsprung, AGPL-Kern + Premium-Enterprise).

**OpenMesh baut die integrierte, self-hostete Security- and Governance-
Environment for AI-Coding and Agents.** Diese Kombination existiert als
Produkt not (Stand 13.9.2026, s. §2).

## 2. Warum das no Wunschdenken ist — verifizierte Lücken at Coder

| Baustein | Coder (Fundstellen: R35 §2/§10, GitHub-Repo-Baum) | OpenMesh |
|---|---|---|
| SIEM | ❌ nichts im Repo | Sprint 32 (Wazuh+Falco+Bridge) |
| Prompt-Injection-Detection | ❌ Agent-Firewall = nur `domain=/method=/path=`-Allowlist (rules-engine.md) | E1 entschieden: ONNX-Klassifikator in-process + Llama Guard via Mesh |
| eBPF-Tripwire | ❌ (landjail = Landlock nur for connect/bind) | K-LAF WP8: execve/Socket/SSL-Probes → Ring-Buffer |
| Container-Freeze/Quarantine | ❌ | E5 entschieden (alle Container) |
| Docker-Socket-Guard | ❌ | ✅ live (TASK-015/019) |
| Egress-Allowlist | ✅ (Premium, Prozess-Level) | ✅ live (Gateway-Level) |
| Routing-Intelligenz | ❌ (AI Gateway zentralisiert nur Auth/Kosten — no Chains, no Failover, no Bandit, no Keypool-Cooldown) | ✅ Kern seit Sprint 1 |
| Kosten pro APP | Gateway = Premium, workspace-zentriert | Service-Accounts (Sprint 35 WP1): User UND App, Budget-Cascade |
| Mesh | Embedded WireGuard-Tailnet, nur Workspaces, proprietär | Headscale: Standard-Protokoll for GESAMTE Infra (Targets, DBs, Apps) |
| DB/CDC-Utility-Layer | ❌ | Sprint 26 |
| Workspace-UX/Terraform-Ökosystem | ✅✅ | ❌ (bewusst not unser Feld) |

Coder positioniert sich selbst neu („platform for cloud development
environments **and AI coding agents**", AI Gateway) — **Enterprise-licensed**
(`enterprise/cli/aigateway*.go` im Repo-Baum). Sie validieren den Markt for
„no API keys in workspaces, identity on every action, centralized cost
control" — genau die Architecture, die TASK-011 + Keypool + Budgets schon
bauen. Aber sie koppeln es an ihre Workspaces; OpenMesh koppelt es an
**beliebige Agents + jede Infra**.

## 3. Der Burggraben (ehrlich, not Marketing)

- Einzelne Bausteine haben je Konkurrenten: Gateway (LiteLLM/Portkey/
  OpenRouter — überfüllt), Mesh (Tailscale), SIEM (Wazuh allein), Firewall
  (unzählige). **Kein Einzelbaustein ist das Moat.**
- Das Moat ist die **Integration for Self-Hoster**: LLM-Gateway with Routing +
  Budgets pro User UND pro App + Freeze + Injection-Detection + SIEM +
  Standard-Mesh about alle SSH-Targets + Provisioning/DB-Layer — **ein
  Stack, eine Instanz, self-hosted, not Premium-gated.**
- Schwäche, die wir akzeptieren: Workspace-UX/Templates 1–2 Jahre hinter
  Coder, wenn überhaupt. Kein Template-Marktplatz. Das ist OK — anderes
  Produktzentrum.

## 4. Konsequenzen for die Sprints

1. **Nicht bauen:** eigener Template-Marktplatz, IDE-Plugin-Suite,
   Workspace-Cosmetics („schöner als Coder"-Spielen).
2. **Bauen (Priorität):** Sprint 35 WP1 — User-Proxy-Keys +
   Service-Accounts („Kosten pro App"), WP3 Headscale-Enrollment
   (Mesh-First, „no komischen Tunnel"), K-LAF WP2–4, SIEM (Sprint 32).
3. **Preset-Muster from Coder übernehmen (Muster, no Code):** deklarative
   YAML-Templates for Framework-Presets (R35 §10.3).
4. **AGPL-Realität:** Coder ist als Basis for die Kommerz-Pläne
   (PolyForm-NC) ohnehin gesperrt — die Build-vs-Fork-Question stellt sich
   nie.

**Verweise:** `docs/research/R35-code-salvage-review.md` (Lizenzen,
Fundstellen), `docs/sprints/SPRINT-35-USER-KEYS-WORKSPACE-IDE-NETWORKS.md`
(Umsetzung), `docs/PRODUCT-ROADMAP.md` (§2 Access Policy).
