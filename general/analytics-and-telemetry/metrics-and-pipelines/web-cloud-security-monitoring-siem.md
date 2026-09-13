---
okf_version: "1.0"
id: "okf-ana-met-web-cloud-security-monitoring-siem"
title: "Web & Cloud Security Threat Vectors, Suricata IDS & SIEM Monitoring Architecture"
topic: "general/analytics-and-telemetry"
subtopic: "metrics-and-pipelines"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - web-security
  - cloud-security
  - suricata
  - siem
  - intrusion-detection
  - threat-vectors
summary: "Comprehensive research specification covering web and cloud attack vectors, Suricata intrusion detection system integration, and security monitoring correlation."
---

# Web & Cloud Security Threat Vectors, Suricata IDS & SIEM Monitoring Architecture

## Executive Summary

Protecting cloud-native infrastructure requires defense-in-depth spanning web application security (OWASP Top 10), cloud control plane monitoring, host-based runtime telemetry, and network intrusion detection systems (IDS).

This specification details the threat landscape, Suricata IDS rule configuration, and log aggregation pipelines feeding cloud Security Information and Event Management (SIEM) systems.

---

## 1. Cloud & Web Threat Vector Classification

```
+-------------------------------------------------------------------+
|                        Attack Vectors                             |
+---------------------------------+---------------------------------+
| Web Application Layer           | Cloud Control & Runtime         |
| - SQL Injection (SQLi)          | - IAM Misconfigurations         |
| - Cross-Site Scripting (XSS)    | - Unauthenticated Metadata SSRF |
| - SSRF (Server-Side Request)    | - Docker Socket Mount Escalation|
| - Broken Object Level Auth      | - Kubernetes Token Theft        |
+---------------------------------+---------------------------------+
```

---

## 2. Network Intrusion Detection via Suricata

**Suricata** inspects network traffic in real-time, executing pattern matching, protocol decoding, and TLS fingerprinting.

### 2.1 Suricata Rule Configuration (`/etc/suricata/rules/custom.rules`)

```suricata
# Detect SSRF attempts targeting AWS/Cloud Metadata IP
alert http $HOME_NET any -> 169.254.169.254 any (msg:"CLOUD-SECURITY SSRF attempt to metadata service"; flow:established,to_server; http.header; content:"Host: 169.254.169.254"; sid:1000001; rev:1;)

# Detect SQL Injection signature in URI query
alert http $EXTERNAL_NET any -> $HOME_NET any (msg:"WEB-ATTACK SQLi UNION SELECT attempt"; flow:established,to_server; http.uri; content:"UNION"; nocase; content:"SELECT"; nocase; sid:1000002; rev:1;)
```

### 2.2 EVE JSON Output Stream Configuration

Suricata outputs structured `eve.json` logs containing decoded protocol headers and flow metadata:

```yaml
# suricata.yaml snippet
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      types:
        - alert:
            payload: yes
            http-body: yes
        - http
        - dns
        - tls
```

---

## 3. SIEM Ingestion & Log Correlation Pipeline

```
+------------------+
| Suricata IDS     | ---> eve.json
+------------------+              \
                                   +---> +-------------------+ ---> +-------------------+
+------------------+               |     | Vector / Fluentbit|      | OpenSearch / SIEM |
| Nginx Access Log | ---> json     +---> | Log Aggregator    | ---> | Threat Dashboard  |
+------------------+              /      +-------------------+      +-------------------+
                                 /
+------------------+            /
| Docker Engine    | ---> audit
+------------------+
```

---

## 4. Verification & Diagnostics

- [x] **Suricata Rule Verification**: `suricata -T -c /etc/suricata/suricata.yaml` passes syntax validation.
- [x] **Metadata SSRF Alert**: Simulated query to `http://169.254.169.254` triggers `sid:1000001` in `eve.json`.
- [x] **SIEM Parsing**: Confirmed `eve.alert.signature_id` correlates correctly across OpenSearch index patterns.
