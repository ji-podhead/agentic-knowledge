---
okf_version: "1.0"
id: "okf-llm-rou-speculative-decoding"
title: "R8 — Speculative Decoding & Advanced Model Features"
topic: "general/llm-orchestration-and-routing"
subtopic: "routing-algorithms"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - llm-orchestration-and-routing
  - routing-algorithms
summary: "Welche advanced model features (speculative decoding, logprobs, reasoning) können"
---

# R8 — Speculative Decoding & Advanced Model Features

## Architectural Question
Welche advanced model features (speculative decoding, logprobs, reasoning) können
wir im proxy unterstützen and wie?

## Research Objectives

### 1. Speculative Decoding
- [ ] Wie funktioniert es?
  - Small "draft" model generiert N tokens
  - Large "verify" model verifiziert in einem forward pass
  - Akzeptierte tokens → output, rejected → fallback
  - Beschleunigung: 2-3x at guter acceptance rate
- [ ] vLLM/NIM support:
  - `--speculative-model <model_name>` flag
  - `--num-speculative-tokens N`
  - Welche draft models funktionieren gut?
  - Self-hosted NIM only? Cloud API?
- [ ] Proxy implications:
  - Speculative decoding ist server-side → proxy braucht nichts extra
  - Aber: proxy sollte es for self-hosted NIM deployments konfigurieren können
  - Deployment config: `speculative_model`, `num_speculative_tokens`

### 2. Logprobs
- [ ] Welche providers unterstützen logprobs?
  - OpenAI: `logprobs: true, top_logprobs: N`
  - vLLM/NIM: `logprobs: N` in chat completions
  - Anthropic: ? (check API)
  - Google Gemini: ?
  - Groq: ? (they use vLLM → probably yes)
  - OpenRouter: passthrough → depends on upstream
- [ ] Proxy implementation:
  - Inject `logprobs: true` in request (like stream_options.include_usage)
  - Parse logprobs from response
  - Compute entropy: Shannon entropy over top-k token probabilities
  - Store in request_log: `entropy float64` column

### 3. Reasoning Models (o1, DeepSeek-R1, Nemotron)
- [ ] Wie funktionieren reasoning models anders?
  - Internal chain-of-thought (hidden tokens)
  - Latency: höher aber bessere quality
  - API: `reasoning_effort` parameter (OpenAI o1)?
  - Token usage: reasoning tokens zählen separat?
- [ ] Proxy support:
  - `reasoning_effort` als routing signal?
  - Low effort → cheap model, high effort → reasoning model?
  - Cost tracking: reasoning tokens extra kosten?
- [ ] NVIDIA Nemotron reasoning:
  - Wie aktiviert man reasoning mode?
  - Separate model ID? API parameter?
  - Doku: developer.nvidia.com nemotron reasoning

### 4. Entropy als Routing Signal
- [ ] Können wir entropy AUS der ersten response berechnen and
  dann entscheiden ob wir nochmal with einem besseren model probieren?
  - "Self-correction": kleines model antwortet → entropy hoch → großes model übernimmt
  - Implementation: zwei-phase request
    1. Phase 1: small model with logprobs → response + entropy
    2. Wenn entropy < threshold → return response
    3. Wenn entropy >= threshold → re-route zu reasoning model
  - Latency: phase 1 dauert ~200-500ms (small model), phase 2 nur at bedarf
- [ ] Alternative: "confidence score" statt entropy
  - Manche models geben confidence scores? (not standard)
  - logprobs ist standardisierter ansatz

### 5. Token-Level Cost Optimization
- [ ] Prompt caching (OpenAI, Anthropic): cached prefix → weniger tokens
  - Proxy: kann er prompt caching headers weiterleiten?
  - OpenAI: automatic? Anthropic: `cache_control` parameter?
- [ ] Token counting: wie genau sind die token counts?
  - Streaming: wir haben jetzt stream_options.include_usage → exakt
  - Non-streaming: usage object in response → exakt
  - Logprobs tokens: zählen die als input or output tokens?

### 6. Provider-Spezifische Features
- [ ] NVIDIA NIM: `/v1/metrics` Prometheus → können wir das for routing nutzen?
  - `vllm:time_to_first_token_seconds`
  - `vllm:request_success_total`
  - `vllm:request_latency_seconds`
  - Diese sind for self-hosted NIM → cloud API 404
- [ ] Groq: ultra-low latency → immer preferezieren for einfache tasks?
- [ ] Cerebras: noch schneller? Verfügbar?

