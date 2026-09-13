---
okf_version: "1.0"
id: "okf-ide-idp-external-idp-integration"
title: "R22 — Identity Broker & External-IdP Federation (B2B/AWS-Self-Host)"
topic: "general/identity-and-access-control"
subtopic: "idp-integration"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - identity-and-access-control
  - idp-integration
summary: "> **Entschieden 7.9.2026: Keycloak, jetzt deployt — not die 'Kontrakt"
---

# R22 — Identity Broker & External-IdP Federation (B2B/AWS-Self-Host)

> **Entschieden 7.9.2026: Keycloak, jetzt deployt — not die "Kontrakt
> jetzt, Broker später"-Recommendation dieses Dokuments.** Der System Administrator wollte
> ordentliches Auth sofort, not erst at einem konkreten B2B-Kunden, and
> zog Keycloak (Java, ausgereift/skalenerprobt) Zitadel (Go, leichter) before.
> Volle Begründung: `docs/research/DECISIONS.md` ("E-IdP — Identity Broker:
> Keycloak"), Implementation: `docs/sprints/Milestone.md`.
> Dieses Dokument bleibt als vollständige Analyse aller geprüften Options
> stehen (Zitadel, Ory, jetzt auch Keycloak/Auth0/OpenFGA/Cerbos from der
> Folgediskussion) — nur die Recommendation in §4 ist überholt.

**Source:** Gemini-Research (separate Gemini-CLI-Session, parallel zu Claude,
7.9.2026), vom System Administrator eingebracht + gegen den bestehenden Repo-Stand
geprüft. Kein Code, reine Architektur-Decisionsvorlage.

**Frage, die Gemini beantwortet hat:** Wie soll The Multi-Provider Gateway OAuth2/OIDC + OTP/MFA
anbieten UND so gebaut sein, dass ein Kunde/Partner, der The Multi-Provider Gateway in seiner
eigenen Cloud (AWS, ggf. Azure/GCP) deployt, dort seinen eigenen Identity
Provider (AWS IAM Identity Center, Okta, Azure AD/Entra ID) per OAuth2/OIDC
anbinden kann — without dass The Multi-Provider Gateway selbst pro Kunde einen Identity-Federation-
Stack von Hand baut.

**Wichtig — andere Achse als Architecture Pillar/`DECISIONS.md` "Access Policy":** Das
dort bereits entschiedene P-R1 (Casbin vs. OPA, "no Casbin/OPA for v1") ist
**Autorisierung** (was darf eine bereits authentifizierte Identität tun).
Dieses Dokument ist **Authentifizierung + Identity-Föderation** (wer ist die
Identität, welcher Provider hat sie bestätigt). Beide Achsen bewusst getrennt
halten, not in eine Decision vermischen.

## 1. Bestehender Befund, on dem das aufbaut (R20/Requirement, Requirement)

- `llm-mesh-gateway-auth` (saits-cloud): **Kontrakt gut, Code not.** Spezifiziert
  RS256, DPoP-Verification am Ingress, `X-Tenant-Id` nur vom Ingress
  abgeleitet (nie vom Client), M2M-`tenant_id` from dem mTLS-Cert-SAN. Der
  Code dahinter: HS256 statt RS256, no DPoP-Verifier, Legacy-Claim-Format,
  Logout ist ein 204-Stub. Conclusion from Requirement: Kontrakt übernehmen, Code
  not als Basis kopieren.
- Die tatsächlich fertige Referenz-Implementation liegt in `sc-gateway`
  (Requirement): **3-Stufen-Kette** — (1) `jwt-authn`: RS256-Signaturprüfung,
  `claim_to_headers` (`x-tenant-id-verified`/`x-actor-id`/`x-tenant-tier`);
  (2) DPoP-Verify: `cnf.jkt`-Thumbprint-Match, htm/htu-Binding (Query-Strip
  after RFC 9449 §4.3), `iat` ±30s, JTI-Replay-Guard; (3) Tenant-Binding:
  Client-Hints strippen, Mismatch → 403 + Audit.
- Das ist der Maßstab, an dem sich jede neue Auth-Decision for The Multi-Provider Gateway
  messen lassen muss — not `llm-mesh-gateway-auth`.

## 2. Geminis Vorschlag (zusammengefasst, Original-Argumentation erhalten)

**Kernidee:** The Multi-Provider Gateway braucht keinen monolithischen Auth-Eigenbau. Rollen-
teilung:

- **Ingress/Gateway (The Multi-Provider Gateway selbst, Go):** bleibt at der bereits
  spezifizierten 3-Stufen-Kette (RS256-Verify via `golang-jwt`, DPoP-Verify
  via `lestrrat-go/jwx`, Tenant-Binding). Zustandslos, schnell, no
  zusätzlicher Service in der Hot-Path.
- **Identity Broker / Token Issuer (neuer, optionaler Baustein):** ein
  separater Service, der OAuth2/OIDC + OTP/MFA/Passkeys übernimmt UND als
  Brücke zu externen Kunden-IdPs (AWS IAM Identity Center, Okta, Azure AD)
  fungiert — stellt am Ende immer ein standardisiertes RS256-JWT im
  The Multi-Provider Gateway-Kontrakt-Format from (inkl. `tenant_id`-Claim), egal welcher
  Kunden-IdP im Background stand.

**Recommendation: Zitadel** (komplett in Go geschrieben, self-hosted, ein
Container/Binary):
- Zertifizierter OIDC-Provider, stellt RS256-JWTs from.
- Natives OTP/MFA (TOTP, Passkeys/WebAuthn, SMS/E-Mail).
- Externe IdPs (AWS, Azure AD, Okta) grafisch konfigurierbar via
  OIDC/SAML — no Code nötig, wenn ein Kunde seinen eigenen IdP anbinden
  will.
- Organisations-Konzept = Multi-Tenancy nativ; Domain-Discovery beim Login
  routet automatisch zum richtigen Kunden-IdP.
- Rollen-Mapping: The Multi-Provider Gateway definiert globale App-Rollen (reader/writer/admin),
  Zitadel erlaubt dem Kunden, seine externen Gruppen (from AWS/Okta) darauf
  zu mappen — landet als Claim im JWT.

**Alternative: Ory Hydra + Kratos** (auch Go, mehr Kontrolle, mehr
Eigenbau): Hydra = reiner OAuth2/OIDC-Server (kennt no User/Provider),
Kratos = Identity/Federation-Layer. Kein fertiges Admin-/Login-UI — das
Mapping externer Provider and die Tenant-Verwaltung müsste The Multi-Provider Gateway komplett
selbst in Go bauen.

| | Zitadel | Ory Hydra+Kratos |
|---|---|---|
| Sprache/Laufzeit | Go, 1 Binary/Container | Go, mehrere Services |
| AWS-Cloud-Ready | Ja, einfach via ECS/EKS+RDS | Ja, about Helm-Charts |
| Externe Provider | OIDC+SAML, grafisch konfigurierbar | OIDC via API konfigurierbar |
| B2B Multi-Tenancy | Native Organisations-Isolation | Muss selbst about Kratos-Logik gebaut werden |
| Login-/Admin-UI | Vollständig vorhanden | Fehlt komplett — selbst bauen |
| Deployment | 1 Container | ≥2 Container + own UI-App |

**Architektur-Diagramm (Gemini):**

```
[ Client ]
   │ 1. Login/OAuth2/OTP
   ▼
[ Zitadel Container ] ──► RS256-JWT (inkl. tenant_id-Claim)
   │ 2. Request with JWT + DPoP-Header
   ▼
[ sc-gateway-Muster (The Multi-Provider Gateway Go Ingress) ]
   │  1. RS256 via golang-jwt validieren
   │  2. DPoP + Replay-Guard via lestrrat-go/jwx prüfen
   │  3. X-Tenant-Id-Header erzeugen (Client-Hints strippen)
   ▼
[ The Multi-Provider Gateway Go-Services ] (konsumieren nur X-Tenant-Id + Rollen)
```

## 3. Kritische Einordnung gegen den bestehenden The Multi-Provider Gateway-Stand (not nur übernommen)

- **Persistence-Mandat (`MANDATES.md` §3/§7, "Postgres via pgx only, no
  zweite Datenbank"):** Zitadel läuft technisch gegen Postgres (not
  zwingend CockroachDB), aber als **eigener Service with eigenem, von
  The Multi-Provider Gateway's `pgx`-Layer unabhängigem Schema**. Kein Mandatsverstoß im
  engeren Sinn (immer noch Postgres als Engine), aber ein zweiter,
  fremdverwalteter Datenbestand neben der einen The Multi-Provider Gateway-Datenbank — not
  "kostenlos", verdient eine explizite Ops-Decision, no Kleingedrucktes.
- **"Keine neuen Abhängigkeiten without Not" (`MANDATES.md` §7):** Ein
  komplettes IAM-Produkt als Laufzeit-Abhängigkeit ist eine deutlich
  größere Decision als eine Go-Library — das ist no `go.mod`-Zeile,
  das ist ein neuer Betriebsbestandteil (Container, Backups, Updates,
  Monitoring, Angriffsfläche).
- **Produktstand:** `PRODUCT-ROADMAP.md` §1 beschreibt The Multi-Provider Gateway aktuell als
  **Single-System Administrator zuerst**, Multi-Tenant/B2B ist E8 ("nur falls
  Multi-Tenant") — bereits in Requirement so eingeordnet
  (Clusterwide-Cross-Tenant-Deny "for später"). Externe-IdP-Föderation ist
  **no Problem, das The Multi-Provider Gateway heute hat** — es ist ein Problem, das erst
  entsteht, sobald ein Kunde The Multi-Provider Gateway selbst hostet and sein eigenes AWS/Azure/
  Okta anbinden will.
- **Deshalb: Frage jetzt entscheiden, Zitadel not jetzt deployen.** Der
  Wert von R22 liegt darin, den Identitäts-**Kontrakt** (RS256, DPoP,
  `tenant_id`-Claim-Form) so zu fixieren, dass er Zitadel-kompatibel bleibt
  — genau das "Kontrakt übernehmen, Code not"-Prinzip from Requirement, jetzt
  ein zweites Mal angewendet. Der Broker selbst (Zitadel or Ory) wird erst
  angeschaltet, wenn ein echter Kunde/Deal das braucht.
- **Wie Work Package (Milestone) heute schon funktioniert:** own Session-Tokens
  (`store.MintSessionToken`), no externer IdP. Das bleibt der Default-Pfad
  for den Single-System Administrator-Fall — Zitadel/Ory ist ein **optionaler,
  zuschaltbarer** Broker for den B2B-Fall, no Ersatz des bestehenden
  Login-Pfads.

## 4. Offene Fragen / Blockierende Decision (System Administrator)

**E-IdP — Identity-Broker jetzt spezifizieren, aber not deployen?**

| Option | Aufwand jetzt | Konsequenz |
|---|---|---|
| **Kontrakt fixieren (Recommendation), Broker erst at Bedarf** | S — Doku + JWT-Claim-Form in `internal/auth` vorsehen | Kein neuer Service jetzt; sc-gateway-Muster (RS256+DPoP) ist das, was `internal/auth`/Work Package sowieso schon bauen soll |
| Zitadel jetzt als optionalen Container aufsetzen | M — neuer Compose-Service, eigenes Schema, Backup-Pflicht | Federation ab Tag 1 verfügbar, aber Betriebslast without aktuellen Kunden-Bedarf |
| Ory Hydra+Kratos jetzt aufsetzen | L — 2 Services + eigenes Login-UI in Go | Maximale Kontrolle, aber deutlich mehr Aufwand als Zitadel for denselben Nutzen |

**Recommendation:** erste Option. Konkret zu klären:
1. Landet die RS256/DPoP/Tenant-Claim-Kontrakt-Doku in `internal/auth`s
   Package-Doc or in einem neuen `docs/reference/AUTH-CONTRACT.md`?
2. Wird das bestehende Work Package-Session-Token-System (`MintSessionToken`) on
   RS256-JWT umgestellt, or bleibt es ein separates internes Format,
   and nur der **externe** B2B-Pfad bekommt später Zitadel-JWTs? (Zwei
   Formate parallel ist plausibel: intern = einfach, extern/B2B = Zitadel-
   kompatibel — muss aber bewusst entschieden werden, not organisch
   entstehen.)
3. Wann wird "echter Kunden-Bedarf" for externe IdP-Föderation
   angenommen — before or after dem ersten zahlenden B2B-Kunden?

## 5. Nicht Teil dieser Decision

- P-R1 (Casbin vs. OPA) — siehe `DECISIONS.md` Architecture Pillar, bereits
  entschieden ("no Casbin/OPA for v1"), unabhängige Achse.
- Milestone E-Policy-Frage (Admin/RBAC-UI-Policy-Engine) — ebenfalls
  Autorisierung, not Authentifizierung/Föderation.
