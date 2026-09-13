---
okf_version: "1.0"
id: "okf-str-pos-r42-multi2"
title: "R42 Multi2"
topic: "strategy-audits-and-decisions"
subtopic: "positioning-and-plans"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - positioning-and-plans
summary: "Hier ist die detaillierte Aufschlüsselung, wie das offizielle Admin-Plugin von Better Auth funktioniert, wie Authentifizierung, Scoping und Integratio"
---

# R42 Multi2

## Overview

Hier ist die detaillierte Aufschlüsselung, wie das offizielle Admin-Plugin von Better Auth funktioniert, wie Authentifizierung, Scoping and Integration geregelt sind and ob du es nachträglich sicher aktivieren kannst: [1] (https://better-auth.com/docs/plugins/admin)1. Authentifizierung: Wie weisen sich Aufrufer from?Das offizielle admin()-Plugin von Better Auth setzt eine authentifizierte Admin-Sitzung (Session/Cookie) eines angemeldeten Menschen voraus. [1] (https://github.com/better-auth/better-auth/issues/4257)Keine statischen API-Keys / Service-Token standardmäßig: Die Endpunkte, die through das Admin-Plugin freigeschaltet werden (z. B. User bannen, Rollen ändern or Impersonation), nutzen intern Middlewares, die prüfen, ob der anfragende Nutzer eingeloggt ist, eine valide Session besitzt and ob seine Rolle als admin deklariert ist or seine User-ID im Array der adminUserIds hinterlegt ist. [1] (https://better-auth-ui.com/docs/shadcn/plugins/admin)Server-zu-Server-Aufrufe: Wenn du von einem trusted Backend (einem anderen Server) programmgesteuert administrative Aktionen ausführen willst, machst du das not about HTTP-Requests gegen das Admin-Plugin. Stattdessen importierst du deine Server-Instanz (auth) direkt in deinem Code and nutzt das interne auth.api-Objekt:ts// Dies umgeht HTTP/Cookies vollständig, da es direkt serverseitig ausgeführt wird
await auth.api.banUser({
  body: { userId: "user_id_here", reason: "Verstoß" }
});

---

Hier ist die detaillierte Aufschlüsselung, wie das offizielle Admin-Plugin von Better Auth funktioniert, wie Authentifizierung, Scoping and Integration geregelt sind and ob du es nachträglich sicher aktivieren kannst: [1] (https://better-auth.com/docs/plugins/admin)1. Authentifizierung: Wie weisen sich Aufrufer from?Das offizielle admin()-Plugin von Better Auth setzt eine authentifizierte Admin-Sitzung (Session/Cookie) eines angemeldeten Menschen voraus. [1] (https://github.com/better-auth/better-auth/issues/4257)Keine statischen API-Keys / Service-Token standardmäßig: Die Endpunkte, die through das Admin-Plugin freigeschaltet werden (z. B. User bannen, Rollen ändern or Impersonation), nutzen intern Middlewares, die prüfen, ob der anfragende Nutzer eingeloggt ist, eine valide Session besitzt and ob seine Rolle als admin deklariert ist or seine User-ID im Array der adminUserIds hinterlegt ist. [1] (https://better-auth-ui.com/docs/shadcn/plugins/admin)Server-zu-Server-Aufrufe: Wenn du von einem trusted Backend (einem anderen Server) programmgesteuert administrative Aktionen ausführen willst, machst du das not about HTTP-Requests gegen das Admin-Plugin. Stattdessen importierst du deine Server-Instanz (auth) direkt in deinem Code and nutzt das interne auth.api-Objekt:ts// Dies umgeht HTTP/Cookies vollständig, da es direkt serverseitig ausgeführt wird
await auth.api.banUser({
  body: { userId: "user_id_here", reason: "Verstoß" }
});

---

I want to design one Go interface (e.g. ListUsers, GetUser, ListRoles, SuspendUser) that a hosting platform can implement once and back with different auth libraries: Better Auth's Admin Plugin API, Ory Kratos's Admin API (+ Ory Keto for roles), and a raw-SQL fallback for libraries with no admin API (Lucia, Auth.js/NextAuth). What's the practical minimal common shape across these three that doesn't force the lowest common denominator (e.g. how do you represent "roles" when Kratos delegates that entirely to a separate service, Better Auth has them inline, and Lucia has an arbitrary developer-defined column)? Are there existing open-source projects that already attempt this kind of "auth library abstraction layer" I could look at instead of designing from scratch?

Das Entwerfen einer Abstraktionsschicht for die Identitätsverwaltung about derart radikal unterschiedliche Architekturmuster hinweg ist eine exzellente Herausforderung.Es gibt derzeit no etabliertes Open-Source-Projekt, das genau diese Bibliotheken (Better Auth, Kratos, Lucia/Auth.js) in Go unter ein einziges Interface zwingt. Frameworks wie Auth0 bieten zwar einheitliche APIs, binden dich jedoch an deren Ökosystem. Wenn du eine Hosting-Plattform baust, die diese Backends austauschbar unterstützen soll, musst du das Interface selbst entwerfen.Um not on den kleinsten gemeinsamen Nenner (Lowest Common Denominator) herabzufallen, muss das Interface zustandslos, flexibel typisiert and erweiterbar sein. Hier ist das praxisnahe Design for dein Go-Interface.Das Problem with "Roles" & "Suspensions" (Die Diskrepanz)Better Auth (Inline): Rollen and Bans sind direkte Spalten in der Tabelle user (role: string, banned: boolean). Ein API-Aufruf reicht from. [1] (https://better-auth.com/docs/plugins/admin)Ory Kratos (Getrennt): Kratos kennt standardmäßig no Rollen. Kratos verwaltet die Identität, während Rollen about Ory Keto (ein separates, Graph-basiertes Zanzibar-System via Relations) abgebildet werden. Eine Sperrung (Suspend) erfolgt about ein state: active/inactive Flag in der Kratos-Admin-API. [1] (https://github.com/ory/kratos)Lucia / Auth.js (Raw SQL): Der Entwickler hat die Tabellenstruktur selbst entworfen. Rollen können Enums, Strings, eine Join-Table (user_roles) or Bitmasks sein.Das Go Interface DesignUm dieses Problem zu lösen, brechen wir starre Strukturen on and nutzen Go-Generics or lose Typisierungen (any / map[string]any) for Metadaten, während wir die Kernaktionen deterministisch halten.gopackage identity

import "context"

// User repräsentiert die normalisierte Kern-Identität.
type User struct {
	ID       string                 `json:"id"`
	Email    string                 `json:"email"`
	Name     string                 `json:"name"`
	IsActive bool                   `json:"is_active"`
	Metadata map[string]any         `json:"metadata,omitempty"` // Für Bibliotheks-spezifische Zusatzdaten
}

// Role repräsentiert eine normalisierte Rolle.
type Role struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Permissions []string `json:"permissions,omitempty"`
}

// UserManager definiert die minimale, aber mächtige Abstraktionsschicht.
type UserManager interface {
	// User Management
	GetUser(ctx context.Context, id string) (*User, error)
	ListUsers(ctx context.Context, limit int, pageToken string) ([]User, string, error)
	SuspendUser(ctx context.Context, id string, reason string) error
	UnsuspendUser(ctx context.Context, id string) error

	// Role Management (Die Abstraktionsbrücke)
	ListRoles(ctx context.Context) ([]Role, error)
	AssignRole(ctx context.Context, userID string, roleID string) error
	RemoveRole(ctx context.Context, userID string, roleID string) error
	GetUserRoles(ctx context.Context, userID string) ([]Role, error)
}
	UsersTable     string // z.B. "users" or "le_user"
	RoleColumn     string // z.B. "role" or "access_level"
	SuspendColumn  string // z.B. "is_banned" or "disabled_at"
	// Falls Rollen in einer n:m Tabelle liegen:
	UserRolesTable string // optional: "user_to_roles"
}

---

Does Better Auth support issuing JWTs for its sessions (as opposed to only opaque cookie-based sessions validated against its own DB/cache)? If a reverse proxy or gateway sits in front of a Better Auth app and already terminates/inspects HTTP traffic for unrelated reasons, could it passively read a user's role out of a Better Auth-issued JWT's claims (assuming JWT mode is enabled and the proxy has or can be given the signing key/JWKS), without calling any Better Auth API or touching its database at all? Is this a supported/intended use of Better Auth's JWT plugin, or does the library documentation warn against relying on JWT claims as a role source of truth (e.g., because roles could change and a not-yet-expired JWT would be stale)?

Ja, Better Auth unterstützt das Ausstellen von JWTs for seine Sitzungen about ein dediziertes Plugin, and der von dir beschriebene Anwendungsfall (Rollenprüfung direkt im Reverse Proxy via JWT-Claims without API- or Datenbank-Hits) ist vollständig unterstützt and einer der primären Einsatzzwecke dieses Plugins. [1] (https://github.com/better-auth/better-auth/blob/main/docs/content/docs/plugins/jwt.mdx), [2] (https://better-auth.com/docs/plugins/jwt)Hier ist die detaillierte technische Funktionsweise, die Konfiguration for Gateways and die offizielle Haltung der Dokumentation zu den von dir angesprochenen Risiken:1. Wie Better Auth JWTs for Sessions handhabtStandardmäßig nutzt Better Auth ein opakes, datenbankgestütztes Cookie-System. Wenn du jedoch das JWT-Plugin (jwt()) aktivierst, stehen dir zwei Wege offen: [1] (https://lobehub.com/skills/okashanadeem-giaic-hackathon-ii-nextjs-better-auth-jwt-usage), [2] (https://github.com/better-auth/better-auth/blob/main/docs/content/docs/plugins/jwt.mdx)Der /token-Endpunkt (Für externe Services / APIs): Generiert ein echtes, asymmetrisch signiertes JWT, das about einen /jwks-Endpunkt von jedem API-Gateway or Proxy verifiziert werden kann. [1] (https://better-auth.com/docs/plugins/jwt)Der Cookie-Cache-Modus (sessionCookieCache): Wenn du in den Better Auth-Options session.cookieCache.strategy = "jwt" or "jwe" nutzt, legt Better Auth die Session-Daten zustandslos verschlüsselt in das Cookie better-auth.session_data. Wenn du im JWT-Plugin zusätzlich sessionCookieCache: true setzt, nutzt dieser Cache dieselben Schlüssel wie dein JWKS-Endpunkt. [1] (https://better-auth.com/docs/concepts/session-management), [2] (https://better-auth.com/docs/plugins/jwt), [3] (https://github.com/better-auth/better-auth/blob/main/docs/content/docs/plugins/jwt.mdx)2. Passives Auslesen der Rollen im Reverse Proxy (Gateway)Ein API-Gateway (wie Envoy, Traefik, Kong, Nginx Plus or AWS API Gateway) kann passiv die Rolle auslesen, sofern:Das Gateway so konfiguriert ist, dass es die JWKS von Better Auth (/api/auth/jwks) abruft and im Cache hält.Du das Standard-JWT-Payload-Verhalten so anpasst, dass die role auch wirklich als Claim im Token landet. Das geschieht in der Server-Konfiguration about die definePayload-Funktion des JWT-Plugins: [1] (https://lobehub.com/skills/bilalmk-todo_correct-betterauth-fastapi-jwt-bridge), [2] (https://better-auth.com/docs/plugins/jwt), [3] (https://github.com/better-auth/better-auth/discussions/7826)tsimport { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
    plugins: [
        jwt({
            // Fügt die Rolle explizit zu den JWT-Claims hinzu
            definePayload: async ({ user }) => {
                return {
                    role: user.role, // Better Auth Admin/Role-Spalte
                };
            }
        })
    ]
});

