---
okf_version: "1.0"
id: "okf-sec-asm-cyberspace-search-engines"
title: "Cyberspace Search Engines: Shodan, Censys, FOFA, ZoomEye and the OSINT Recon Stack"
topic: "general/security-and-observability"
subtopic: "attack-surface-management"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - osint
  - attack-surface-management
  - shodan
  - censys
  - fofa
  - zoomeye
  - jarm
  - cve-search
summary: "Reference catalog of the public internet-wide scanning platforms (Western and Chinese), how mass port scanning + banner grabbing + fingerprinting works, ASN-based hosting-provider filtering, direct CVE search, and JARM fingerprinting."
---

# Cyberspace Search Engines: Shodan, Censys, FOFA, ZoomEye and the OSINT Recon Stack

## Mechanism

Three-step pipeline, run continuously and at internet scale: (1) mass port scanning (Masscan, ZMap, Nmap, Naabu), (2) banner grabbing (record the raw protocol response — HTTP headers, TLS cert, SSH/DB handshake), (3) indexing/fingerprinting into a searchable database (product, version, ASN, geolocation, cert chain). No exploitation involved — pure protocol observation at scale.

## Platform catalog

| Platform | Origin | Strength |
|---|---|---|
| Shodan | USA | Original/reference; IoT, ICS, `vuln:` CVE filter (paid tier) |
| Censys | USA | Certificate-based infra mapping; CVE context (paid add-on) |
| FOFA | China (Huaxin) | Largest fingerprint DB, favicon/cert pivoting |
| ZoomEye | China (Knownsec 404) | IoT/device discovery |
| Quake | China (360/Qihoo) | Clean built-in CVE tagging |
| Hunter.how | China (Qianxin) | Web-component/API identification |
| Criminal IP | — | IP risk scoring |
| Onyphe | — | Active CVE/misconfig checks layered on scan data |
| Netlas.io | Europe | Wildcard/fuzzy search free where FOFA charges for it |
| Grayhat Warfare | — | Public AWS S3 / Azure Blob / GCS bucket index, filterable by extension |
| LeakIX | Belgium | Active leak detection: open Elasticsearch/MongoDB/Redis, exposed `.git` dirs |
| PublicWWW | — | Source-code (HTML/JS/CSS) search across live sites |
| Grep.app | — | Full-text regex search across ~500k active GitHub repos |

## Query patterns

```
ASN filter (Hetzner = AS24940):
  Shodan:  asn:AS24940 "MongoDB" port:27017
  FOFA:    asn="24940" && port="9200"

Direct CVE search:
  Shodan:  vuln:CVE-2021-44228          (paid tier)
  Censys:  services.vulnerabilities.cve: "CVE-2024-21626"   (paid add-on)
  Quake:   vuln: "CVE-2023-38606"

Vulnerability dorking (fallback when no CVE tag exists):
  Shodan:  product:"Apache httpd" version:"2.4.49"
  FOFA:    app="Apache" && version="2.4.49"
```

## JARM fingerprinting

TLS-handshake fingerprinting technique released by Salesforce (John Althouse, Andrew Smart, RJ Nunnally, Mike Brady, 2020 — same team as JA3). Identifies the underlying software/OS combination by how it negotiates TLS, independent of a spoofed or hidden version banner. Most cyberspace search engines support querying by JARM hash directly.

## AI infrastructure fingerprints

| Service | Port | Tell |
|---|---|---|
| Ollama | 11434 | body: `"Ollama is running"` |
| vLLM (OpenAI-compatible) | 8000 | `/v1/models`, `/v1/chat/completions` |
| Qdrant | 6333 (HTTP) / 6334 (gRPC) | body: `"qdrant - vector search engine"` |
| Milvus | 19530 (gRPC) | — |
| ChromaDB | 8000 | `nanoseconds_since_epoch` in root response |
| Gradio | 7860 | — |
| Streamlit | 8501 | — |
| Jupyter | 8888 | random token required by default (exception to the pattern) |

Common tell across all: HTTP `200 OK` with real application data instead of `401`/`403`, no login form in the response body.

## Secret/leak discovery (separate tooling stack)

- **Manual dorking**: `site:github.com "DB_PASSWORD" ext:env`, GitHub native: `path:.env "OPENAI_API_KEY"`, `language:javascript "sk-ant"`.
- **Automated/continuous**: TruffleHog and Gitleaks (full commit-history scan, entropy + regex); GitGuardian (real-time GitHub/GitLab/Bitbucket event-stream monitoring, catches leaks within seconds of push); Intelligence X (historical paste/Tor/Git-dump archive, selector-based search).
- **GitHub Secret Scanning** (free, default-on for public repos): recognizes partner key formats and notifies the provider directly — often auto-revoked within seconds.

## Source article

- articles repo: `attack-surface-osint/2026-09-16-attack-surface-osint-blogpost.md` ("How Hackers Find Your Infra Weakpoints, Leaks and Unprotected AI") — Part 1 of 2.

## Sources

- Shodan — https://www.shodan.io
- Censys — https://search.censys.io
- FOFA — https://fofa.info
- LeakIX — https://leakix.net
- Grayhat Warfare — https://buckets.grayhatwarfare.com
- JARM (Salesforce Engineering) — https://engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a/
- Gitleaks — https://github.com/gitleaks/gitleaks
- GitHub Secret Scanning — https://docs.github.com/en/code-security/secret-scanning
