---
okf_version: "1.0"
id: "okf-net-vpn-tailscale-app-certificates"
title: "R42 — App-Certs-Plan: Tailscale-Magic-Certs + Wazuh-Fallback (14.9.)"
topic: "general/networking"
subtopic: "vpn-and-overlay"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - networking
  - vpn-and-overlay
summary: "**Source:** System Administrator 14.9. („wieso haben wir eigentlich no certs for unsere"
---

# R42 — App-Certs-Plan: Tailscale-Magic-Certs + Wazuh-Fallback (14.9.)

**Source:** System Administrator 14.9. („wieso haben wir eigentlich no certs for unsere
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

<<<<<<< HEAD:knowledge/identity-and-access-management/idp-integration/r42-app-certs-tailscale-plan.md
### TASK-080 — App-Certs via Tailscale-Magic-DNS (WURZEL-LÖSUNG, P0)
- **WP1:** `tailscale cert [tailnet-domain]` — echtes LE-Cert (DNS-01,
  Tailscale als Authority); cert-file unter /var/lib/tailscale/certs/
- **WP2:** `tailscale serve` konfigurieren: https://[tailnet-domain]

### Requirement — App-Certs via Tailscale-Magic-DNS (WURZEL-LÖSUNG, P0)
- **Work Package:** `tailscale cert podhead.taile6d410.ts.net` — echtes LE-Cert (DNS-01,
  Tailscale als Authority); cert-file unter /var/lib/tailscale/certs/
- **Work Package:** `tailscale serve` konfigurieren: https://podhead.taile6d410.ts.net
  → :5601 (Wazuh-Dashboard), :8081 (Keycloak), :19090 (jr), :19091 (API) —
  with echtem Cert, Reverse-Proxy-Modus
- **Work Package:** Verify: Browser-Zugriff without Warnung, iframe-fähig (Requirement:
  iframe statt new-tab geht wieder, da cert vertraut + same-origin via Proxy)
- **Work Package:** Doku: USER_GUIDE + ARCHITECTURE (Tailscale als Cert+VPN-Grundlage)

### Requirement — Wazuh-localhost-Fallback (P1, for offline/without-Tailnet)
- **Work Package:** gen-certs.sh SAN erweitern: `DNS:wazuh.dashboard, DNS:localhost,
  IP:127.0.0.1` (heute nur Node-Name)
- **Work Package:** Regen + Dashboard-Restart
- **Work Package:** CA-Trust installieren: `update-ca-certificates` (System) +
  Chrome-NSSDB `certutil -d sql:$HOME/.pki/nssdb -A -t "C,,"` (Browser)
- **Work Package:** Verify: `curl https://localhost:5601` without -k → 200

### Requirement — Keycloak-TLS (P2, optional)
- Keycloak :8081 läuft HTTP — for Browser-Zugriff about Tailscale-Serve später
  echtes Cert; lokal bleibt HTTP ok (nur localhost, Dev)
- Für Produktion (öfter Extern): Keycloak-Production-Mode with eigenem Cert

## Decision (System Administrator): Tailscale SaaS vs. Headscale self-hosted
- **Tailscale SaaS (empfohlen, läuft schon):** Magic-Domain-Feature eingebaut,
  echte LE-Certs for `*.ts.net` kostenlos, DNS-01 automatisch. Nachteil:
  Domain gehört Tailscale (`[tailnet-domain].ts.net`), Service ist Dritt-Cloud
  (macht nichts for Certs — die Nodes sind eh im Tailnet)
- **Headscale self-hosted (Alternative, wenn eigenes Domain-Branding):**
  Headscale selbst kann KEINE ACME-Certs for Clients (no DNS-Authority
  for fremde Domains). Du brauchst: own Domain + Caddy/Lego with DNS-01
  via eigenem DNS-Provider → real cert, gleicher Effekt, mehr Setup. Lohnt
<<<<<<< HEAD:knowledge/identity-and-access-management/idp-integration/r42-app-certs-tailscale-plan.md
  nur wenn du `*.workstation.example`-Branding willst.
- **Empfehlung:** Tailscale SaaS jetzt (0-Mehraufwand, 0-Risiko),
  Headscale/Mkcert fürs Offline-Dev-Fallback (TASK-080a).
=======
  nur wenn du `*.podhead.example`-Branding willst.
- **Recommendation:** Tailscale SaaS jetzt (0-Mehraufwand, 0-Risiko),
  Headscale/Mkcert fürs Offline-Dev-Fallback (Requirement).

## Wazuh-iframe-Revisit (Requirement after Requirement)
- Mit echtem Cert on :5601 (via Tailscale-Serve, same-origin) or
  localhost+CA-Trust (via 080a) → iframe geht wieder, System Administrator-UX besser

## Erweiterung (14.9., System Administrator-Frage): Extern via Cloudflare + Router-Ports

### Requirement — Extern via Cloudflare-Tunnel (P0 for Extern, after 080)
- **Work Package:** `cloudflared` deployen (Container, outbound-only — **no
  Router-Port-Forwarding nötig** for HTTP(S))
- **Work Package:** Eigene Domain in Cloudflare (System Administrator: Domain registrieren/bestehende
  einbinden — Wazuh/Ky/Jr-Hostnames als CNAME→Tunnel)
- **Work Package:** Tunnel-Routen: `siem.<domain>` → :5601, `auth.<domain>` → :8081,
  `jr.<domain>` → :19090, `api.<domain>` → :19091 — **Cloudflare-Edge beendet
  TLS with echten Certs** (no Cert-Management on unserer Seite)
- **Work Package:** Optional: Cloudflare-Origin-CA-Cert for Origin↔Edge (wenn Origin
  HTTPS soll; HTTP hinter Tunnel reicht meist)
- **Work Package:** Access-Policies (Cloudflare Access = Zero-Trust before den Apps,
  ersetzt teils IP-Allowlists)

### Requirement — Router-Port-Forwarding (Networking-Task, P2)
- Nur nötig for **not-HTTP(S)-Dienste** (Wazuh-Agent 1514/1515, SIEM-Syslog
  514/udp, SSH) — for HTTP(S) ist der Tunnel die saubere Lösung (0
  Router-Config, 0 Angriffsfläche on dem Router)
- Router-Forwarding-Task gehört in die Networking-Epik (R42-Fußnote)
- **Hinweis:** 31 Listener on 0.0.0.0/::: — before Extern-Freigabe hart prüfen,
  was wirklich exponiert werden soll (Defaults: nur Tunnel-Routen, no
  Router-Forwarding)

<<<<<<< HEAD:knowledge/identity-and-access-management/idp-integration/r42-app-certs-tailscale-plan.md
### Integration der Certs (das Anliegen des Operators)
- **Intern (Tailnet):** `*.[tailnet-domain].ts.net` — echte LE-Certs via Tailscale
  (TASK-080) → gleiche Cert-Kette for Wazuh/Ky/Jr
=======
### Integration der Certs (das Anliegen des System Administrators)
- **Intern (Tailnet):** `*.taile6d410.ts.net` — echte LE-Certs via Tailscale
  (Requirement) → gleiche Cert-Kette for Wazuh/Ky/Jr
- **Extern (Cloudflare):** `*.deine-domain` — echte Edge-Certs via Cloudflare
  (Requirement) → Browser sieht Cloudflare-Edge, Origin-Zertifikate optional
- **Gemeinsame Integration:** Eine `apps.yml` (or service-map) als
  Single-Source-of-Truth: for jeden App-Slot ein Eintrag with internem Port,
  Tailnet-Hostname (080) and CF-Hostname (081) — dann rendert/serviert das
  beide Wege konsistent

## Die Port-Schichten (System Administrator-Frage 14.9.: „Ports machen wir about die WAF?")

**Antwort: WAF = L7-Inspektion IM Pfad — aber die „Freigabe"-Decision
liegt in anderen Schichten.** Die externe Erreichbarkeits-Kette:

```
Extern (Cloudflare-Tunnel Requirement / Tailscale-Serve Requirement)
   → TLS-Termination (echte Certs, Edge/serve)
   → Router-Node-Firewall (Requirement, GEBUT): gateway_inbound Default-DROP
     pro Alias — System Administrator-Grant entscheidet, WELCHER Port überhaupt offen ist
   → WAF-Sidecar (Requirement, GEBUT, opt-in): L7-HTTP-Inspektion (OWASP-CRS)
     — filtert SQLi/XSS BEVOR die App es sieht
   → App-Container (Zero-Port, Mandat 12: publiziert nichts)
```

- **„Port freigeben"** = Router-Grant (Requirement) + System Administrator-UI (Requirement
  Rules-Editor, gebaut) + Tunnel/Cloudflare-Routing — **die WAF öffnet nichts,
  sie filtert was durchkommt**