---
▎ Under GDPR, if a B2B hosting platform's own admin dashboard displays or manages another company's end-users' personal data (emails, ban status, session activity) — obtained via that hosted application's own auth library's official admin API, not raw database access — does the hosting platform likely become a joint controller, or does it remain a data processor/sub-processor of the hosted company? What contractual terms (DPA — Data Processing Agreement) are typically required for this specific scenario (a PaaS/hosting platform with programmatic admin access into a customer's own end-user auth system)? Are there existing DPA templates or legal guidance specifically covering "platform has admin API access to customer's own end-user data," as opposed to the more common "platform only stores encrypted customer application data at rest"?

Hier ist die datenschutzrechtliche Einordnung (DSGVO) for dieses spezifische PaaS/Hosting-Szenario, aufgeteilt in die rechtliche Rolle, vertragliche Requirements and die Praxis der Datenverarbeitungsverträge (DPA).1. Rechtliche Rolle: Joint Controller or (Sub-)Processor?Die Hosting-Plattform bleibt in diesem Szenario ein Data Processor (Auftragsverarbeiter) bzw. Sub-Processor (Unterauftragsverarbeiter). Sie wird not zum Joint Controller (gemeinsam Verantwortlichen). [1] (https://www.back4app.com/product/parse-gdpr), [2] (https://www.wsiworld.com/blog/responsibilities-of-a-controller-processor-and-data-protection-officer-according-to-gdpr), [3] (https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html)Der entscheidende Faktor (Zweck and Mittel): Nach den Leitlinien des Europäischen Datenschutzausschusses (EDSA/EDPB) wird man nur dann zum (Joint) Controller, wenn man about die Zwecke („Warum wird verarbeitet?“) and die wesentlichen Mittel („Welche Daten werden von wem erhoben?“) der Verarbeitung entscheidet. [1] (https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html)Warum Sie Processor bleiben: Dass Ihre Plattform about ein Admin-Dashboard personenbezogene Endnutzerdaten (E-Mails, Sperrstatus, Sitzungen) anzeigt and manipuliert, dient ausschließlich dem Zweck, Ihrem B2B-Kunden die Verwaltung seines Dienstes zu ermöglichen. Sie tun dies on dokumentierte Weisung des Kunden. [1] (https://usercentrics.com/knowledge-hub/gdpr-controller-vs-processor/), [2] (https://sprinto.com/gdpr/data-processor/), [3] (https://www.manageengine.com/compliance-manager/gdpr-compliance/gdpr-chapter-4.html), [4] (https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html)Wann die Grenze überschritten wird: Sie würden erst dann zum Controller werden, wenn Sie diese about die API erlangten Daten for eigene Zwecke nutzen würden (z. B. for plattformübergreifendes Benchmarking, eigene Nutzerprofile or KI-Modelltraining). Da dies not der Fall ist, bleibt die Rollenverteilung strikt: Ihr B2B-Kunde ist Controller, Sie sind Processor. [1] (https://www.flosum.com/blog/gdpr-compliance-for-saas-platform-owners), [2] (https://www.legiscope.com/blog/gdpr-data-controller-vs-processor.html), [3] (https://payproglobal.com/answers/what-is-dpa-agreement-in-saas/)2. Typische vertragliche Klauseln (DPA) for dieses SzenarioDa Ihre Plattform about die administrative API aktiven Lese- and Schreibzugriff on die Endnutzerdaten hat, reicht ein Standard-DPA for „verschlüsselte Daten im Ruhezustand (Data at Rest)“ not from. Folgende spezifische Regelungen müssen im DPA (after Art. 28 DSGVO) verankert werden: [1] (https://www.atlassian.com/blog/development/data-processing-agreements-dpas-developer-info), [2] (https://payproglobal.com/answers/what-is-dpa-agreement-in-saas/)Erweiterter Gegenstand and Art der Verarbeitung (Anlage 1): Es muss explizit festgehalten werden, dass die Verarbeitung not nur das Speichern/Hosting umfasst, sondern das „Auslesen, Modifizieren, Sperren and Verwalten von Identitäts- and Sitzungsdaten about programmgesteuerte Schnittstellen (APIs) zu administrativen Zwecken“. [1] (https://www.back4app.com/product/parse-gdpr), [2] (https://www.atlassian.com/blog/development/data-processing-agreements-dpas-developer-info)Spezifische technische and organisatorische Maßnahmen (TOMs / Anlage 2): Da Ihre Plattform Code ausführt, der die Daten im Klartext verarbeitet, fordern Kunden hier präzise Sicherheitsnachweise:Audit-Logging on Plattformebene: Protokollierung, welcher Mitarbeiter Ihrer Plattform (or welches automatisierte Skript) wann die Admin-API eines Kunden aufgerufen hat.Mandantentrennung (Multi-Tenancy Isolation): Nachweis, dass die Admin-API von Mandant A unter keinen Umständen Daten von Mandant B abrufen kann.Verschlüsselung "In Transit": Zwingender Einsatz von TLS for alle API-Aufrufe. [1] (https://payproglobal.com/answers/what-is-dpa-agreement-in-saas/), [2] (https://www.atlassian.com/blog/development/data-processing-agreements-dpas-developer-info)Unterstützung at Betroffenenrechten (DSAR): Wenn ein Endnutzer des Kunden von seinem „Recht on Vergessenwerden“ (Löschung) Gebrauch macht, muss im DPA geregelt sein, wie Ihre Plattform dem Kunden hilft, diese Daten auch about das Admin-Dashboard/die API konsistent zu löschen. [1] (https://sisl.pl/en/blog/dpa-agreements-small-saas), [2] (https://payproglobal.com/answers/what-is-dpa-agreement-in-saas/)3. Existierende DPA-Templates and rechtliche LeitfädenEs gibt no offiziellen Standard-Vorlagen, die exakt den Titel „Plattform with Admin-API-Zugriff“ tragen. Stattdessen orientiert sich der Markt an etablierten PaaS- and Backend-as-a-Service (BaaS)-DPAs, da diese genau denselben tiefen Zugriff on die Auth-Systeme der Kunden haben.Folgende Referenzen and Musterstrukturen spiegeln dieses Szenario wider:Das Supabase- / Firebase-Modell: Anbieter wie Supabase or Google Firebase hosten die Auth-Bibliotheken (Go/Node) for ihre Kunden and bieten Web-Dashboards zur Nutzerverwaltung (E-Mails, Bans, Sessions). Deren öffentlich einsehbare DPAs (z. B. der Supabase Data Processing Addendum) dienen als perfekte Vorlage for Ihre Hosting-Plattform. Sie listen die Auth-Daten explizit als „Customer Data“ on, die im Auftrag verarbeitet wird. [1] (https://eurobase.app/blog/supabase-gdpr-dpa-eu-region), [2] (https://brightinteraction.com/insights/gdpr-for-saas-companies/), [3] (https://runsite.app/blog/what-is-a-data-processing-agreement-dpa)Standardvertragsklauseln (SCCs) der EU (Modul 2: Controller-to-Processor): Wenn Ihr Hosting-Unternehmen or die Server außerhalb der EU liegen (or der Kunde außerhalb sitzt), nutzen Unternehmen die Standardvertragsklauseln der EU. Modul 2 ist genau for den Fall ausgelegt, dass der Processor via Software/Plattform tiefen, operativen Zugriff on die Daten des Controllers hat.Die "Shared Responsibility"-Architecture: In der Praxis wird dem DPA oft ein technisches Dokument (Shared Responsibility Matrix) angehängt. Dieses stellt klar: Der Kunde ist dafür verantwortlich, wen er in seiner Auth-Bibliothek sperrt. Ihre Plattform ist nur dafür verantwortlich, dass die API and das Dashboard, die diesen Befehl ausführen, sicher and DSGVO-konform verschlüsselt betrieben werden. [1] (https://www.domo.com/glossary/data-platform-as-a-service)Zusammenfassend: Sie müssen das Rad rechtlich not neu erfinden. Ein gut strukturierter Auftragsverarbeitungsvertrag (AVV / DPA) after Art. 28 DSGVO, der in den Leistungsbeschreibungen den „interaktiven API- and Dashboard-Zugriff on Identitätsdaten“ klar benennt, deckt Ihr Plattform-Modell rechtlich sauber ab. [1] (https://www.atlassian.com/blog/development/data-processing-agreements-dpas-developer-info), [2] (https://payproglobal.com/answers/what-is-dpa-agreement-in-saas/)Falls Sie Ihre Plattform-DPA aufsetzen, kann ich Ihnen dabei helfen, die Formulierungen for die technischen Sicherheitsmaßnahmen (TOMs) bezüglich des API-Schutzes or des Audit-Loggings zu entwerfen. Wäre das for Sie hilfreich?
