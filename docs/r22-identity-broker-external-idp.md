---
id: "R22"
title: "R22 — Identity Broker & External-IdP Federation (B2B/AWS-Self-Host)"
type: research
date: 2026-09-07
status: final
tags: [mesh, oauth, keycloak, opa, ufw]
license: CC-BY-4.0
---

# R22 — Identity Broker & External-IdP Federation (B2B/AWS-Self-Host)

> **Entschieden 7.9.2026: Keycloak, jetzt deployt — nicht die "Kontrakt
> jetzt, Broker später"-Empfehlung dieses Dokuments.** Der Operator wollte
> ordentliches Auth sofort, nicht erst bei einem konkreten B2B-Kunden, und
> zog Keycloak (Java, ausgereift/skalenerprobt) Zitadel (Go, leichter) vor.
> Volle Begründung: `docs/research/DECISIONS.md` ("E-IdP — Identity Broker:
> Keycloak"), Umsetzung: `sprint docs (internal)`.
> Dieses Dokument bleibt als vollständige Analyse aller geprüften Optionen
> stehen (Zitadel, Ory, jetzt auch Keycloak/Auth0/OpenFGA/Cerbos aus der
> Folgediskussion) — nur die Empfehlung in §4 ist überholt.

**Quelle:** Gemini-Recherche (separate Gemini-CLI-Session, parallel zu Claude,
7.9.2026), vom Operator eingebracht + gegen den bestehenden Repo-Stand
geprüft. Kein Code, reine Architektur-Entscheidungsvorlage.

**Frage, die Gemini beantwortet hat:** Wie soll JiMesh OAuth2/OIDC + OTP/MFA
anbieten UND so gebaut sein, dass ein Kunde/Partner, der JiMesh in seiner
eigenen Cloud (AWS, ggf. Azure/GCP) deployt, dort seinen eigenen Identity
Provider (AWS IAM Identity Center, Okta, Azure AD/Entra ID) per OAuth2/OIDC
anbinden kann — ohne dass JiMesh selbst pro Kunde einen Identity-Federation-
Stack von Hand baut.

**Wichtig — andere Achse als Epic 17/`DECISIONS.md` "Access Policy":** Das
dort bereits entschiedene P-R1 (Casbin vs. OPA, "kein Casbin/OPA für v1") ist
**Autorisierung** (was darf eine bereits authentifizierte Identität tun).
Dieses Dokument ist **Authentifizierung + Identity-Föderation** (wer ist die
Identität, welcher Provider hat sie bestätigt). Beide Achsen bewusst getrennt
halten, nicht in eine Entscheidung vermischen.

## 1. Bestehender Befund, auf dem das aufbaut (R20/TASK-001, TASK-002)

- `jimesh-auth` (saits-cloud): **Kontrakt gut, Code nicht.** Spezifiziert
  RS256, DPoP-Verifizierung am Ingress, `X-Tenant-Id` nur vom Ingress
  abgeleitet (nie vom Client), M2M-`tenant_id` aus dem mTLS-Cert-SAN. Der
  Code dahinter: HS256 statt RS256, kein DPoP-Verifier, Legacy-Claim-Format,
  Logout ist ein 204-Stub. Fazit aus TASK-001: Kontrakt übernehmen, Code
  nicht als Basis kopieren.
- Die tatsächlich fertige Referenz-Implementierung liegt in `sc-gateway`
  (TASK-002): **3-Stufen-Kette** — (1) `jwt-authn`: RS256-Signaturprüfung,
  `claim_to_headers` (`x-tenant-id-verified`/`x-actor-id`/`x-tenant-tier`);
  (2) DPoP-Verify: `cnf.jkt`-Thumbprint-Match, htm/htu-Binding (Query-Strip
  nach RFC 9449 §4.3), `iat` ±30s, JTI-Replay-Guard; (3) Tenant-Binding:
  Client-Hints strippen, Mismatch → 403 + Audit.
- Das ist der Maßstab, an dem sich jede neue Auth-Entscheidung für JiMesh
  messen lassen muss — nicht `jimesh-auth`.

## 2. Geminis Vorschlag (zusammengefasst, Original-Argumentation erhalten)

**Kernidee:** JiMesh braucht keinen monolithischen Auth-Eigenbau. Rollen-
teilung:

- **Ingress/Gateway (JiMesh selbst, Go):** bleibt bei der bereits
  spezifizierten 3-Stufen-Kette (RS256-Verify via `golang-jwt`, DPoP-Verify
  via `lestrrat-go/jwx`, Tenant-Binding). Zustandslos, schnell, kein
  zusätzlicher Service in der Hot-Path.
- **Identity Broker / Token Issuer (neuer, optionaler Baustein):** ein
  separater Service, der OAuth2/OIDC + OTP/MFA/Passkeys übernimmt UND als
  Brücke zu externen Kunden-IdPs (AWS IAM Identity Center, Okta, Azure AD)
  fungiert — stellt am Ende immer ein standardisiertes RS256-JWT im
  JiMesh-Kontrakt-Format aus (inkl. `tenant_id`-Claim), egal welcher
  Kunden-IdP im Hintergrund stand.

**Empfehlung: Zitadel** (komplett in Go geschrieben, self-hosted, ein
Container/Binary):
- Zertifizierter OIDC-Provider, stellt RS256-JWTs aus.
- Natives OTP/MFA (TOTP, Passkeys/WebAuthn, SMS/E-Mail).
- Externe IdPs (AWS, Azure AD, Okta) grafisch konfigurierbar via
  OIDC/SAML — kein Code nötig, wenn ein Kunde seinen eigenen IdP anbinden
  will.
- Organisations-Konzept = Multi-Tenancy nativ; Domain-Discovery beim Login
  routet automatisch zum richtigen Kunden-IdP.
- Rollen-Mapping: JiMesh definiert globale App-Rollen (reader/writer/admin),
  Zitadel erlaubt dem Kunden, seine externen Gruppen (aus AWS/Okta) darauf
  zu mappen — landet als Claim im JWT.

**Alternative: Ory Hydra + Kratos** (auch Go, mehr Kontrolle, mehr
Eigenbau): Hydra = reiner OAuth2/OIDC-Server (kennt keine User/Provider),
Kratos = Identity/Federation-Layer. Kein fertiges Admin-/Login-UI — das
Mapping externer Provider und die Tenant-Verwaltung müsste JiMesh komplett
selbst in Go bauen.

| | Zitadel | Ory Hydra+Kratos |
|---|---|---|
| Sprache/Laufzeit | Go, 1 Binary/Container | Go, mehrere Services |
| AWS-Cloud-Ready | Ja, einfach via ECS/EKS+RDS | Ja, über Helm-Charts |
| Externe Provider | OIDC+SAML, grafisch konfigurierbar | OIDC via API konfigurierbar |
| B2B Multi-Tenancy | Native Organisations-Isolation | Muss selbst über Kratos-Logik gebaut werden |
| Login-/Admin-UI | Vollständig vorhanden | Fehlt komplett — selbst bauen |
| Deployment | 1 Container | ≥2 Container + eigene UI-App |

**Architektur-Diagramm (Gemini):**

```
[ Client ]
   │ 1. Login/OAuth2/OTP
   ▼
[ Zitadel Container ] ──► RS256-JWT (inkl. tenant_id-Claim)
   │ 2. Request mit JWT + DPoP-Header
   ▼
[ sc-gateway-Muster (JiMesh Go Ingress) ]
   │  1. RS256 via golang-jwt validieren
   │  2. DPoP + Replay-Guard via lestrrat-go/jwx prüfen
   │  3. X-Tenant-Id-Header erzeugen (Client-Hints strippen)
   ▼
[ JiMesh Go-Services ] (konsumieren nur X-Tenant-Id + Rollen)
```

## 3. Kritische Einordnung gegen den bestehenden JiMesh-Stand (nicht nur übernommen)

- **Persistenz-Mandat (`MANDATES.md` §3/§7, "Postgres via pgx only, keine
  zweite Datenbank"):** Zitadel läuft technisch gegen Postgres (nicht
  zwingend CockroachDB), aber als **eigener Service mit eigenem, von
  JiMesh's `pgx`-Layer unabhängigem Schema**. Kein Mandatsverstoß im
  engeren Sinn (immer noch Postgres als Engine), aber ein zweiter,
  fremdverwalteter Datenbestand neben der einen JiMesh-Datenbank — nicht
  "kostenlos", verdient eine explizite Ops-Entscheidung, kein Kleingedrucktes.
- **"Keine neuen Abhängigkeiten ohne Not" (`MANDATES.md` §7):** Ein
  komplettes IAM-Produkt als Laufzeit-Abhängigkeit ist eine deutlich
  größere Entscheidung als eine Go-Library — das ist kein `go.mod`-Zeile,
  das ist ein neuer Betriebsbestandteil (Container, Backups, Updates,
  Monitoring, Angriffsfläche).
- **Produktstand:** `PRODUCT-ROADMAP.md` §1 beschreibt JiMesh aktuell als
  **Single-Operator zuerst**, Multi-Tenant/B2B ist E8 ("nur falls
  Multi-Tenant") — bereits in TASK-002 so eingeordnet
  (Clusterwide-Cross-Tenant-Deny "für später"). Externe-IdP-Föderation ist
  **kein Problem, das JiMesh heute hat** — es ist ein Problem, das erst
  entsteht, sobald ein Kunde JiMesh selbst hostet und sein eigenes AWS/Azure/
  Okta anbinden will.
- **Deshalb: Frage jetzt entscheiden, Zitadel nicht jetzt deployen.** Der
  Wert von R22 liegt darin, den Identitäts-**Kontrakt** (RS256, DPoP,
  `tenant_id`-Claim-Form) so zu fixieren, dass er Zitadel-kompatibel bleibt
  — genau das "Kontrakt übernehmen, Code nicht"-Prinzip aus TASK-001, jetzt
  ein zweites Mal angewendet. Der Broker selbst (Zitadel oder Ory) wird erst
  angeschaltet, wenn ein echter Kunde/Deal das braucht.
- **Wie WP1 (Sprint 20) heute schon funktioniert:** eigene Session-Tokens
  (`store.MintSessionToken`), kein externer IdP. Das bleibt der Default-Pfad
  für den Single-Operator-Fall — Zitadel/Ory ist ein **optionaler,
  zuschaltbarer** Broker für den B2B-Fall, kein Ersatz des bestehenden
  Login-Pfads.

## 4. Offene Fragen / Blockierende Entscheidung (Operator)

**E-IdP — Identity-Broker jetzt spezifizieren, aber nicht deployen?**

| Option | Aufwand jetzt | Konsequenz |
|---|---|---|
| **Kontrakt fixieren (Empfehlung), Broker erst bei Bedarf** | S — Doku + JWT-Claim-Form in `internal/auth` vorsehen | Kein neuer Service jetzt; sc-gateway-Muster (RS256+DPoP) ist das, was `internal/auth`/WP1 sowieso schon bauen soll |
| Zitadel jetzt als optionalen Container aufsetzen | M — neuer Compose-Service, eigenes Schema, Backup-Pflicht | Federation ab Tag 1 verfügbar, aber Betriebslast ohne aktuellen Kunden-Bedarf |
| Ory Hydra+Kratos jetzt aufsetzen | L — 2 Services + eigenes Login-UI in Go | Maximale Kontrolle, aber deutlich mehr Aufwand als Zitadel für denselben Nutzen |

**Empfehlung:** erste Option. Konkret zu klären:
1. Landet die RS256/DPoP/Tenant-Claim-Kontrakt-Doku in `internal/auth`s
   Package-Doc oder in einem neuen `docs/reference/AUTH-CONTRACT.md`?
2. Wird das bestehende WP1-Session-Token-System (`MintSessionToken`) auf
   RS256-JWT umgestellt, oder bleibt es ein separates internes Format,
   und nur der **externe** B2B-Pfad bekommt später Zitadel-JWTs? (Zwei
   Formate parallel ist plausibel: intern = einfach, extern/B2B = Zitadel-
   kompatibel — muss aber bewusst entschieden werden, nicht organisch
   entstehen.)
3. Wann wird "echter Kunden-Bedarf" für externe IdP-Föderation
   angenommen — vor oder nach dem ersten zahlenden B2B-Kunden?

## 5. Nicht Teil dieser Entscheidung

- P-R1 (Casbin vs. OPA) — siehe `DECISIONS.md` Epic 17, bereits
  entschieden ("kein Casbin/OPA für v1"), unabhängige Achse.
- SPRINT-22s E-Policy-Frage (Admin/RBAC-UI-Policy-Engine) — ebenfalls
  Autorisierung, nicht Authentifizierung/Föderation.
