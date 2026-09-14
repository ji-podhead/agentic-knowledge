---
okf_version: "1.0"
id: "okf-ana-met-grafana-11-5-prometheus-docker-compose"
title: "Zero-Touch Grafana 11.5 & Prometheus Provisioning via Docker Compose"
topic: "general/analytics-and-telemetry"
subtopic: "metrics-and-pipelines"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - grafana
  - prometheus
  - docker-compose
  - observability
  - metrics
summary: "Technical guide for zero-touch provisioning of Grafana 11.5 with Prometheus, automated datasources, dashboard providers, and target scraping via Docker Compose."
---

# Zero-Touch Grafana 11.5 & Prometheus Provisioning via Docker Compose

## Executive Summary

Setting up monitoring dashboards often involves manual UI clicks to add datasources, import dashboard JSON files, configure user permissions, and establish alert rules. This manual workflow hinders team velocity and infrastructure-as-code consistency.

This specification details zero-touch automated provisioning of **Grafana 11.5** and **Prometheus** using Docker Compose. Team members can launch a complete observability stack—pre-populated with PostgreSQL, Redis, and system exporters—with a single command (`docker compose up -d`).

---

## 1. Stack Architecture & Flow

```
+-------------------------------------------------------------------+
| Scraped Target Containers                                         |
|  +--------------------+  +------------------+  +---------------+  |
|  | PostgreSQL Exporter|  | Redis Exporter   |  | Node Exporter |  |
|  | (:9187)            |  | (:9121)          |  | (:9100)       |  |
|  +---------+----------+  +--------+---------+  +-------+-------+  |
+------------|----------------------|--------------------|----------+
             |                      |                    |
             +----------------------+--------------------+
                                    | Prometheus Scrape Loop
                                    v
+-------------------------------------------------------------------+
| Prometheus Time-Series Database (:9090)                           |
+-----------------------------------+-------------------------------+
                                    |
                                    | Auto-Provisioned Datasource
                                    v
+-------------------------------------------------------------------+
| Grafana 11.5 Dashboard Engine (:3000)                             |
| (Pre-loaded Dashboards, Datasources, and Security Admin Policies) |
+-------------------------------------------------------------------+
```

---

## 2. Docker Compose Infrastructure Manifest (`docker-compose.yml`)

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:v2.50.0
    container_name: monitoring-prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:11.5.0
    container_name: monitoring-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=[REDACTED_SECRET]
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./grafana/provisioning/datasources:/etc/grafana/provisioning/datasources:ro
      - ./grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

---

## 3. Provisioning Configurations

### 3.1 Prometheus Datasource Definition (`grafana/provisioning/datasources/prometheus.yml`)

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

### 3.2 Dashboard Provider Definition (`grafana/provisioning/dashboards/provider.yml`)

```yaml
apiVersion: 1

providers:
  - name: 'Default Provisioned Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

---

## Sources & References

- [https://github.com/ji-podhead/Grafana-11.5-with-Prometheus-and-Docker-Compose](https://github.com/ji-podhead/Grafana-11.5-with-Prometheus-and-Docker-Compose)
