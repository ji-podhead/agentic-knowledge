---
okf_version: "1.0"
id: "okf-ide-idp-r42-app-certs-tailscale-plan"
title: "R42 — App-Certs-Plan: Tailscale-Magic-Certs + Wazuh-Fallback (14.9.)"
topic: "identity-and-access-management"
subtopic: "idp-integration"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - identity-and-access-management
  - idp-integration
summary: "**Quelle:** Operator 14.9. („wieso haben wir eigentlich keine certs für unsere"
---

# R42 — App-Certs-Plan: Tailscale-Magic-Certs + Wazuh-Fallback (14.9.)

**Quelle:** Operator 14.9. („wieso haben wir eigentlich no certs for unsere
apps? können wir das not with tailscale/headscale machen?") + cert-Fehlerbild
`net::ERR_CERT_AUTHORITY_INVALID` on Wazuh-Dashboard `https://localhost:5601`.

## Fakten (verifiziert)

- **Tailscale läuft**: Tailnet `[tailnet]`, Node `workstation`, MagicDNS-Name
  `[tailnet-domain]`, MagicDNS aktiv
- **Tailscale SaaS = DNS-Authority for ACME DNS-01** on `*.[tailnet-domain].ts.net`
  → `tailscale cert` holt echte Let's-Encrypt-Certs (vertrauenswürdig überall)
- **Wazuh-Cert-Ursache (2 Defekte):** (a) CA = Wazuh-eigen (unbekannt im
  Browser → AUTHORITY_INVALID), (b) SAN nur `DNS:wazuh.dashboard` —
  `localhost`/`127.0.0.1` FEHLEN → auch with vertrauter CA würde
  COMMON_NAME_INVALID kommen. gen-certs.sh generiert nur den Node-Namen.
- Keycloak :8081 = **no TLS** (HTTP) — for Browser-Zugriff via Tailscale-Serve
  später with echtem Cert aufladbar
- `tailscale serve status` = "No serve config" — Feature ist verfügbar, nichts
  konfiguriert

## Der Plan (zukünftige Tasks)

### TASK-080 — App-Certs via Tailscale-Magic-DNS (WURZEL-LÖSUNG, P0)
- **WP1:** `tailscale cert [tailnet-domain]` — echtes LE-Cert (DNS-01,
  Tailscale als Authority); cert-file unter /var/lib/tailscale/certs/
- **WP2:** `tailscale serve` konfigurieren: https://[tailnet-domain]
  → :5601 (Wazuh-Dashboard), :8081 (Keycloak), :19090 (jr), :19091 (API) —
  with echtem Cert, Reverse-Proxy-Modus
- **WP3:** Verify: Browser-Zugriff without Warnung, iframe-fähig (TASK-067-Revisit:
  iframe statt new-tab geht wieder, da cert vertraut + same-origin via Proxy)
- **WP4:** Doku: USER_GUIDE + ARCHITECTURE (Tailscale als Cert+VPN-Grundlage)

### TASK-080a — Wazuh-localhost-Fallback (P1, for offline/without-Tailnet)
- **WP1:** gen-certs.sh SAN erweitern: `DNS:wazuh.dashboard, DNS:localhost,
  IP:127.0.0.1` (heute nur Node-Name)
- **WP2:** Regen + Dashboard-Restart
- **WP3:** CA-Trust installieren: `update-ca-certificates` (System) +
  Chrome-NSSDB `certutil -d sql:$HOME/.pki/nssdb -A -t "C,,"` (Browser)
- **WP4:** Verify: `curl https://localhost:5601` without -k → 200

### TASK-080b — Keycloak-TLS (P2, optional)
- Keycloak :8081 läuft HTTP — for Browser-Zugriff about Tailscale-Serve später
  echtes Cert; lokal bleibt HTTP ok (nur localhost, Dev)
- Für Produktion (öfter Extern): Keycloak-Production-Mode with eigenem Cert

## Entscheidung (Operator): Tailscale SaaS vs. Headscale self-hosted
- **Tailscale SaaS (empfohlen, läuft schon):** Magic-Domain-Feature eingebaut,
  echte LE-Certs for `*.ts.net` kostenlos, DNS-01 automatisch. Nachteil:
  Domain gehört Tailscale (`[tailnet-domain].ts.net`), Service ist Dritt-Cloud
  (macht nichts for Certs — die Nodes sind eh im Tailnet)
- **Headscale self-hosted (Alternative, wenn eigenes Domain-Branding):**
  Headscale selbst kann KEINE ACME-Certs for Clients (no DNS-Authority
  for fremde Domains). Du brauchst: eigene Domain + Caddy/Lego with DNS-01
  via eigenem DNS-Provider → real cert, gleicher Effekt, mehr Setup. Lohnt
  nur wenn du `*.workstation.example`-Branding willst.
- **Empfehlung:** Tailscale SaaS jetzt (0-Mehraufwand, 0-Risiko),
  Headscale/Mkcert fürs Offline-Dev-Fallback (TASK-080a).

## Wazuh-iframe-Revisit (TASK-067-Erweiterung after TASK-080)
- Mit echtem Cert on :5601 (via Tailscale-Serve, same-origin) or
  localhost+CA-Trust (via 080a) → iframe geht wieder, Operator-UX besser

## Erweiterung (14.9., Operator-Question): Extern via Cloudflare + Router-Ports

### TASK-081 — Extern via Cloudflare-Tunnel (P0 for Extern, after 080)
- **WP1:** `cloudflared` deployen (Container, outbound-only — **no
  Router-Port-Forwarding nötig** for HTTP(S))
- **WP2:** Eigene Domain in Cloudflare (Operator: Domain registrieren/bestehende
  einbinden — Wazuh/Ky/Jr-Hostnames als CNAME→Tunnel)
- **WP3:** Tunnel-Routen: `siem.<domain>` → :5601, `auth.<domain>` → :8081,
  `jr.<domain>` → :19090, `api.<domain>` → :19091 — **Cloudflare-Edge beendet
  TLS with echten Certs** (no Cert-Management on unserer Seite)
- **WP4:** Optional: Cloudflare-Origin-CA-Cert for Origin↔Edge (wenn Origin
  HTTPS soll; HTTP hinter Tunnel reicht meist)
- **WP5:** Access-Policies (Cloudflare Access = Zero-Trust before den Apps,
  ersetzt teils IP-Allowlists)

### TASK-081a — Router-Port-Forwarding (Networking-Task, P2)
- Nur nötig for **not-HTTP(S)-Dienste** (Wazuh-Agent 1514/1515, SIEM-Syslog
  514/udp, SSH) — for HTTP(S) ist der Tunnel die saubere Lösung (0
  Router-Config, 0 Angriffsfläche on dem Router)
- Router-Forwarding-Task gehört in die Networking-Epik (R42-Fußnote)
- **Hinweis:** 31 Listener on 0.0.0.0/::: — before Extern-Freigabe hart prüfen,
  was wirklich exponiert werden soll (Defaults: nur Tunnel-Routen, no
  Router-Forwarding)

### Integration der Certs (das Anliegen des Operators)
- **Intern (Tailnet):** `*.[tailnet-domain].ts.net` — echte LE-Certs via Tailscale
  (TASK-080) → gleiche Cert-Kette for Wazuh/Ky/Jr
- **Extern (Cloudflare):** `*.deine-domain` — echte Edge-Certs via Cloudflare
  (TASK-081) → Browser sieht Cloudflare-Edge, Origin-Zertifikate optional
- **Gemeinsame Integration:** Eine `apps.yml` (or service-map) als
  Single-Source-of-Truth: for jeden App-Slot ein Eintrag with internem Port,
  Tailnet-Hostname (080) and CF-Hostname (081) — dann rendert/serviert das
  beide Wege konsistent

## Die Port-Schichten (Operator-Question 14.9.: „Ports machen wir about die WAF?")

**Answer: WAF = L7-Inspektion IM Pfad — aber die „Freigabe"-Entscheidung
liegt in anderen Schichten.** Die externe Erreichbarkeits-Kette:

```
Extern (Cloudflare-Tunnel TASK-081 / Tailscale-Serve TASK-080)
   → TLS-Termination (echte Certs, Edge/serve)
   → Router-Node-Firewall (TASK-050, GEBUT): openmesh_inbound Default-DROP
     pro Alias — Operator-Grant entscheidet, WELCHER Port überhaupt offen ist
   → WAF-Sidecar (TASK-057, GEBUT, opt-in): L7-HTTP-Inspektion (OWASP-CRS)
     — filtert SQLi/XSS BEVOR die App es sieht
   → App-Container (Zero-Port, Mandat 12: publiziert nichts)
```

- **„Port freigeben"** = Router-Grant (TASK-050) + Operator-UI (TASK-053-Firewall-
  Rules-Editor, gebaut) + Tunnel/Cloudflare-Routing — **die WAF öffnet nichts,
  sie filtert was durchkommt**