- **WAF im Pfad** = for extern erreichbare HTTP-Ports Default (Milestone §4:
  WAF sitzt zwischen Tunnel-Endpunkt and App, Mandat 12 bleibt exakt erfüllt —
  einzige -p-Bindung ist die WAF on 127.0.0.1)
- **Offene Lücke (Networking-Task):** die Verkabelung „extern-erreichbarer Port
  → automatisch with WAF im Pfad" (heute opt-in per DeployRequest-Flag; soll
  for extern-exposed Apps Default werden — Requirement)
- **Nicht-HTTP-Ports** (Wazuh-Agent 1514, Syslog 514/udp, SSH): no WAF-Pfad
  (L7-Inspektion setzt HTTP voraus) — hier sind Router-Grant + Tailscale die
  Kontrollebenen

### Requirement (neu, Networking): Exposed-Ports-Default-WAF + Ports-UI
- Work Package: DeployRequest-Semantik — wenn ein Port extern exponiert wird
  (Cloudflare-Routing/Tailscale-Serve), ist WAF-Opt-in Pflicht or Warnung
- Work Package: Ports-Section in Workspaces UND Apps (R41-C2: allocated Host-Ports,
  WAF-Status je Port, Grant-Status je Port — eine Sicht)
- Work Package: Router-Firewall-Grants ↔ WAF-Status ↔ Tunnel-Routen in einer
  Exposure-Matrix (SecurityExposurePage-Erweiterung)
