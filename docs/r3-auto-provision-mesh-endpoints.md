---
id: "R3"
title: "R3 — Auto-Provision: Mesh Endpoints in Coding Deployments"
type: research
date: 2026-09-06
status: final
tags: [mesh, llama]
license: CC-BY-4.0
---

# R3 — Auto-Provision: Mesh Endpoints in Coding Deployments

## Frage
Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als
provider in coding deployments (Ollama, OpenCode, DSH)?

## Recherche-Aufgaben

### 1. Ziel-Formate
Welche config formats brauchen coding tools für custom providers?

- [ ] **OpenCode**: provider config format? JSON? YAML? Wo gespeichert?
  - Suchen: OpenCode docs für custom provider / custom OpenAI endpoint
  - Felder: `base_url`, `api_key`, `model_name`?
- [ ] **Ollama**: kann Ollama einen remote OpenAI endpoint als model registrieren?
  - `ollama pull` von custom model? Modelfile mit `FROM` remote?
  - Oder besser: JiMesh als OpenAI proxy → coding tool zeigt auf `jimesh:9091`
- [ ] **DSH (DeepSeek Harness)**: provider config in vconfig.json?
  - Wie trägt man custom OpenAI endpoint ein?
  - Können wir DSH models page nutzen um JiMesh zu registrieren?
- [ ] **Cursor / VS Code**: `.cursor/config`? settings.json `openai.baseUrl`?

### 2. Provisioning API
- [ ] `POST /api/projects/{id}/provision` — body: `{ chainId, format }`
  - Liest die chain endpoint URL + deploy token aus JiMesh
  - Schreibt sie ins coding tool's config format
  - Restartet das tool falls nötig (hot-reload vs redeploy)
- [ ] Auto-provision: beim deploy eines coding projects → automatisch alle
  aktiven mesh chains als provider eintragen
- [ ] Provisioning status: erfolgreich? Config überschrieben? Backup erstellt?

### 3. Model-Namens-Mapping
- [ ] JiMesh chain name → coding tool model name
  - `smart:coding-free` → model name in OpenCode?
  - Multiple chains → multiple "models" in der auswahl?
- [ ] Model discovery: coding tool sollte `/v1/models` vom JiMesh proxy abrufen
  können → wir haben das schon (`/v1/models` endpoint)
- [ ] Brauchen wir einen dedizierten `/v1/models` der die chain-namen als
  "models" zurückgibt? (statt platform model IDs)

### 4. Mouse-Click Provisioning
- [ ] Per drag-drop: mesh endpoint aus sidebar → coding deployment config
- [ ] Per button: "Add to OpenCode" / "Add to DSH" neben jedem chain
- [ ] Per auto: checkbox "auto-provision on deploy" pro coding project
- [ ] Feedback: toast "Added smart:coding-free to OpenCode as model 'jimesh-coding-free'"

## Output Format
Pro coding tool: config path, format, fields, provisioning command.
Empfehlung: auto-provision strategy (auto vs manual vs hybrid).
Schema für `/v1/models` endpoint der chain-namen zurückgibt.

---