- **WAF im Pfad** = for extern erreichbare HTTP-Ports Default (SPRINT-31 §4:
  WAF sitzt zwischen Tunnel-Endpunkt and App, Mandat 12 bleibt exakt erfüllt —
  einzige -p-Bindung ist die WAF on 127.0.0.1)
- **Offene Lücke (Networking-Task):** die Verkabelung „extern-erreichbarer Port
  → automatisch with WAF im Pfad" (heute opt-in per DeployRequest-Flag; soll
  for extern-exposed Apps Default werden — TASK-082-Kandidat)
- **Nicht-HTTP-Ports** (Wazuh-Agent 1514, Syslog 514/udp, SSH): no WAF-Pfad
  (L7-Inspektion setzt HTTP voraus) — hier sind Router-Grant + Tailscale die
  Kontrollebenen

### TASK-082 (neu, Networking): Exposed-Ports-Default-WAF + Ports-UI
- WP1: DeployRequest-Semantik — wenn ein Port extern exponiert wird
  (Cloudflare-Routing/Tailscale-Serve), ist WAF-Opt-in Pflicht or Warnung
- WP2: Ports-Section in Workspaces UND Apps (R41-C2: allocated Host-Ports,
  WAF-Status je Port, Grant-Status je Port — eine Sicht)
- WP3: Router-Firewall-Grants ↔ WAF-Status ↔ Tunnel-Routen in einer
  Exposure-Matrix (SecurityExposurePage-Erweiterung)
