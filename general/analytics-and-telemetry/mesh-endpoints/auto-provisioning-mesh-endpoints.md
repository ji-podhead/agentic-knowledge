---
okf_version: "1.0"
id: "okf-ana-mes-auto-provisioning-mesh-endpoints"
title: "R3 — Auto-Provision: Mesh Endpoints in Coding Deployments"
topic: "general/analytics-and-telemetry"
subtopic: "mesh-endpoints"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - analytics-and-telemetry
  - mesh-endpoints
summary: "Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als"
---

# R3 — Auto-Provision: Mesh Endpoints in Coding Deployments

## Architectural Question
Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als
provider in coding deployments (Ollama, OpenCode, DSH)?

## Research Objectives

### 1. Ziel-Formate
Welche config formats brauchen coding tools for custom providers?

- [ ] **OpenCode**: provider config format? JSON? YAML? Wo gespeichert?
  - Suchen: OpenCode docs for custom provider / custom OpenAI endpoint
  - Felder: `base_url`, `api_key`, `model_name`?
- [ ] **Ollama**: kann Ollama einen remote OpenAI endpoint als model registrieren?
  - `ollama pull` von custom model? Modelfile with `FROM` remote?
  - Oder besser: The Multi-Provider Gateway als OpenAI proxy → coding tool zeigt on `llm-mesh-gateway:9091`
- [ ] **DSH (DeepSeek Harness)**: provider config in vconfig.json?
  - Wie trägt man custom OpenAI endpoint ein?
  - Können wir DSH models page nutzen um The Multi-Provider Gateway zu registrieren?
- [ ] **Cursor / VS Code**: `.cursor/config`? settings.json `openai.baseUrl`?

### 2. Provisioning API
- [ ] `POST /api/projects/{id}/provision` — body: `{ chainId, format }`
  - Liest die chain endpoint URL + deploy token from The Multi-Provider Gateway
  - Schreibt sie ins coding tool's config format
  - Restartet das tool falls nötig (hot-reload vs redeploy)
- [ ] Auto-provision: beim deploy eines coding projects → automatisch alle
  aktiven mesh chains als provider eintragen
- [ ] Provisioning status: erfolgreich? Config überschrieben? Backup erstellt?

### 3. Model-Namens-Mapping
- [ ] The Multi-Provider Gateway chain name → coding tool model name
  - `smart:coding-free` → model name in OpenCode?
  - Multiple chains → multiple "models" in der auswahl?
- [ ] Model discovery: coding tool sollte `/v1/models` vom The Multi-Provider Gateway proxy abrufen
  können → wir haben das schon (`/v1/models` endpoint)
- [ ] Brauchen wir einen dedizierten `/v1/models` der die chain-namen als
  "models" zurückgibt? (statt platform model IDs)

### 4. Mouse-Click Provisioning
- [ ] Per drag-drop: mesh endpoint from sidebar → coding deployment config
- [ ] Per button: "Add to OpenCode" / "Add to DSH" neben jedem chain
- [ ] Per auto: checkbox "auto-provision on deploy" pro coding project
- [ ] Feedback: toast "Added smart:coding-free to OpenCode as model 'llm-mesh-gateway-coding-free'"

## Output Format
Pro coding tool: config path, format, fields, provisioning command.
Recommendation: auto-provision strategy (auto vs manual vs hybrid).
Schema for `/v1/models` endpoint der chain-namen zurückgibt.

---