Hier ist das Systemdesign für das automatische Provisionieren von JiMesh Fallback Endpoints und Modellen direkt in deine Coding-Deployments.1. Ziel-Formate der Coding ToolsToolConfig-Pfad (relativ / global)FormatWichtige Felder für Custom ProviderProvisioning Command / TriggerOpenCode~/.config/opencode/opencode.json (global) oder opencode.json (Projekt)JSON"provider": { "jimesh": { "options": { "baseURL": "...", "apiKey": "..." }, "models": { "chain-id": {} } } }POST /api/projects/{id}/config -> JSON-Patch (Kein Restart nötig bei Dateimanipulation)Ollama— (Wird als Proxy umgangen)Modelfile / APIKein Pull nötig. JiMesh agiert direkt als Proxy, sodass andere Tools auf jimesh:9091 statt auf Ollama zeigen.Keiner (JiMesh fängt /v1/chat/completions ab).DSH./vconfig.json (im Workspace)JSON"openai_compatible_providers": [{ "name": "JiMesh", "api_base": "...", "api_key": "..." }]In-Memory Hot-Reload via Client-HMR (pnpm run dev:web).Cursor / VS Code.cursorrules / .vscode/settings.jsonJSON"openai.baseUrl": "http://localhost:9091/v1", "openai.apiKey": "jimesh-token"Automatisches Einlesen durch den Datei-Watcher der IDE.OpenCode-Besonderheit: OpenCode erlaubt das Einbinden von Custom OpenAI-kompatiblen Endpunkten über die Definition eines Custom-Schlüssels im "provider"-Objekt (z. B. "jimesh"), benötigt aber zwingend die explizite Auflistung der verfügbaren Modell-IDs unter "models". [1] (https://github.com/orgs/community/discussions/200311), [2] (https://docs.ollama.com/integrations/opencode)Ollama-Strategie: Ollama über ein Modelfile mit FROM http://... zu provisionieren fügt unnedige Netzwerklatenz und Speicher-Overhead hinzu. Die Architektur-Empfehlung lautet hier klar: JiMesh als zentraler OpenAI-Proxy, an den sich die Editoren direkt hängen.2. Provisioning API (POST /api/projects/{id}/provision)Wenn ein Projekt deployt wird (oder ein neuer Mesh-Fallback-Endpoint via Drag-and-Drop hinzukommt), stößt das Dashboard die Provisionierung an:Read State: Das Backend liest die aktive Mesh-Konfiguration (Chain-URLs und Tokens) aus der JiMesh-Instanz aus.Generate Config Patch: Basierend auf dem Typ des Ziel-Deployments wird die spezifische Konfigurationsdatei manipuliert.Backup & Write: Das Backend sichert die bestehende Datei (.json.bak) und schreibt die neue Struktur atomar.HMR Trigger / Reload: Bei DSH wird der Hot-Reload-Endpoint getriggert; OpenCode liest die Projekt-opencode.json beim nächsten Befehl automatisch frisch ein.3. Model-Namens-Mapping (/v1/models)Da Editoren und CLI-Tools wie OpenCode dynamische oder statische Modelllisten erwarten, muss JiMesh einen dedizierten, standardkonformen OpenAI-Endpoint bereitstellen, der die aktiven Mesh-Chains als virtuelle Modell-IDs ausgibt. [1] (https://github.com/anomalyco/opencode/issues/26863), [2] (https://github.com/orgs/community/discussions/200311)Schema für den /v1/models Endpoint:json{
  "object": "list",
  "data": [
    {
      "id": "jimesh:smart:coding-free",
      "object": "model",
      "created": 1717545600,
      "owned_by": "jimesh-mesh"
    },
    {
      "id": "jimesh:fast:inline-completion",
      "object": "model",
      "created": 1717545600,
      "owned_by": "jimesh-mesh"
    }
  ]
}
Nutzen: In OpenCode wird das Modell dann deklarativ als jimesh/jimesh:smart:coding-free angesprochen. [1] (https://opencode.ai/docs/models/)4. UX & Provisionierungs-StrategieEmpfehlung: Hybrid-Strategie (Auto-Provision on Deploy + Manual Override via Sidebar).Ablauf:Standardmäßig ist in den Projekt-Settings die Checkbox "Auto-provision active mesh chains on deploy" aktiv. Beim Klick auf "Deploy" schreibt das System die Endpunkte vollautomatisch.Mouse-Click UX: In der linken Sidebar des Dashboards befindet sich die Liste der aktiven JiMesh-Chains. Der Entwickler kann eine Chain per Drag-and-Drop in das geöffnete Editor-Fenster (oder auf die Deployment-Card) ziehen. Ein fliegender Tooltip zeigt "Add to OpenCode as Model" an. Nach dem Drop erscheint ein Toast: „⚡ Added smart:coding-free to OpenCode as model 'jimesh:smart:coding-free'“.🛠 Beispiel für den OpenCode-Config-Patch (Backend-Logik)So sieht der JSON-Inhalt aus, den die Provisioning-Engine automatisch in die opencode.json deines Zielprojekts injiziert: [1] (https://docs.ollama.com/integrations/opencode)json{
  "$schema": "https://opencode.ai/config.json",
  "model": "jimesh/jimesh:smart:coding-free",
  "provider": {
    "jimesh": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "JiMesh Proxy",
      "options": {
        "baseURL": "http://localhost:9091/v1",
        "apiKey": "jm_live_tkn_84920f"
      },
      "models": {
        "jimesh:smart:coding-free": {},
        "jimesh:fast:inline-completion": {}
      }
    }
  }
}
Möchtest du als Nächstes den Code für den Node.js-Dateipatcher sehen, der die JSON/JSONC-Dateien ohne Verlust von User-Kommentaren modifiziert, oder sollen wir den Go-Handler für den virtuellen /v1/models-Endpoint in JiMesh schreiben? [1] (https://opencode.ai/docs/config/)