---
okf_version: "1.0"
id: "okf-fro-das-multi-window-dashboard"
title: "R1 — Multi-Window Dashboard Grid"
topic: "general/frontend-and-ui-architecture"
subtopic: "dashboard-and-widgets"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - frontend-and-ui-architecture
  - dashboard-and-widgets
summary: "Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet"
---

# R1 — Multi-Window Dashboard Grid

## Architectural Question
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
with drag-resize-split-screen?

## Research Objectives

### 1. Grid Layout Library compare
Teste diese Libraries and bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` or `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues at resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues with iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir on `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistence
- [ ] localStorage vs PostgreSQL — was ist besser for layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze with Bewertung + Recommendation + Link.
Decision am Ende: welche Library, welches Layout-Schema, wie iframe embedding.

---

## Architectural Question
Wie bauen wir ein Multi-Window Dashboard wo man HTTP-Projekte als iframe einbettet
with drag-resize-split-screen?

## Research Objectives

### 1. Grid Layout Library compare
Teste diese Libraries and bewerte:
- [ ] `react-grid-layout` — reift, drag+resize, responsive breakpoints. npm page?
- [ ] `golden-layout` — docking-style (wie IDE panels), stack/tab/float
- [ ] `muxt` or `react-mosaic` — tiling window manager
- [ ] `allotment` — VS Code-style split panes

Pro Library bewerten:
- Bundle size?
- TypeScript support?
- Resize per drag?
- Persist layout (save/load positions)?
- Iframe support (re-render issues at resize)?
- Aktiv maintained? (last commit, stars)
- Bekannte Issues with iframes?

### 2. Iframe Embedding
- [ ] Sandbox attribute: `allow-scripts allow-same-origin` — security implications?
- [ ] Cross-origin iframes: können wir on `http://localhost:9090` von `http://localhost:9091` zugreifen?
- [ ] X-Frame-Options / CSP: müssen Projekte `X-Frame-Options: ALLOWALL` setzen?
- [ ] Resize observer: iframe content resize → grid resize?
- [ ] Performance: 5+ iframes gleichzeitig — memory impact?

### 3. Layout Persistence
- [ ] localStorage vs PostgreSQL — was ist besser for layout state?
- [ ] Layout schema: `{ projectId, x, y, w, h, minimized, maximized }`
- [ ] Reset-to-default button?
- [ ] Template layouts (coding, monitoring, debugging)?

### 4. Single-Deploy Mandat
- [ ] Nur ein Projekt deploybar gleichzeitig — wie enforcement?
- [ ] Deploy status: `building → running → stopped → error`
- [ ] Was passiert wenn man Projekt B deployt während A läuft? Auto-stop A?

