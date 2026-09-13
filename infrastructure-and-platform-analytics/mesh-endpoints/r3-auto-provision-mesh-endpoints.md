---
okf_version: "1.0"
id: "okf-inf-mes-r3-auto-provision-mesh-endpoints"
title: "R3 — Auto-Provision: Mesh Endpoints in Coding Deployments"
topic: "infrastructure-and-platform-analytics"
subtopic: "mesh-endpoints"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - infrastructure-and-platform-analytics
  - mesh-endpoints
summary: "Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als"
---

# R3 — Auto-Provision: Mesh Endpoints in Coding Deployments

## Question
Wie provisionieren wir automatisch unsere mesh fallback endpoints + models als
provider in coding deployments (Ollama, OpenCode, DSH)?

## Research Tasks

### 1. Ziel-Formate
Welche config formats brauchen coding tools for custom providers?

- [ ] **OpenCode**: provider config format? JSON? YAML? Wo gespeichert?
  - Suchen: OpenCode docs for custom provider / custom OpenAI endpoint
  - Felder: `base_url`, `api_key`, `model_name`?
- [ ] **Ollama**: kann Ollama einen remote OpenAI endpoint als model registrieren?
  - `ollama pull` von custom model? Modelfile with `FROM` remote?
  - Oder besser: OpenMesh als OpenAI proxy → coding tool zeigt on `openmesh:9091`
- [ ] **DSH (DeepSeek Harness)**: provider config in vconfig.json?
  - Wie trägt man custom OpenAI endpoint ein?
  - Können wir DSH models page nutzen um OpenMesh zu registrieren?
- [ ] **Cursor / VS Code**: `.cursor/config`? settings.json `openai.baseUrl`?

### 2. Provisioning API
- [ ] `POST /api/projects/{id}/provision` — body: `{ chainId, format }`
  - Liest die chain endpoint URL + deploy token from OpenMesh
  - Schreibt sie ins coding tool's config format
  - Restartet das tool falls nötig (hot-reload vs redeploy)
- [ ] Auto-provision: beim deploy eines coding projects → automatisch alle
  aktiven mesh chains als provider eintragen
- [ ] Provisioning status: erfolgreich? Config überschrieben? Backup erstellt?

### 3. Model-Namens-Mapping
- [ ] OpenMesh chain name → coding tool model name
  - `smart:coding-free` → model name in OpenCode?
  - Multiple chains → multiple "models" in der auswahl?
- [ ] Model discovery: coding tool sollte `/v1/models` vom OpenMesh proxy abrufen
  können → wir haben das schon (`/v1/models` endpoint)
- [ ] Brauchen wir einen dedizierten `/v1/models` der die chain-namen als
  "models" zurückgibt? (statt platform model IDs)

### 4. Mouse-Click Provisioning
- [ ] Per drag-drop: mesh endpoint from sidebar → coding deployment config
- [ ] Per button: "Add to OpenCode" / "Add to DSH" neben jedem chain
- [ ] Per auto: checkbox "auto-provision on deploy" pro coding project
- [ ] Feedback: toast "Added smart:coding-free to OpenCode as model 'openmesh-coding-free'"

## Output Format
Pro coding tool: config path, format, fields, provisioning command.
Empfehlung: auto-provision strategy (auto vs manual vs hybrid).
Schema for `/v1/models` endpoint der chain-namen zurückgibt.

---

Hier ist das Systemdesign for das automatische Provisionieren von OpenMesh Fallback Endpoints and Modellen direkt in deine Coding-Deployments.1. Ziel-Formate der Coding ToolsToolConfig-Pfad (relativ / global)FormatWichtige Felder for Custom ProviderProvisioning Command / TriggerOpenCode~/.config/opencode/opencode.json (global) or opencode.json (Projekt)JSON"provider": { "openmesh": { "options": { "baseURL": "...", "apiKey": "..." }, "models": { "chain-id": {} } } }POST /api/projects/{id}/config -> JSON-Patch (Kein Restart nötig at Dateimanipulation)Ollama— (Wird als Proxy umgangen)Modelfile / APIKein Pull nötig. OpenMesh agiert direkt als Proxy, sodass andere Tools on openmesh:9091 statt on Ollama zeigen.Keiner (OpenMesh fängt /v1/chat/completions ab).DSH./vconfig.json (im Workspace)JSON"openai_compatible_providers": [{ "name": "OpenMesh", "api_base": "...", "api_key": "..." }]In-Memory Hot-Reload via Client-HMR (pnpm run dev:web).Cursor / VS Code.cursorrules / .vscode/settings.jsonJSON"openai.baseUrl": "http://localhost:9091/v1", "openai.apiKey": "openmesh-token"Automatisches Einlesen through den Datei-Watcher der IDE.OpenCode-Besonderheit: OpenCode erlaubt das Einbinden von Custom OpenAI-kompatiblen Endpunkten about die Definition eines Custom-Schlüssels im "provider"-Objekt (z. B. "openmesh"), benötigt aber zwingend die explizite Auflistung der verfügbaren Modell-IDs unter "models". [1] (https://github.com/orgs/community/discussions/200311), [2] (https://docs.ollama.com/integrations/opencode)Ollama-Strategie: Ollama about ein Modelfile with FROM http://... zu provisionieren fügt unnedige Netzwerklatenz and Speicher-Overhead hinzu. Die Architecture-Empfehlung lautet hier klar: OpenMesh als zentraler OpenAI-Proxy, an den sich die Editoren direkt hängen.2. Provisioning API (POST /api/projects/{id}/provision)Wenn ein Projekt deployt wird (or ein neuer Mesh-Fallback-Endpoint via Drag-and-Drop hinzukommt), stößt das Dashboard die Provisionierung an:Read State: Das Backend liest die aktive Mesh-Konfiguration (Chain-URLs and Tokens) from der OpenMesh-Instanz from.Generate Config Patch: Basierend on dem Typ des Ziel-Deployments wird die spezifische Konfigurationsdatei manipuliert.Backup & Write: Das Backend sichert die bestehende Datei (.json.bak) and schreibt die neue Struktur atomar.HMR Trigger / Reload: Bei DSH wird der Hot-Reload-Endpoint getriggert; OpenCode liest die Projekt-opencode.json beim nächsten Befehl automatisch frisch ein.3. Model-Namens-Mapping (/v1/models)Da Editoren and CLI-Tools wie OpenCode dynamische or statische Modelllisten erwarten, muss OpenMesh einen dedizierten, standardkonformen OpenAI-Endpoint bereitstellen, der die aktiven Mesh-Chains als virtuelle Modell-IDs ausgibt. [1] (https://github.com/anomalyco/opencode/issues/26863), [2] (https://github.com/orgs/community/discussions/200311)Schema for den /v1/models Endpoint:json{
  "object": "list",
  "data": [
    {
      "id": "openmesh:smart:coding-free",
      "object": "model",
      "created": 1717545600,
      "owned_by": "openmesh-mesh"
    },
    {
      "id": "openmesh:fast:inline-completion",
      "object": "model",
      "created": 1717545600,
      "owned_by": "openmesh-mesh"
    }
  ]
}
  "$schema": "https://opencode.ai/config.json",
  "model": "openmesh/openmesh:smart:coding-free",
  "provider": {
    "openmesh": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "OpenMesh Proxy",
      "options": {
        "baseURL": "http://localhost:9091/v1",
        "apiKey": "jm_live_tkn_84920f"
      },
      "models": {
        "openmesh:smart:coding-free": {},
        "openmesh:fast:inline-completion": {}
      }
    }
  }
}
