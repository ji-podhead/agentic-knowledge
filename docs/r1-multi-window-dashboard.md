---
id: "R1"
title: "R1 — Multi-Window Dashboard Grid"
type: research
date: 2026-09-06
status: final
tags: [redis]
license: CC-BY-4.0
---

# R1 — Multi-Window Dashboard Grid

## Frage
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
mit drag-resize-split-screen?

## Recherche-Aufgaben

### 1. Grid Layout Library vergleichen
Teste diese Libraries und bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` oder `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues bei resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues mit iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir auf `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistenz
- [ ] localStorage vs PostgreSQL — was ist besser für layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze mit Bewertung + Empfehlung + Link.
Entscheidung am Ende: welche Library, welches Layout-Schema, wie iframe embedding.

---

Unterhaltung im KI-Modus: ich hab ein paar fragenDu hast Folgendes gesagt: ich hab ein paar fragenich hab ein paar fragenGerne! Stelle mir deine Fragen, und ich helfe dir weiter.Um dir direkt bestmöglich zu helfen, nenne mir einfach deine Fragen oder das Thema, um das es geht.# R1 — Multi-Window Dashboard Grid

## Frage
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
mit drag-resize-split-screen?

## Recherche-Aufgaben

### 1. Grid Layout Library vergleichen
Teste diese Libraries und bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` oder `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues bei resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues mit iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir auf `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistenz
- [ ] localStorage vs PostgreSQL — was ist besser für layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze mit Bewertung + Empfehlung + Link.
Entscheidung am Ende: welche Library, welches Layout-Schema, wie iframe embedding.Hier ist die strukturierte Bewertung und Architektur-Empfehlung für dein Multi-Window Dashboard Grid.1. Grid Layout Library VergleichBewertung: Für ein Dashboard mit Iframe-Fokus ist react-grid-layout (RGL) am besten erprobt, da es Freiform-Grids bietet und in Version 2 vollen React 18+ und TypeScript-Support hat. golden-layout bietet zwar exzellentes IDE-Docking, kämpft aber stark mit Iframes, da Tabs das DOM oft komplett zerstören/neu aufbauen, was Iframe-Resets erzwingt. react-mosaic-component (Tiling) und allotment (VS Code Split Panes) bieten saubere, serielle Tree-Layouts mit guter TypeScript-Integration und kleiner Bundle Size, schränken aber die freie Dashboard-Anordnung im Vergleich zu RGL ein. Der kritische Punkt bei allen Libraries im Zusammenspiel mit Drag-und-Resize ist das "Iframe-Pointer-Capture-Problem": Sobald die Maus beim Ziehen über einen Iframe rutscht, schluckt dieser die Mouse-Events, und der Drag-Vorgang bricht ab. [1] (https://www.npmjs.com/package/react-grid-layout), [2] (https://www.npmjs.com/package/react-mosaic-component), [3] (https://www.npmjs.com/package/allotment?activeTab=dependencies)Empfehlung: Nutze react-grid-layout, wenn du klassische Dashboard-Widgets willst, oder react-mosaic-component, wenn ein striktes Kachel-Splitting (wie in einer IDE) gewünscht ist. Um das Iframe-Problem bei beiden zu lösen, musst du während des Drag/Resize-Vorgangs via globalem CSS-State pointer-events: none auf alle Iframes legen. [1] (https://www.npmjs.com/package/react-mosaic-component), [2] (https://www.npmjs.com/package/react-grid-layout)2. Iframe EmbeddingBewertung: Aus Sicherheitsgründen ist das Attribut sandbox="allow-scripts allow-same-origin" absolut kritisch; ohne allow-same-origin können Cookies/LocalStorage nicht richtig genutzt werden, während allow-scripts die Applikation im Iframe überhaupt erst lauffähig macht. Cross-Origin-Zugriffe zwischen localhost:9090 und localhost:9091 werden vom Browser blockiert (Same-Origin-Policy), weshalb direkter JS-Zugriff scheitert und Kommunikation ausschließlich via window.postMessage() erfolgen muss. Zudem müssen die eingebetteten Projekte zwingend darauf vorbereitet sein, in Iframes zu laufen: Wenn sie X-Frame-Options: DENY oder restriktive CSPs (frame-ancestors 'none') konfiguriert haben, blockiert der Browser das Laden im Dashboard vollständig. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)Empfehlung: Bette die Projekte mit sandbox="allow-scripts allow-same-origin allow-forms allow-popups" ein. Stelle sicher, dass die Quellprojekte keinen X-Frame-Options Header senden, sondern stattdessen Content-Security-Policy: frame-ancestors http://localhost:dashboard-port restriktiv setzen, und nutze eine CSS-Klasse mit width: 100%; height: 100%, um dem Iframe das automatische Skalieren des Layout-Containers zu überlassen. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)3. Layout PersistenzBewertung: localStorage eignet sich hervorragend für temporäre Benutzerpräferenzen, UI-Zustände auf Client-Seite und schnelles Prototyping ohne Latenz. PostgreSQL ist zwingend erforderlich, um Layouts persistent über mehrere Endgeräte hinweg zu speichern, geteilte Team-Templates bereitzustellen und Datenverlust beim Löschen von Browserdaten zu verhindern. Ein serialisierbares JSON-Schema reicht für beide Speicherarten völlig aus. Vordefinierte Templates (z. B. Coding, Debugging) lassen sich serverseitig als statische JSON-Schemata hinterlegen und per Knopfdruck laden.Empfehlung: Nutze PostgreSQL als Single Source of Truth für gespeicherte Layouts, puffere Änderungen im Frontend via Debounce und nutze ein Schema, das flexibel genug für Erweiterungen ist.Layout Schema:json{
  "layoutId": "uuid-v4",
  "userId": "uuid-v4",
  "name": "Debugging Template",
  "windows": [
    {
      "id": "win-1",
      "projectId": "proj-abc",
      "grid": { "x": 0, "y": 0, "w": 6, "h": 4 },
      "state": { "minimized": false, "maximized": false, "activeTab": "logs" }
    }
  ]
}
4. Single-Deploy MandatBewertung: Das Enforcement eines "Single-Deploy Mandats" (nur eine App läuft gleichzeitig aktiv) muss zwingend auf dem Backend/Server-Level (z. B. via Redis Locks oder DB-Flags) verankert sein, da Frontend-Checks leicht umgangen werden können. Der Lebenszyklus building → running → stopped → error lässt sich ideal über eine Zustandsmaschine im Backend steuern und via WebSockets (z. B. Socket.io) in Echtzeit an alle Dashboard-Instanzen streamen. Startet ein User Projekt B, muss das Backend einen atomaren Prozess anstoßen: Stopp-Signal an Instanz A senden, auf Exit warten (oder per Timeout killen), Status auf stopped setzen und danach erst das Deployment von B auf building / running umschalten.Empfehlung: Setze das Enforcement im Backend über eine Semaphore oder ein eindeutiges active_deployment-Flag in der Datenbank durch. Wenn Projekt B gestartet wird, triggert das einen orchestralen "Graceful Shutdown" von Projekt A, bevor B initialisiert wird, und informiert das Frontend live über den Zustandswechsel.