## Output Format
Für jedes der 4 Themen: 3-5 Sätze with Bewertung + Recommendation + Link.
Decision am Ende: welche Library, welches Layout-Schema, wie iframe embedding.Hier ist die strukturierte Bewertung and Architektur-Recommendation for dein Multi-Window Dashboard Grid.1. Grid Layout Library VergleichBewertung: Für ein Dashboard with Iframe-Fokus ist react-grid-layout (RGL) am besten erprobt, da es Freiform-Grids bietet and in Version 2 vollen React 18+ and TypeScript-Support hat. golden-layout bietet zwar exzellentes IDE-Docking, kämpft aber stark with Iframes, da Tabs das DOM oft komplett zerstören/neu aufbauen, was Iframe-Resets erzwingt. react-mosaic-component (Tiling) and allotment (VS Code Split Panes) bieten saubere, serielle Tree-Layouts with guter TypeScript-Integration and kleiner Bundle Size, schränken aber die freie Dashboard-Anordnung im Comparison zu RGL ein. Der kritische Punkt at allen Libraries im Zusammenspiel with Drag-and-Resize ist das "Iframe-Pointer-Capture-Problem": Sobald die Maus beim Ziehen about einen Iframe rutscht, schluckt dieser die Mouse-Events, and der Drag-Vorgang bricht ab. [1] (https://www.npmjs.com/package/react-grid-layout), [2] (https://www.npmjs.com/package/react-mosaic-component), [3] (https://www.npmjs.com/package/allotment?activeTab=dependencies)Recommendation: Nutze react-grid-layout, wenn du klassische Dashboard-Widgets willst, or react-mosaic-component, wenn ein striktes Kachel-Splitting (wie in einer IDE) gewünscht ist. Um das Iframe-Problem at beiden zu lösen, musst du während des Drag/Resize-Vorgangs via globalem CSS-State pointer-events: none on alle Iframes legen. [1] (https://www.npmjs.com/package/react-mosaic-component), [2] (https://www.npmjs.com/package/react-grid-layout)2. Iframe EmbeddingBewertung: Aus Sicherheitsgründen ist das Attribut sandbox="allow-scripts allow-same-origin" absolut kritisch; without allow-same-origin können Cookies/LocalStorage not richtig genutzt werden, während allow-scripts die Applikation im Iframe überhaupt erst lauffähig macht. Cross-Origin-Zugriffe zwischen localhost:9090 and localhost:9091 werden vom Browser blockiert (Same-Origin-Policy), weshalb direkter JS-Zugriff scheitert and Kommunikation ausschließlich via window.postMessage() erfolgen muss. Zudem müssen die eingebetteten Projekte zwingend darauf vorbereitet sein, in Iframes zu laufen: Wenn sie X-Frame-Options: DENY or restriktive CSPs (frame-ancestors 'none') konfiguriert haben, blockiert der Browser das Laden im Dashboard vollständig. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)Recommendation: Bette die Projekte with sandbox="allow-scripts allow-same-origin allow-forms allow-popups" ein. Stelle sicher, dass die Quellprojekte keinen X-Frame-Options Header senden, sondern stattdessen Content-Security-Policy: frame-ancestors http://localhost:dashboard-port restriktiv setzen, and nutze eine CSS-Klasse with width: 100%; height: 100%, um dem Iframe das automatische Skalieren des Layout-Containers zu überlassen. [1] (https://kb.scompler.com/en/knowledge/widgets-i-can-create-in-my-project)3. Layout PersistenzBewertung: localStorage eignet sich hervorragend for temporäre Benutzerpräferenzen, UI-Zustände on Client-Seite and schnelles Prototyping without Latenz. PostgreSQL ist zwingend erforderlich, um Layouts persistent about mehrere Endgeräte hinweg zu speichern, geteilte Team-Templates bereitzustellen and Datenverlust beim Löschen von Browserdaten zu verhindern. Ein serialisierbares JSON-Schema reicht for beide Speicherarten völlig from. Vordefinierte Templates (z. B. Coding, Debugging) lassen sich serverseitig als statische JSON-Schemata hinterlegen and per Knopfdruck laden.Recommendation: Nutze PostgreSQL als Single Source of Truth for gespeicherte Layouts, puffere Änderungen im Frontend via Debounce and nutze ein Schema, das flexibel genug for Erweiterungen ist.Layout Schema:json{
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
4. Single-Deploy MandatBewertung: Das Enforcement eines "Single-Deploy Mandats" (nur eine App läuft gleichzeitig aktiv) muss zwingend on dem Backend/Server-Level (z. B. via Redis Locks or DB-Flags) verankert sein, da Frontend-Checks leicht umgangen werden können. Der Lebenszyklus building → running → stopped → error lässt sich ideal about eine Zustandsmaschine im Backend steuern and via WebSockets (z. B. Socket.io) in Echtzeit an alle Dashboard-Instanzen streamen. Startet ein User Projekt B, muss das Backend einen atomaren Prozess anstoßen: Stopp-Signal an Instanz A senden, on Exit warten (or per Timeout killen), Status on stopped setzen and danach erst das Deployment von B on building / running umschalten.Recommendation: Setze das Enforcement im Backend about eine Semaphore or ein eindeutiges active_deployment-Flag in der Datenbank through. Wenn Projekt B gestartet wird, triggert das einen orchestralen "Graceful Shutdown" von Projekt A, bevor B initialisiert wird, and informiert das Frontend live about den Zustandswechsel.
