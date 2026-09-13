---
okf_version: "1.0"
id: "okf-ide-idp-r42-hosted-app-auth-integration"
title: "R42 — Superadmin Visibility into a Hosted App's Own Auth/RBAC: Design Synthesis"
topic: "identity-and-access-management"
subtopic: "idp-integration"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - identity-and-access-management
  - idp-integration
summary: "**Quelle:** Operator-Frage 14.9.2026 ('wir wollen als superadmin auch direkt"
---

# R42 — Superadmin Visibility into a Hosted App's Own Auth/RBAC: Design Synthesis

**Quelle:** Operator-Question 14.9.2026 ("wir wollen als superadmin auch direkt
die auths and datenbanken and rbac der apps verwalten... das selbe rbac and
die rollen in den apps sollte man dann auch direkt about openmesh benutzen
können"). Konkreter Anlass: der Chef des Operators hat Better Auth in seinen
eigenen Server integriert; der Operator wird diesen Server als OpenMesh-
Deployment absichern. Research about 9 Gemini-Prompts (`R42_multi.md`,
`R42_multi2.md`) — dieses Dokument synthetisiert die Rohantworten zu einer
Entscheidung.

**Status:** Design-Vorschlag, not gebaut. Keine Code-Änderung in diesem
Dokument.

---

## 1. Das Problem, präzise gefasst

OpenMesh hostet fremde Apps (SSH Remote Target → Workspace → App). Jede App
hat typischerweise ihr eigenes End-User-Auth-System (Better Auth, Lucia,
Auth.js, Ory Kratos, Supabase Auth, Clerk — je nachdem, was der App-
Entwickler gewählt hat). Der Operator will als Superadmin in OpenMesh sehen
(and teilweise verwalten) können, wer in der gehosteten App Nutzer/Rolle X
ist — without for jede App-Auth-Bibliothek eine eigene, tief gekoppelte
Integration zu bauen, and without die Sicherheits-/Rechtsrisiken einer
naiven "wir lesen einfach die DB" Lösung einzugehen.

## 2. Die zuerst naheliegende Idee war falsch — warum

Der ursprüngliche Gedanke (weil OpenMesh's Router-Node ohnehin als DB-Proxy
before jeder App-Datenbank sitzt — Sprint 36 WP2): einfach die Auth-Tabellen
der App direkt about den Router lesen. Die Recherche (Prompt 1+2)
widerlegt das als **Default-Ansatz**, from drei konkreten, technischen
Gründen — not nur "das ist unüblich", sondern **so bricht es real**:

- **Cache-/Session-Desync (kritisch):** Better Auth (and die meisten
  modernen Auth-Libs) cachen Session-Status in Redis (`secondaryStorage`)
  or verschlüsselt im Browser-Cookie (`cookieCache`). Ein direkter
  DB-Write (z. B. `banned = true` setzen) erreicht diese Caches not —
  der Nutzer bleibt bis zum TTL-Ablauf eingeloggt, obwohl OpenMesh ihn
  gesperrt zu haben glaubt. Ein `docker stop` on Container-Ebene würde
  das umgehen, aber genau das will der Operator hier not (er will
  granulare App-User-Verwaltung, not nur Container-Freeze).
- **Schema-Drift:** Auch at Libraries with einem "stabilen Kern-Schema"
  (Better Auth's `user`/`session`/`account`/`verification` sind laut
  eigener Doku ein versionierter, öffentlicher Vertrag) brechen
  Custom-Felder (`additionalFields`), Plugins (Multi-Tenant-Orgs,
  Admin-Plugin fügt eigene Spalten hinzu) and abweichende
  Tabellennamen/Types je after ORM-Adapter (Drizzle/Prisma/Kysely/raw SQL)
  einen starren Lesezugriff.
- **Krypto-/Event-Bypass:** Ein direkter `INSERT` in die `user`-Tabelle
  umgeht Passwort-Hashing (Argon2id/bcrypt-Ableitung passiert im
  App-Code, not in der DB), Lifecycle-Hooks and Audit-Logs/Webhooks der
  App. Für **reines Lesen** ist dieses Risiko gering; for **Schreiben**
  (Rolle ändern, Sperren) ist es real and laut Recherche "dringend
  abzuraten".

Zusätzlich: das Präzedenzfall-Bild ist eindeutig. Reine PaaS-Hoster
(Vercel, Render, Railway, Fly.io) tun das **nie** — sie behandeln
Kunden-DB-Inhalt strikt als Blackbox. Nur echte BaaS-Anbieter (Supabase,
Firebase) lesen Auth-Tabellen direkt — aber nur, weil sie selbst die
Auth-Bibliothek geschrieben/kontrolliert haben (Supabase hat GoTrue
selbst gebaut). OpenMesh ist in der Rolle "hostet fremden, not
selbstgeschriebenen Auth-Code" — das ist strukturell näher an
Vercel/Railway als an Supabase. Ein real dokumentierter Vorfall stützt
das: die Supabase `SECURITY DEFINER`-Trigger-Privilegien-Eskalation
(2022/23) entstand exakt from der Kultur, Entwickler zu ermutigen, direkt
with Auth-Tabellen zu interagieren.

**Konsequenz:** Roher DB-Zugriff on App-Auth-Tabellen ist no
Default-Pfad for dieses Feature. Punkt.

## 3. Die Admin-API-Alternative — auch not der richtige Default

Better Auth hat ein offizielles Admin-Plugin (`/admin/get-user`,
`/admin/ban-user`, `/admin/list-user-sessions`, with eigenem RBAC about
`adminRoles`/Custom-Permissions). Das klingt zunächst wie die saubere
Lösung — hat aber drei Eigenschaften, die es for OpenMeshs Fall (ein
**externer** Dienst, der **viele fremde** Apps verwalten will)
unpraktisch machen:

1. **Strikt Opt-in with DB-Migration.** Der App-Betreiber muss das Plugin
   im Code registrieren UND `npx better-auth migrate` laufen lassen
   (neue Spalten: `role`, `banned`, `banReason`, `banExpires`,
   `impersonatedBy`). Eine bereits laufende App (wie die des Chefs) kann
   das not rückwirkend "einfach so" freischalten — es erfordert
   bewusste Code-Änderung through den App-Eigentümer.
2. **Server-zu-Server-Aufruf ist als Same-Process-Import gedacht, not
   als HTTP-Call.** Die Doku zeigt `auth.api.banUser(...)` als direkten
   In-Process-Funktionsaufruf innerhalb derselben Node-Anwendung — not
   als HTTP-Request von einem externen Go-Service. Für echte
   HTTP-Server-zu-Server-Aufrufe bräuchte man zusätzlich das separate
   `apiKey()`-Plugin (noch ein Opt-in mehr).
3. **Ohne API-Key-Plugin: nur Human-Session-Auth.** Die Standard-Admin-
   Endpunkte prüfen einen eingeloggten Menschen with Admin-Rolle — no
   Maschinen-Credential von Haus from.

**Konsequenz:** Die Admin-Plugin-Route ist ein plausibler **v2-Baustein**
for Apps, die es explizit einrichten wollen — aber no Zero-Touch-Default
for "jede beliebige gehostete App."

## 4. Der empfohlene v1-Ansatz: passives JWT-Claim-Lesen am Gateway

Das ist der eigentliche Fund dieser Recherche (Prompt 8), and er dreht die
ursprüngliche Annahme um: **Better Auth unterstützt JWT-Sessions, and das
passive Auslesen von Rollen-Claims through einen vorgeschalteten
Reverse-Proxy — ganz without API-Aufruf or DB-Zugriff — ist explizit der
vorgesehene, dokumentierte Anwendungsfall des JWT-Plugins**, not ein
Hack.

Wie es funktioniert:

1. Der App-Betreiber aktiviert Better Auths `jwt()`-Plugin and definiert
   `definePayload({ user }) => ({ role: user.role })`, damit die Rolle
   tatsächlich als Claim im Token landet.
2. Better Auth stellt einen `/api/auth/jwks`-Endpunkt bereit.
3. **OpenMeshs Router-Node (der ohnehin als L7-Proxy before jedem Workspace
   sitzt, Sprint 36 WP2) holt/cached diesen JWKS and verifiziert das JWT
   lokal** — Signatur + `exp` prüfen, `role`-Claim extrahieren. Kein
   Netzwerk-Call zurück zu Better Auth or dessen DB pro Request.

Das ist strukturell fast identisch zu dem, was OpenMeshs eigener Keycloak-
JWT-Verifier bereits tut (`internal/auth/keycloak_oidc.go`) — nur for die
Rollen einer *fremden* App statt for OpenMeshs eigene Nutzer. Der Router
sitzt bereits an der richtigen Stelle im Traffic.

**Die zwei ehrlichen Grenzen, von Better Auth selbst dokumentiert:**

- **JWT ist no Ersatz for die primäre Session** — laut Doku "not meant
  as a replacement for the session... meant to be used for services that
  require JWT tokens." Das App-Frontend spricht weiterhin normal per
  Cookie with Better Auth; das JWT ist zusätzlich, for genau
  nachgelagerte Dienste wie OpenMeshs Router gedacht.
- **Stale-Role-Problem at Sperrung/Rollenänderung.** Da JWTs zustandslos
  sind, bleibt eine geänderte/entzogene Rolle im Proxy bis `exp` "stale".
  Mitigation: kurze TTL (Doku empfiehlt ~15 Min) for schnelle
  Propagation about Refresh: ODER (Better Auth ≥1.7, OAuth-2.1-Modul)
  Token-Introspection for Routen, wo Echtzeit-Sperrung kritisch ist (ein
  zusätzlicher, aber gezielter HTTP-Call nur dort, wo es zählt).

**v1-Scope-Empfehlung:** read-only, opt-in pro Workspace ("dieser
Workspace hat eine App with JWT-fähiger Auth — trage den JWKS-Endpunkt and
das Rollen-Claim-Feld ein"), zeigt Rolle/aktive-Session-Zahl im
OpenMesh-Dashboard, with explizit kurzer Cache-TTL. Keine Schreib-Aktionen
(Sperren/Rollen-Ändern) in v1 — das wäre der v2-Schritt about das
Admin-Plugin, nur for Apps, die es aktiv bereitstellen.

## 5. v2 (später, not jetzt): eine generische `UserManager`-Schnittstelle

Für den Fall, dass echte **Schreibaktionen** (User sperren, Rolle
zuweisen) about OpenMesh gewünscht sind — not nur Sichtbarkeit — schlägt
die Recherche (Prompt 7) ein Go-Interface before, das dem bereits im Repo
etablierten Muster folgt (`SecretsEngine`/`CloudProvider`: echte
Implementation wo möglich, ehrlicher 501-Stub sonst):

```go
package identity

type User struct {
    ID       string
    Email    string
    Name     string
    IsActive bool
    Metadata map[string]any // Bibliotheks-spezifische Zusatzdaten
}

type Role struct {
    ID          string
    Name        string
    Permissions []string
}

type UserManager interface {
    GetUser(ctx context.Context, id string) (*User, error)
    ListUsers(ctx context.Context, limit int, pageToken string) ([]User, string, error)
    SuspendUser(ctx context.Context, id string, reason string) error
    UnsuspendUser(ctx context.Context, id string) error

    ListRoles(ctx context.Context) ([]Role, error)
    AssignRole(ctx context.Context, userID, roleID string) error
    RemoveRole(ctx context.Context, userID, roleID string) error
    GetUserRoles(ctx context.Context, userID string) ([]Role, error)
}
```

Kein existierendes OSS-Projekt macht das schon for genau diese
Bibliotheks-Kombination — es müsste selbst entworfen werden. Wichtige
Design-Entscheidung: **"Rollen" not in ein starres Feld zwingen** — der
Kratos-Treiber würde intern gegen Ory Keto (Zanzibar-Style Graph-Relations)
sprechen, der Better-Auth-Treiber gegen ein flaches DB-Feld/die Admin-API,
ein Lucia/Auth.js-Treiber gegen eine vom Operator konfigurierte
`SQLConfig{UsersTable, RoleColumn, SuspendColumn}` (weil dort Spaltennamen
komplett app-spezifisch sind). Die Plattform-UI merkt vom Unterschied
nichts — nur die Interface-Implementation variiert.

Adapter-Aufwand pro Bibliothek (from Prompt 4+7, zur Priorisierung falls
v2 kommt):

| Library | Zugriffsweg | Aufwand |
|---|---|---|
| Better Auth | Admin-Plugin-API (opt-in) or JWT-Claims (v1) | niedrig |
| Auth.js/NextAuth | rohes SQL, sehr standardisiertes Schema, aber no native RBAC-Spalte | niedrig |
| Lucia | rohes SQL, aber Spaltennamen 100% frei wählbar through Entwickler | mittel (braucht Config-Mapping) |
| Supabase Auth (self-hosted) | `auth.users`/`auth.sessions`, standardisiert, aber JSONB-Metadaten for Custom-Rollen | mittel |
| Ory Kratos | NIE roh per SQL — eigene Admin-API zwingend (schema-agnostische JSON-Traits) | hoch (+ Ory Keto for Rollen) |
| Clerk | not selbst-hostbar, nur Cloud-API | niedrig (aber selten relevant for unseren Fall) |

## 6. Rechtliche Einordnung (DSGVO) — muss before jedem Produktivfeature geklärt sein

Die Recherche (Prompt 9) ist hier eindeutig and beruhigend, solange wir
uns an eine Grenze halten:

- OpenMesh bleibt **Auftragsverarbeiter (Processor/Sub-Processor)**, solange
  der Zugriff ausschließlich der vom Kunden beauftragten
  App-Verwaltung dient (dokumentierte Weisung). OpenMesh würde erst zum
  **gemeinsam Verantwortlichen (Joint Controller)**, wenn diese Daten for
  eigene Zwecke genutzt würden — z. B. plattformübergreifendes
  Benchmarking, eigene Nutzerprofile, or Modell-Training about
  mehrere Kunden-Apps hinweg. **Das darf nie passieren, without dass es
  explizit als neue Datenverarbeitung deklariert and vom Kunden
  zugestimmt wird.**
- Ein bestehendes Art.-28-DPA reicht not automatisch — es muss den
  "interaktiven API-/Dashboard-Zugriff on Identitätsdaten" explizit als
  Verarbeitungsgegenstand benennen (not nur "verschlüsselte Daten im
  Ruhezustand"), plus konkrete TOMs: Plattform-seitiges Audit-Logging
  (wer/welches Skript hat wann welche Kunden-Admin-API aufgerufen),
  nachweisbare Mandantentrennung, TLS-Pflicht, and eine Regelung, wie
  OpenMesh dem Kunden at DSAR/Löschungsanfragen seiner Endnutzer hilft.
- **Referenz-Vorlage:** Supabase's öffentliches Data Processing Addendum
  ist strukturell das nächstliegende Beispiel (gleiche Rolle: Anbieter
  with Dashboard-Zugriff on Kunden-Endnutzer-Auth-Daten) and sollte als
  Ausgangspunkt for eine OpenMesh-DPA-Ergänzung dienen, bevor dieses
  Feature real angeboten wird — auch im MVP/Pilot with dem Chef-Server.

## 7. Empfehlung / nächste Schritte

1. **v1 bauen:** pro Workspace optional konfigurierbar — JWKS-Endpunkt +
   Rollen-Claim-Feldname der gehosteten App; OpenMeshs Router liest das
   Rollen-Claim passiv from dem bereits durchlaufenden Traffic (no
   neuer API-Call); Anzeige im Workspace-/App-Dashboard (Nutzeranzahl je
   Rolle, aktive Sessions je Rolle geschätzt from Claims). Read-only.
2. **v1 explizit NICHT bauen:** DB-Direktzugriff on App-Auth-Tabellen,
   Schreibaktionen (Sperren/Rolle ändern) about OpenMesh.
3. **Vor dem ersten echten Kunden-Einsatz (auch dem Chef-Server-Fall):**
   DPA-Ergänzung entwerfen (Supabase-DPA als Vorlage), auch wenn es nur
   ein interner/Pilot-Fall ist — Gewohnheit before Wachstum ist billiger als
   Nachrüsten.
4. **v2 (später, eigener Sprint):** `UserManager`-Interface nur bauen,
   wenn ein echter Bedarf for Schreibaktionen entsteht — not
   vorbauen. Reihenfolge after Aufwandstabelle: Better Auth
   (Admin-Plugin, opt-in) → Auth.js/NextAuth (SQL) → Lucia (SQL +
   Config-Mapping) → Supabase (SQL + JSONB) → Kratos+Keto (zwei
   Admin-APIs).

## Quellen (Gemini-Recherche, 14.9.2026, roh in `R42_multi.md`/`R42_multi2.md`)

- Better Auth: [Database schema](https://better-auth.com/docs/concepts/database) · [Admin plugin](https://better-auth.com/docs/plugins/admin) · [JWT plugin](https://better-auth.com/docs/plugins/jwt) · [Session management](https://better-auth.com/docs/concepts/session-management) · [Changelog](https://better-auth.com/changelog)
- Ory Kratos: https://github.com/ory/kratos (Admin/Public API split, Ory Keto for authorization)
- Supabase Auth schema (`auth.users`/`auth.sessions`) and public DPA: https://supabase.com/docs/guides/auth/managing-user-data
- GDPR controller/processor distinction (EDPB-aligned framing): https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html
- Supabase 2022/23 `SECURITY DEFINER` trigger privilege-escalation pattern (cited as the cautionary precedent against encouraging direct auth-table interaction)