## Output Format
1. Speculative decoding: deployment config schema
2. Logprobs support matrix (welche providers ja/nein)
3. Entropy routing implementation plan (two-phase request)
4. Reasoning model support: parameter, routing signal, cost tracking
5. Provider feature matrix (was unterstützt welcher provider)

---

Hier ist die systematische Auswertung and der Implementierungsplan for die Integration von Speculative Decoding, Logprobs and fortgeschrittenen Routing-Mechanismen in deinen The Multi-Provider Gateway-Proxy.1. Speculative Decoding: Deployment-KonfigurationsschemaDa Speculative Decoding rein serverseitig in der Inferenz-Engine (vLLM / NVIDIA NIM) läuft, konfiguriert der The Multi-Provider Gateway-Proxy dies deklarativ im Deployment-Manifest der Container. Das Go-Backend übersetzt dieses Schema direkt in die CLI-Flags des Container-Starts.json{
  "$schema": "http://json-schema.org",
  "type": "object",
  "properties": {
    "speculative_decoding": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean", "default": false },
        "draft_model": {
          "type": "string",
          "description": "Kleines Model (z.B. gemma-2-2b for ein Llama-3.1-70B Target)"
        },
        "num_speculative_tokens": { "type": "integer", "default": 5, "minimum": 1, "maximum": 10 }
      },
      "required": ["enabled"]
    }
  }
}
Tipp for die Praxis: Draft- and Target-Model müssen den gleichen Tokenizer nutzen (z. B. Llama-3.1-8B als Draft for Llama-3.1-70B), da der Forward-Pass sonst fehlschlägt.2. Logprobs Support MatrixDer Proxy benötigt native Logprobs, um die Shannon-Entropie mathematisch präzise zu ermitteln.Provider / EngineLogprobs SupportAPI-ParameterZuverlässigkeit / EinschränkungenvLLM (Self-Hosted)Jalogprobs: NExtrem zuverlässig. Gibt top-N Tokens pro Position from.NVIDIA NIM (Self-Hosted)Jalogprobs: NBasiert intern on vLLM/TensorRT-LLM. Perfekt integriert.OpenAI CloudJalogprobs: true, top_logprobs: NStandardisiert, aber on max. 20 Tokens limitiert.Groq CloudJalogprobs: trueNutzt modifizierte vLLM-Backends; verhält sich wie OpenAI.OpenRouterBedingtAbhängig von UpstreamReicht Parameter through. Bei DeepSeek/Meta-Modellen meist stabil.Google GeminiNein—Native API bietet aktuell no standardisierten Logprobs for Chats.Anthropic ClaudeNein—Harter Blocker. Anthropic verweigert from Sicherheitsgründen Logprobs.3. Entropy Routing: Two-Phase Request (Selbstkorrektur)Im Gegensatz zum R4-Ansatz (wo der Planner nur 1 Token zur reinen Klassifizierung generiert) erzeugt der Two-Phase Self-Correction Ansatz die vollständige Antwort des kleinen Modells and eskaliert nur at schlechter Token-Qualität.[User Request]
      │
      ▼
┌────────────────────────────────────────┐
│ Phase 1: Small Model Call              │ ◄─── Generiert volle Antwort
│ (Parameters: logprobs: true)           │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│ Proxy Interceptor:                     │
│ Berechne Durchschnitts-Entropie (H)    │ ◄─── H_avg about alle generierten Tokens
│ about den gesamten Response-Body        │
└───────────────────┬────────────────────┘
                    │
            [H >= Threshold?]
            ───┬─────────┬───
               │         │
            [Nein]      [Ja]
               │         │
               │         ▼
               │   ┌────────────────────────────────────────┐
               │   │ Phase 2: Reroute & Discard             │
               │   │ - Verwerfe die Small-Model-Antwort    │
               │   │ - Sende Request an teures Reasoning-M. │
               │   └───────────────────┬────────────────────┘
               │                       │
               ▼                       ▼
      [Serve Small Model]     [Serve Reasoning Model]
Latenz- & Kosten-Trade-off:Best Case (Geringe Entropie): Minimale Kosten, minimale Latenz (~300ms TTFB + Generation).Worst Case (Hohe Entropie): Die Latenz von Phase 1 (~500ms) wird voll als Penalty-Verlust addiert, da der Output verworfen and der zeitintensive Reasoning-Call neu gestartet werden muss.Optimierung: Nur anwenden, wenn das Prompt-Präfix Anzeichen for "Hard Tasks" (z. B. komplexe Algorithmen) aufweist, um die Worst-Case-Quote unter 15 % zu halten.