Hier ist das Systemdesign for das automatische Provisionieren von The Multi-Provider Gateway Fallback Endpoints and Modellen direkt in deine Coding-Deployments.1. Ziel-Formate der Coding ToolsToolConfig-Pfad (relativ / global)FormatWichtige Felder for Custom ProviderProvisioning Command / TriggerOpenCode~/.config/opencode/opencode.json (global) or opencode.json (Projekt)JSON"provider": { "llm-mesh-gateway": { "options": { "baseURL": "...", "apiKey": "..." }, "models": { "chain-id": {} } } }POST /api/projects/{id}/config -> JSON-Patch (Kein Restart nötig at Dateimanipulation)Ollama— (Wird als Proxy umgangen)Modelfile / APIKein Pull nötig. The Multi-Provider Gateway agiert direkt als Proxy, sodass andere Tools on llm-mesh-gateway:9091 statt on Ollama zeigen.Keiner (The Multi-Provider Gateway fängt /v1/chat/completions ab).DSH./vconfig.json (im Workspace)JSON"openai_compatible_providers": [{ "name": "The Multi-Provider Gateway", "api_base": "...", "api_key": "..." }]In-Memory Hot-Reload via Client-HMR (pnpm run dev:web).Cursor / VS Code.cursorrules / .vscode/settings.jsonJSON"openai.baseUrl": "http://localhost:9091/v1", "openai.apiKey": "llm-mesh-gateway-token"Automatisches Einlesen through den Datei-Watcher der IDE.OpenCode-Besonderheit: OpenCode erlaubt das Einbinden von Custom OpenAI-kompatiblen Endpunkten about die Definition eines Custom-Schlüssels im "provider"-Objekt (z. B. "llm-mesh-gateway"), benötigt aber zwingend die explizite Auflistung der verfügbaren Modell-IDs unter "models". [1] (https://github.com/orgs/community/discussions/200311), [2] (https://docs.ollama.com/integrations/opencode)Ollama-Strategie: Ollama about ein Modelfile with FROM http://... zu provisionieren fügt unnedige Netzwerklatenz and Speicher-Overhead hinzu. Die Architektur-Recommendation lautet hier klar: The Multi-Provider Gateway als zentraler OpenAI-Proxy, an den sich die Editoren direkt hängen.2. Provisioning API (POST /api/projects/{id}/provision)Wenn ein Projekt deployt wird (or ein neuer Mesh-Fallback-Endpoint via Drag-and-Drop hinzukommt), stößt das Dashboard die Provisionierung an:Read State: Das Backend liest die aktive Mesh-Konfiguration (Chain-URLs and Tokens) from der The Multi-Provider Gateway-Instanz from.Generate Config Patch: Basierend on dem Typ des Ziel-Deployments wird die spezifische Konfigurationsdatei manipuliert.Backup & Write: Das Backend sichert die bestehende Datei (.json.bak) and schreibt die neue Struktur atomar.HMR Trigger / Reload: Bei DSH wird der Hot-Reload-Endpoint getriggert; OpenCode liest die Projekt-opencode.json beim nächsten Befehl automatisch frisch ein.3. Model-Namens-Mapping (/v1/models)Da Editoren and CLI-Tools wie OpenCode dynamische or statische Modelllisten erwarten, muss The Multi-Provider Gateway einen dedizierten, standardkonformen OpenAI-Endpoint bereitstellen, der die aktiven Mesh-Chains als virtuelle Modell-IDs ausgibt. [1] (https://github.com/anomalyco/opencode/issues/26863), [2] (https://github.com/orgs/community/discussions/200311)Schema for den /v1/models Endpoint:json{
  "object": "list",
  "data": [
    {
      "id": "llm-mesh-gateway:smart:coding-free",
      "object": "model",
      "created": 1717545600,
      "owned_by": "llm-mesh-gateway-mesh"
    },
    {
      "id": "llm-mesh-gateway:fast:inline-completion",
      "object": "model",
      "created": 1717545600,
      "owned_by": "llm-mesh-gateway-mesh"
    }
  ]
}
Nutzen: In OpenCode wird das Modell dann deklarativ als llm-mesh-gateway/llm-mesh-gateway:smart:coding-free angesprochen. [1] (https://opencode.ai/docs/models/)4. UX & Provisionierungs-StrategieEmpfehlung: Hybrid-Strategie (Auto-Provision on Deploy + Manual Override via Sidebar).Ablauf:Standardmäßig ist in den Projekt-Settings die Checkbox "Auto-provision active mesh chains on deploy" aktiv. Beim Klick on "Deploy" schreibt das System die Endpunkte vollautomatisch.Mouse-Click UX: In der linken Sidebar des Dashboards befindet sich die Liste der aktiven The Multi-Provider Gateway-Chains. Der Entwickler kann eine Chain per Drag-and-Drop in das geöffnete Editor-Fenster (or on die Deployment-Card) ziehen. Ein fliegender Tooltip zeigt "Add to OpenCode as Model" an. Nach dem Drop erscheint ein Toast: „⚡ Added smart:coding-free to OpenCode as model 'llm-mesh-gateway:smart:coding-free'“.🛠 Beispiel for den OpenCode-Config-Patch (Backend-Logik)So sieht der JSON-Inhalt from, den die Provisioning-Engine automatisch in die opencode.json deines Zielprojekts injiziert: [1] (https://docs.ollama.com/integrations/opencode)json{
  "$schema": "https://opencode.ai/config.json",
  "model": "llm-mesh-gateway/llm-mesh-gateway:smart:coding-free",
  "provider": {
    "llm-mesh-gateway": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "The Multi-Provider Gateway Proxy",
      "options": {
        "baseURL": "http://localhost:9091/v1",
        "apiKey": "jm_live_tkn_84920f"
      },
      "models": {
        "llm-mesh-gateway:smart:coding-free": {},
        "llm-mesh-gateway:fast:inline-completion": {}
      }
    }
  }
}
Möchtest du als Nächstes den Code for den Node.js-Dateipatcher sehen, der die JSON/JSONC-Dateien without Verlust von User-Kommentaren modifiziert, or sollen wir den Go-Handler for den virtuellen /v1/models-Endpoint in The Multi-Provider Gateway schreiben? [1] (https://opencode.ai/docs/config/)
