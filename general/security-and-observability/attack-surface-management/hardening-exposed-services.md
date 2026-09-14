---
okf_version: "1.0"
id: "okf-sec-asm-hardening-exposed-services"
title: "Hardening Checklist: Closing Attack-Surface Gaps Found by OSINT Scanners"
topic: "general/security-and-observability"
subtopic: "attack-surface-management"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - attack-surface-management
  - hardening
  - network-isolation
  - ai-infrastructure
  - secret-management
summary: "Defensive playbook mirroring the cyberspace-search-engine reconnaissance techniques: self-audit cadence, cloud config auditing, default-deny network posture, AI-infra bind/auth/isolate fixes, and secret-leak prevention layers."
---

# Hardening Checklist: Closing Attack-Surface Gaps Found by OSINT Scanners

Companion defense doc to [[okf-sec-asm-cyberspace-search-engines]]. Same queries, run against your own infrastructure, on a schedule rather than once.

## By category

**Self-inventory** — run your own ASN/domain set through Shodan/Censys/FOFA monthly minimum; infrastructure drifts between audits.

**Cloud storage/databases** — Prowler / Scout Suite against AWS/GCP/Azure on a schedule (CIS benchmark checks via the cloud API). For Elasticsearch/MongoDB/Redis specifically: auth *plus* network placement — these shipped no-auth-by-default for years under a "trusted internal network" assumption that breaks the moment a cloud template opens the port outward.

**ASN/hosting exposure** — default-deny security groups/`ufw`, open by explicit rule only. Re-scan after any infra change (new subnet, LB reconfig).

**CVE exposure** — Nuclei (ProjectDiscovery) against own hosts on a schedule; community CVE templates typically land within hours of disclosure. Patch on CVE severity + inventory, not on banner claims (JARM can unmask a spoofed banner either way).

**AI infrastructure** — the fix set is uniform across Ollama/vLLM/Qdrant/Milvus/Gradio/Streamlit/Jupyter:
1. Bind to `127.0.0.1`, never `0.0.0.0`, unless the service must be reachable externally.
2. Never disable auth "for local convenience" in a config that will be reused in production (Jupyter's own default token behavior is the correct model to copy).
3. Reverse proxy in front of anything externally reachable — the proxy owns auth/rate-limit/TLS, not the app.
4. **Network-layer isolation, not just app-layer**: a compromised AI service on its own segment with an explicit egress allowlist can't pivot laterally even if its own auth check fails. This is the architectural justification for running agent workspaces inside a sandboxed runtime (gVisor) behind a per-project VLAN rather than trusting app-layer auth alone.
5. Firewall the known AI dev ports by default: 6333, 7860, 8000, 8501, 8888, 11434, 19530.

Ollama specifically: binds to `127.0.0.1` by design with **no auth mechanism at all** — the ~175k exposed instances found in 2025 scans came from Docker/Compose setups explicitly rebinding to `0.0.0.0`, which is the standard way to make it reachable from another container. Milvus, when auth *is* enabled, ships default credentials `root`/`Milvus` — "enabled" isn't "secured" until that default is changed too.

**Secret leaks** — layered defense, cheapest first: (1) `.gitignore` before the first commit — `.env`, `*.pem`, `*.key`; (2) pre-commit hook running Gitleaks locally; (3) Gitleaks/equivalent as a CI gate that blocks the merge; (4) GitHub Secret Scanning as the last line (free, default-on for public repos, provider-notified auto-revocation); (5) rotate on any suspicion immediately — don't wait for confirmed impact.

## The common thread

Every finding in this category is a control that exists but isn't the default, never explicitly turned on. Fix pattern: bind narrowly, authenticate explicitly, isolate at the network layer regardless of app-layer state, audit on a schedule with the same tools an attacker would use.

## Source article

- articles repo: `hardening-the-recon-surface/2026-09-16-hardening-the-recon-surface-blogpost.md` ("Closing the Gaps") — Part 2 of 2.

## Sources

- Prowler — https://github.com/prowler-cloud/prowler
- Scout Suite — https://github.com/nccgroup/ScoutSuite
- Nuclei — https://github.com/projectdiscovery/nuclei
- Ollama auth issue — https://github.com/ollama/ollama/issues/2194
- Jupyter server security docs — https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- gVisor — https://gvisor.dev