eine sasche war da noch latent space and was nvidia auto framework noch so benutzt with low level planningHier ist die tiefere technische Analyse dazu, wie NVIDIA in seinen aktuellen Architekturen den Latent Space (latentischen Raum) manipuliert and about Low-Level-Planung (wie z. B. in NVIDIA Cosmos or den autonomen Frameworks for Robotik/Weltmodelle) Agenten-Steuerungen on unterster Ebene realisiert.1. Latent Space Planning: Token-level vs. Continuous Vector SpaceKlassische LLMs planen im diskreten Raum (Wort-Token for Wort-Token). NVIDIAs fortgeschrittene Frameworks (insbesondere for multimodale Weltmodelle and autonome Systeme) brechen hieraus from:Der Latent Space als Simulator: Anstatt Text zu generieren, komprimieren Encoder (wie Video- or Sensor-Autoencoder) die reale Welt in einen kontinuierlichen, hochdimensionalen Vektorraum – den Latent Space.World Models: Ein Modell (z. B. NVIDIA Cosmos or GAIA) generiert no Pixel, sondern sagt die nächste latente Repräsentation der Welt voraus, wenn ein Agent eine bestimmte Aktion ausführt.Vorteil for den Proxy/Agenten: Die Planung findet in einem komprimierten Raum statt, der physikalische Gesetze versteht, bevor überhaupt Text or Steuerbefehle decodiert werden. Das spart massiv Rechenleistung.2. NVIDIA Auto/Robotics Frameworks (Low-Level Planning)NVIDIA nutzt hierfür Frameworks wie Isaac Lab, NVIDIA Cosmos and die NVIDIA Drive/Robotics AI Workflows. Diese kombinieren High-Level-LLMs with mathematisch exakter Low-Level-Steuerung.+-----------------------------------------------------------+

| High-Level Agent (LLM / DSH Plugin)                      |
| "Fahre vorsichtig um das Hindernis herum."                |
+-----------------------------+-----------------------------+
                              |
                              v (Übersetzung in latente Goals)
+-----------------------------+-----------------------------+

| Latent Space Planner (Cosmos / World Model)               |
| Simuliert zukünftige Zustände im Vektorraum               |
+-----------------------------+-----------------------------+
                              |
                              v (Trajektorien-Vorgabe)
+-----------------------------+-----------------------------+

| Low-Level Controller (Isaac / MPC / TensorRT)             |
| Berechnet exakte Physik-Frequenzen (z.B. 200 Hz Drehmoment) |
+-----------------------------------------------------------+
Hierarchische Planung (HRL): Ein High-Level-Modell (z. B. ein feingetuntes Llama/Nemotron in deinem DSH-Dashboard) gibt die strategische Richtung before („Generiere einen Pfad through Datei X“ or „Bewege den Roboterarm zu Punkt Y“).Low-Level Execution: Das Framework bricht dies in mathematische Trajektorien or minimale logische Operationen herunter, die about Model Predictive Control (MPC) or extrem schnelle, spezialisierte Mini-Netze (TensorRT-optimiert) ausgeführt werden.3. Was bedeutet das for unsere The Multi-Provider Gateway- / DSH-Architektur?Wenn du diese Konzepte in deinem Multi-Window-Dashboard and Proxy-System spiegeln möchtest, implementierst du das Hierarchical Agent Pattern:High-Level Orchestration (DSH / R7): Der User interagiert with dem DSH-Interface. Die Gating-Agenten (R6) arbeiten rein on logischer, abstrakter Ebene (Code-Struktur planen, System-Architektur entwerfen).Low-Level Pipeline Execution (The Multi-Provider Gateway Go Core): Der Go-Core fungiert als der "Physik-Motor" or Low-Level-Planer. Er kümmert sich um die atomaren, latenzkritischen Operationen:Er führt den Entropy-Check (R4) on Token-Ebene from.Er steuert die genauen Container-Neustarts and Dateisystem-Patches (R2/R3).Er übersetzt die abstrakten Agenten-Wünsche in exakt getaktete HTTP/gRPC-Streams.Durch diese strikte Trennung bleibt dein Frontend (DSH) sauber and reaktionsschnell for den Menschen, während der Go-Core (The Multi-Provider Gateway) die performante, deterministische "Low-Level-Arbeit" im Background verrichtet.Möchtest du als Nächstes sehen, wie wir im The Multi-Provider Gateway Go Core ein hierarchisches Queue-System aufbauen, das High-Level-Tasks in diese schnellen Low-Level-Execution-Steps zerlegt, or sollen wir die Schnittstelle for multimodale Streams (falls du Video-/Sensordaten verarbeiten willst) definieren?
