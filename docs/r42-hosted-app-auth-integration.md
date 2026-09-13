---
id: "R42"
title: "R42 — Superadmin Visibility into a Hosted App's Own Auth/RBAC: Design Synthesis"
type: research
date: 2026-09-13
status: final
tags: [mesh, rbac, ufw, keycloak, ssh]
license: CC-BY-4.0
---

# R42 — Superadmin Visibility into a Hosted App's Own Auth/RBAC: Design Synthesis

**Quelle:** Operator-Frage 14.9.2026 ("wir wollen als superadmin auch direkt
die auths und datenbanken und rbac der apps verwalten... das selbe rbac und
die rollen in den apps sollte man dann auch direkt über jimesh benutzen
können"). Konkreter Anlass: der Chef des Operators hat Better Auth in seinen
eigenen Server integriert; der Operator wird diesen Server als JiMesh-
Deployment absichern. Research über 9 Gemini-Prompts (`R42_multi.md`,
`R42_multi2.md`) — dieses Dokument synthetisiert die Rohantworten zu einer
Entscheidung.

**Status:** Design-Vorschlag, nicht gebaut. Keine Code-Änderung in diesem
Dokument.

---

## 1. Das Problem, präzise gefasst

JiMesh hostet fremde Apps (SSH Remote Target → Workspace → App). Jede App
hat typischerweise ihr eigenes End-User-Auth-System (Better Auth, Lucia,
Auth.js, Ory Kratos, Supabase Auth, Clerk — je nachdem, was der App-
Entwickler gewählt hat). Der Operator will als Superadmin in JiMesh sehen
(und teilweise verwalten) können, wer in der gehosteten App Nutzer/Rolle X
ist — ohne für jede App-Auth-Bibliothek eine eigene, tief gekoppelte
Integration zu bauen, und ohne die Sicherheits-/Rechtsrisiken einer
naiven "wir lesen einfach die DB" Lösung einzugehen.

## 2. Die zuerst naheliegende Idee war falsch — warum

Der ursprüngliche Gedanke (weil JiMesh's Router-Node ohnehin als DB-Proxy
vor jeder App-Datenbank sitzt — Sprint 36 WP2): einfach die Auth-Tabellen
der App direkt über den Router lesen. Die Recherche (Prompt 1+2)
widerlegt das als **Default-Ansatz**, aus drei konkreten, technischen
Gründen — nicht nur "das ist unüblich", sondern **so bricht es real**:

- **Cache-/Session-Desync (kritisch):** Better Auth (und die meisten
  modernen Auth-Libs) cachen Session-Status in Redis (`secondaryStorage`)
  oder verschlüsselt im Browser-Cookie (`cookieCache`). Ein direkter
  DB-Write (z. B. `banned = true` setzen) erreicht diese Caches nicht —
  der Nutzer bleibt bis zum TTL-Ablauf eingeloggt, obwohl JiMesh ihn
  gesperrt zu haben glaubt. Ein `docker stop` auf Container-Ebene würde
  das umgehen, aber genau das will der Operator hier nicht (er will
  granulare App-User-Verwaltung, nicht nur Container-Freeze).
- **Schema-Drift:** Auch bei Libraries mit einem "stabilen Kern-Schema"
  (Better Auth's `user`/`session`/`account`/`verification` sind laut
  eigener Doku ein versionierter, öffentlicher Vertrag) brechen
  Custom-Felder (`additionalFields`), Plugins (Multi-Tenant-Orgs,
  Admin-Plugin fügt eigene Spalten hinzu) und abweichende
  Tabellennamen/Typen je nach ORM-Adapter (Drizzle/Prisma/Kysely/raw SQL)
  einen starren Lesezugriff.
- **Krypto-/Event-Bypass:** Ein direkter `INSERT` in die `user`-Tabelle
  umgeht Passwort-Hashing (Argon2id/bcrypt-Ableitung passiert im
  App-Code, nicht in der DB), Lifecycle-Hooks und Audit-Logs/Webhooks der
  App. Für **reines Lesen** ist dieses Risiko gering; für **Schreiben**
  (Rolle ändern, Sperren) ist es real und laut Recherche "dringend
  abzuraten".

Zusätzlich: das Präzedenzfall-Bild ist eindeutig. Reine PaaS-Hoster
(Vercel, Render, Railway, Fly.io) tun das **nie** — sie behandeln
Kunden-DB-Inhalt strikt als Blackbox. Nur echte BaaS-Anbieter (Supabase,
Firebase) lesen Auth-Tabellen direkt — aber nur, weil sie selbst die
Auth-Bibliothek geschrieben/kontrolliert haben (Supabase hat GoTrue
selbst gebaut). JiMesh ist in der Rolle "hostet fremden, nicht
selbstgeschriebenen Auth-Code" — das ist strukturell näher an
Vercel/Railway als an Supabase. Ein real dokumentierter Vorfall stützt
das: die Supabase `SECURITY DEFINER`-Trigger-Privilegien-Eskalation
(2022/23) entstand exakt aus der Kultur, Entwickler zu ermutigen, direkt
mit Auth-Tabellen zu interagieren.

**Konsequenz:** Roher DB-Zugriff auf App-Auth-Tabellen ist kein
Default-Pfad für dieses Feature. Punkt.

## 3. Die Admin-API-Alternative — auch nicht der richtige Default

Better Auth hat ein offizielles Admin-Plugin (`/admin/get-user`,
`/admin/ban-user`, `/admin/list-user-sessions`, mit eigenem RBAC über
`adminRoles`/Custom-Permissions). Das klingt zunächst wie die saubere
Lösung — hat aber drei Eigenschaften, die es für JiMeshs Fall (ein
**externer** Dienst, der **viele fremde** Apps verwalten will)
unpraktisch machen:

1. **Strikt Opt-in mit DB-Migration.** Der App-Betreiber muss das Plugin
   im Code registrieren UND `npx better-auth migrate` laufen lassen
   (neue Spalten: `role`, `banned`, `banReason`, `banExpires`,
   `impersonatedBy`). Eine bereits laufende App (wie die des Chefs) kann
   das nicht rückwirkend "einfach so" freischalten — es erfordert
   bewusste Code-Änderung durch den App-Eigentümer.
2. **Server-zu-Server-Aufruf ist als Same-Process-Import gedacht, nicht
   als HTTP-Call.** Die Doku zeigt `auth.api.banUser(...)` als direkten
   In-Process-Funktionsaufruf innerhalb derselben Node-Anwendung — nicht
   als HTTP-Request von einem externen Go-Service. Für echte
   HTTP-Server-zu-Server-Aufrufe bräuchte man zusätzlich das separate
   `apiKey()`-Plugin (noch ein Opt-in mehr).
3. **Ohne API-Key-Plugin: nur Human-Session-Auth.** Die Standard-Admin-
   Endpunkte prüfen einen eingeloggten Menschen mit Admin-Rolle — kein
   Maschinen-Credential von Haus aus.

**Konsequenz:** Die Admin-Plugin-Route ist ein plausibler **v2-Baustein**
für Apps, die es explizit einrichten wollen — aber kein Zero-Touch-Default
für "jede beliebige gehostete App."

## 4. Der empfohlene v1-Ansatz: passives JWT-Claim-Lesen am Gateway

Das ist der eigentliche Fund dieser Recherche (Prompt 8), und er dreht die
ursprüngliche Annahme um: **Better Auth unterstützt JWT-Sessions, und das
passive Auslesen von Rollen-Claims durch einen vorgeschalteten
Reverse-Proxy — ganz ohne API-Aufruf oder DB-Zugriff — ist explizit der
vorgesehene, dokumentierte Anwendungsfall des JWT-Plugins**, nicht ein
Hack.

Wie es funktioniert:

1. Der App-Betreiber aktiviert Better Auths `jwt()`-Plugin und definiert
   `definePayload({ user }) => ({ role: user.role })`, damit die Rolle
   tatsächlich als Claim im Token landet.
2. Better Auth stellt einen `/api/auth/jwks`-Endpunkt bereit.
3. **JiMeshs Router-Node (der ohnehin als L7-Proxy vor jedem Workspace
   sitzt, Sprint 36 WP2) holt/cached diesen JWKS und verifiziert das JWT
   lokal** — Signatur + `exp` prüfen, `role`-Claim extrahieren. Kein
   Netzwerk-Call zurück zu Better Auth oder dessen DB pro Request.

Das ist strukturell fast identisch zu dem, was JiMeshs eigener Keycloak-
JWT-Verifier bereits tut (`internal/auth/keycloak_oidc.go`) — nur für die
Rollen einer *fremden* App statt für JiMeshs eigene Nutzer. Der Router
sitzt bereits an der richtigen Stelle im Traffic.

**Die zwei ehrlichen Grenzen, von Better Auth selbst dokumentiert:**

- **JWT ist kein Ersatz für die primäre Session** — laut Doku "not meant
  as a replacement for the session... meant to be used for services that
  require JWT tokens." Das App-Frontend spricht weiterhin normal per
  Cookie mit Better Auth; das JWT ist zusätzlich, für genau
  nachgelagerte Dienste wie JiMeshs Router gedacht.
- **Stale-Role-Problem bei Sperrung/Rollenänderung.** Da JWTs zustandslos
  sind, bleibt eine geänderte/entzogene Rolle im Proxy bis `exp` "stale".
  Mitigation: kurze TTL (Doku empfiehlt ~15 Min) für schnelle
  Propagation über Refresh: ODER (Better Auth ≥1.7, OAuth-2.1-Modul)
  Token-Introspection für Routen, wo Echtzeit-Sperrung kritisch ist (ein
  zusätzlicher, aber gezielter HTTP-Call nur dort, wo es zählt).

**v1-Scope-Empfehlung:** read-only, opt-in pro Workspace ("dieser
Workspace hat eine App mit JWT-fähiger Auth — trage den JWKS-Endpunkt und
das Rollen-Claim-Feld ein"), zeigt Rolle/aktive-Session-Zahl im
JiMesh-Dashboard, mit explizit kurzer Cache-TTL. Keine Schreib-Aktionen
(Sperren/Rollen-Ändern) in v1 — das wäre der v2-Schritt über das
Admin-Plugin, nur für Apps, die es aktiv bereitstellen.

## 5. v2 (später, nicht jetzt): eine generische `UserManager`-Schnittstelle

Für den Fall, dass echte **Schreibaktionen** (User sperren, Rolle
zuweisen) über JiMesh gewünscht sind — nicht nur Sichtbarkeit — schlägt
die Recherche (Prompt 7) ein Go-Interface vor, das dem bereits im Repo
etablierten Muster folgt (`SecretsEngine`/`CloudProvider`: echte
Implementierung wo möglich, ehrlicher 501-Stub sonst):

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

Kein existierendes OSS-Projekt macht das schon für genau diese
Bibliotheks-Kombination — es müsste selbst entworfen werden. Wichtige
Design-Entscheidung: **"Rollen" nicht in ein starres Feld zwingen** — der
Kratos-Treiber würde intern gegen Ory Keto (Zanzibar-Style Graph-Relations)
sprechen, der Better-Auth-Treiber gegen ein flaches DB-Feld/die Admin-API,
ein Lucia/Auth.js-Treiber gegen eine vom Operator konfigurierte
`SQLConfig{UsersTable, RoleColumn, SuspendColumn}` (weil dort Spaltennamen
komplett app-spezifisch sind). Die Plattform-UI merkt vom Unterschied
nichts — nur die Interface-Implementierung variiert.

Adapter-Aufwand pro Bibliothek (aus Prompt 4+7, zur Priorisierung falls
v2 kommt):

| Library | Zugriffsweg | Aufwand |
|---|---|---|
| Better Auth | Admin-Plugin-API (opt-in) oder JWT-Claims (v1) | niedrig |
| Auth.js/NextAuth | rohes SQL, sehr standardisiertes Schema, aber keine native RBAC-Spalte | niedrig |
| Lucia | rohes SQL, aber Spaltennamen 100% frei wählbar durch Entwickler | mittel (braucht Config-Mapping) |
| Supabase Auth (self-hosted) | `auth.users`/`auth.sessions`, standardisiert, aber JSONB-Metadaten für Custom-Rollen | mittel |
| Ory Kratos | NIE roh per SQL — eigene Admin-API zwingend (schema-agnostische JSON-Traits) | hoch (+ Ory Keto für Rollen) |
| Clerk | nicht selbst-hostbar, nur Cloud-API | niedrig (aber selten relevant für unseren Fall) |

## 6. Rechtliche Einordnung (DSGVO) — muss vor jedem Produktivfeature geklärt sein

Die Recherche (Prompt 9) ist hier eindeutig und beruhigend, solange wir
uns an eine Grenze halten:

- JiMesh bleibt **Auftragsverarbeiter (Processor/Sub-Processor)**, solange
  der Zugriff ausschließlich der vom Kunden beauftragten
  App-Verwaltung dient (dokumentierte Weisung). JiMesh würde erst zum
  **gemeinsam Verantwortlichen (Joint Controller)**, wenn diese Daten für
  eigene Zwecke genutzt würden — z. B. plattformübergreifendes
  Benchmarking, eigene Nutzerprofile, oder Modell-Training über
  mehrere Kunden-Apps hinweg. **Das darf nie passieren, ohne dass es
  explizit als neue Datenverarbeitung deklariert und vom Kunden
  zugestimmt wird.**
- Ein bestehendes Art.-28-DPA reicht nicht automatisch — es muss den
  "interaktiven API-/Dashboard-Zugriff auf Identitätsdaten" explizit als
  Verarbeitungsgegenstand benennen (nicht nur "verschlüsselte Daten im
  Ruhezustand"), plus konkrete TOMs: Plattform-seitiges Audit-Logging
  (wer/welches Skript hat wann welche Kunden-Admin-API aufgerufen),
  nachweisbare Mandantentrennung, TLS-Pflicht, und eine Regelung, wie
  JiMesh dem Kunden bei DSAR/Löschungsanfragen seiner Endnutzer hilft.
- **Referenz-Vorlage:** Supabase's öffentliches Data Processing Addendum
  ist strukturell das nächstliegende Beispiel (gleiche Rolle: Anbieter
  mit Dashboard-Zugriff auf Kunden-Endnutzer-Auth-Daten) und sollte als
  Ausgangspunkt für eine JiMesh-DPA-Ergänzung dienen, bevor dieses
  Feature real angeboten wird — auch im MVP/Pilot mit dem Chef-Server.

## 7. Empfehlung / nächste Schritte

1. **v1 bauen:** pro Workspace optional konfigurierbar — JWKS-Endpunkt +
   Rollen-Claim-Feldname der gehosteten App; JiMeshs Router liest das
   Rollen-Claim passiv aus dem bereits durchlaufenden Traffic (kein
   neuer API-Call); Anzeige im Workspace-/App-Dashboard (Nutzeranzahl je
   Rolle, aktive Sessions je Rolle geschätzt aus Claims). Read-only.
2. **v1 explizit NICHT bauen:** DB-Direktzugriff auf App-Auth-Tabellen,
   Schreibaktionen (Sperren/Rolle ändern) über JiMesh.
3. **Vor dem ersten echten Kunden-Einsatz (auch dem Chef-Server-Fall):**
   DPA-Ergänzung entwerfen (Supabase-DPA als Vorlage), auch wenn es nur
   ein interner/Pilot-Fall ist — Gewohnheit vor Wachstum ist billiger als
   Nachrüsten.
4. **v2 (später, eigener Sprint):** `UserManager`-Interface nur bauen,
   wenn ein echter Bedarf für Schreibaktionen entsteht — nicht
   vorbauen. Reihenfolge nach Aufwandstabelle: Better Auth
   (Admin-Plugin, opt-in) → Auth.js/NextAuth (SQL) → Lucia (SQL +
   Config-Mapping) → Supabase (SQL + JSONB) → Kratos+Keto (zwei
   Admin-APIs).

## Quellen (Gemini-Recherche, 14.9.2026, roh in `R42_multi.md`/`R42_multi2.md`)

- Better Auth: [Database schema](https://better-auth.com/docs/concepts/database) · [Admin plugin](https://better-auth.com/docs/plugins/admin) · [JWT plugin](https://better-auth.com/docs/plugins/jwt) · [Session management](https://better-auth.com/docs/concepts/session-management) · [Changelog](https://better-auth.com/changelog)
- Ory Kratos: https://github.com/ory/kratos (Admin/Public API split, Ory Keto for authorization)
- Supabase Auth schema (`auth.users`/`auth.sessions`) and public DPA: https://supabase.com/docs/guides/auth/managing-user-data
- GDPR controller/processor distinction (EDPB-aligned framing): https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html
- Supabase 2022/23 `SECURITY DEFINER` trigger privilege-escalation pattern (cited as the cautionary precedent against encouraging direct auth-table interaction)
