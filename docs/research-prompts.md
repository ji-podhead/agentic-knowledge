---
id: "research-prompts"
title: "Research-Prompts — Vorlagen für KI-Recherchen"
type: research
date: 2026-09-06
status: final
tags: [ssh, ebpf, redis, gvisor, mesh]
license: CC-BY-4.0
---

# Research-Prompts — Vorlagen für KI-Recherchen

> Zweck: Recherche-Prompts, die sich bewährt haben — kopieren, in Gemini/Web-KI
> einfügen, Ergebnis zurückschicken. Die Ergebnisse werden sortiert in
> `docs/research/` (wie R1–R19), mit Korrekturen und offenen Fragen.
> Erstellt nach dem R19-Durchlauf (LLM-Firewall-Recherche), dessen Korrektur-
> bedürftigkeit diese Regeln hergeleitet hat.

## Workflow (so landen Ergebnisse im Research-Folder)

1. **Prompt kopieren:** Basisblock + gewünschter Themablock zusammen einfügen.
2. **Ergebnis zurückgeben:** Ganze Ausgabe inkl. Quellen-URLs einreichen (Chat).
3. **Sortierung (Claude):** Neues `R<n>-<topic>.md` mit Kopf
   (`Quelle` / `Status` / `⚠️ unverifiziert`), Abgleich gegen Sprints und
   `PRODUCT-ROADMAP.md`, Korrektur-Abschnitt, offene Fragen als `O-R<n>-*`.
4. **Index:** Zeile in der Research-Tabelle von `backlog (internal)`,
   Querverweise in Sprint-/Roadmap-Docs setzen.

## Namens- und Formatkonvention (bestehend)

* Datei: `docs/research/R<n>-<topic>.md`, Nummerierung läuft weiter ab **R20**.
* `DECISIONS.md` ist nur für **live verifizierte** Entscheidungen (mit API-Test),
  nicht für Recherchen.
* Ergebnis ohne belegbare URLs → im R-Doc pauschal als `[UNVERIFIZIERT]` behandeln.

## Basisblock (an jeden Prompt voranstellen)

```
Du recherchierst für ein technisches Architektur-Dokument. Regeln für deine Antwort:

1. Jede behauptete Tatsache bekommt eine Quelle: URL + Datum. Keine Behauptung ohne Beleg.
2. Was du nicht verifizieren konntest, kennzeichnest du explizit: [UNVERIFIZIERT].
3. Erfinde nichts: keine Paper-IDs, keine Release-Daten, keine Übernahmen, keine
   Zuordnungen ("gehört zu X"), die du nicht belegen kannst. Unsicher → UNSICHER
   schreiben statt raten.
4. Zu jedem Ansatz: der stärkste Gegenargument/Kritikpunkt und die harten technischen
   Grenzen. Kein Ansatz ist nur vorteilhaft.
5. Mechanismen als Datenfluss beschreiben: Wo liegt der Klartext, wer hält Keys/Symbole,
   welcher Prozess entscheidet, was passiert bei Ausfall. Keine Marketing-Sätze.
6. Nenne explizit, was NICHT existiert oder woran Ansätze gescheitert sind —
   negative Ergebnisse sind wertvoll.
7. Vergleiche in einer Tabelle: Name | Typ | Lizenz | Self-Hosting möglich |
   Status (production/beta/nur Paper/eingestellt) | letztes Release (Datum, Quelle) |
   Kernlimitation.
8. Schließe mit 3–5 offenen Fragen, die deine Recherche NICHT beantworten konnte.
9. Antworte auf Deutsch, Fachbegriffe auf Englisch. Keine Einleitung, keine
   Abschlussfrage ("Möchtest du...?") — nur die Recherche selbst.
```

---

## P1 — LLM-Firewall-Anbieter verifizieren

*Schließt R19 O-R1 (TigerGate, Portkey/Palo Alto, Lakera/Check Point, K8s Agent Sandbox).*

```
THEMA: LLM-Firewall-/Guardrail-Anbieter verifizieren (Stand heute)

Prüfe zu jedem dieser Punkte den aktuellen Status, mit Beleg-URL je Antwort:
1. TigerGate: existiert ein kommerzielles Produkt "Runtime AI Gateway powered by
   eBPF"? Wer steckt dahinter, Status, dokumentierte Kunden, Pricing.
2. Portkey: gehört Portkey zu Palo Alto Networks oder ist es unabhängig? Seit wann,
   welche Primärquelle?
3. Lakera: Übernahme durch Check Point — Datum, Produktweiterführung von Lakera Guard.
4. Kubernetes: gibt es ein SIG-Projekt "Agent Sandbox" (Kata-basiert)? Offizielles
   Repo, Reifegrad, SIG.
5. Prompt Security: Produktstatus, Shadow-AI-Discovery wie beschrieben?
6. Cloudflare "Firewall for AI": nutzt es Llama Guard — welches Modell, welche Phasen
   (Prompt/Response), Verfügbarkeitsstatus.
7. Falls existent, ein Satz je Anbieter: Lasso Security, Pillar Security, Zenity,
   Aim Security.

Abschließend: welche der Klassen (Gateway-Proxy, In-Process-Scanner, kommerzielle
Plattform, Edge/Netzwerk, Kernel/Runtime) ist am stärksten gewachsen, woran erkennst
du das (Funding, Release-Rhythmus, Stellenanzeigen)?
```

## P2 — eBPF an der TLS-Grenze

*Schließt R19 O-R2 (uprobe-Feasibility; blind spot: Go-Binaries).*

```
THEMA: Klartext-Abgriff von LLM-Traffic per eBPF-uprobes — Machbarkeit und Grenzen

Kontext: Ein Go-Backend (kein Kubernetes) auf einem Linux-Host soll LLM-Traffic von
Docker-Containern abgreifen — ohne Proxy im Agenten, ohne Code-Änderung im Container.

Recherchiere:
1. AgentSight (Boundary Tracing, uprobes an SSL_write/SSL_read): Repo, Paper
   (Datum, DOI/URL), wie reassembliert der Userspace-Daemon die Fragmente?
2. Kommerzielle "eBPF AI Gateways" (z. B. TigerGate): was ist öffentlich dokumentiert
   über ihren Abgriffsmechanismus?
3. Go-Binaries: crypto/tls hat keine C-Symbole — welche Ansätze existieren (Go-ABI-
   uprobes, SSLKEYLOGFILE, eBPF an write/read statt SSL_*)? Stand der Technik vs.
   Forschung?
4. Node.js/Electron (OpenSSL/BoringSSL): wie brüchig ist Symbol-Anheftung an
   SSL_write über Versionen in der Praxis?
5. Alternative Hebel: HTTPS_PROXY-Env im Container, iptables-REDIRECT mit TLS-
   Terminierung und substituierter CA, lokaler Egress-Proxy (Envoy) — Latenz- und
   Wartungsvergleich gegen den uprobe-Weg.
6. eBPF-Limits: maximale Stringlänge pro uprobe-Aufruf, Ring-Buffer-Größen,
   Verlustverhalten bei Hochlast.

Ergebnis als Entscheidungsvorlage: wann lohnt uprobe, wann ein lokaler Egress-Proxy,
wann beides — mit Zahlen (Latenz, Overhead) und je stärkstem Gegenargument.
```

## P3 — Injection-Klassifikator-Kaskade

*Schließt R19 O-R3; konkretisiert Sprint 20 E1/E2/WP2.*

```
THEMA: Prompt-Injection-Klassifikatoren — Latenz, Qualität, Betrieb ohne CGO

Kontext: Go-Gateway mit CGO_ENABLED=0. Scanner-Kaskade: Regex (<1 ms) → heuristisch
→ Modell im Sidecar (Rust/C++ oder Python). Nichts im Hot Path über ~20 ms.

Recherchiere mit Benchmark-Zahlen (Quelle + Datum je Zahl):
1. Meta Llama Prompt Guard 2 (22M/86M): echte Latenz auf CPU, ONNX-Interoperabilität,
   False-Positive-Rate auf welchen Benchmarks?
2. Llama Guard 3/4: Größenklasse, Latenz, warum es für den Hot Path ausscheidet.
3. Embedding + klassisches ML (XGBoost/Random Forest, z. B. malicious-prompt-detection):
   Accuracy/FP-Rate, Latenz, Robustheit gegen adaptive Attacken?
4. NeMo Guardrails, Guardrails AI, LLM Guard (Protect AI): was davon läuft als
   Sidecar in Rust/C++/Python, was ist fest in Python?
5. ONNX Runtime aus Go ohne CGO: welche Bindings funktionieren real (onnx-go,
   Prozessgrenze, gRPC-Sidecar)?
6. Injection-Benchmarks (Gandalf, PolygloT, Doppelgänger, Red-Teaming-Sets):
   welches Modell schneidet wo ab — Tabelle.

Ergebnis: empfohlene Kaskade mit Latenzbudget pro Stufe und je stärkstem Gegenargument.
```

## P4 — Cloud-Transport-Schicht

*Schließt Roadmap §6 O1/O2 (IAP, SSM, Chisel, SSH-CA-Bootstrap).*

```
THEMA: SSH-Zugang zu Cloud-VMs ohne öffentlichen Port — IAP, SSM, Chisel, Overlay-Netze

Kontext: Ein Management-Server (Go, x/crypto/ssh) verwaltet Nodes per SSH (Exec,
Port-Forwarding, Tunneling). Ziel: kein offenes :22 auf Cloud-Nodes; der Verbindungs-
aufbau soll hinter einem Transport-Interface austauschbar sein.

Recherchiere mit Latenz-/Overhead-Zahlen (Quelle je Zahl):
1. GCP IAP TCP Forwarding: exakter Datenfluss (WebSocket zur Google-API, Relay
   35.235.240.0/20), IAM-Rollen im Detail, Bandbreitenlimits, Latenz ggü. direktem
   SSH, gcloud-Kommando vs. eigene WebSocket-Implementierung.
2. AWS SSM Session Manager Port Forwarding: ohne sshd? Welche Komponente terminiert
   was (session-manager-plugin), Datenfluss, IAM-Bedingungen, Limits (Sitzungsdauer,
   Bandbreite), Latenz.
3. Chisel: Multiplexing-Verhalten, TCP-over-TCP-Meltdown — real gemessen oder nur
   theoretisch? YAMUX/QUIC-Varianten.
4. Tailscale/Headscale als SSH-Transport (inkl. Tailscale SSH): passt das in ein
   Multi-Tenant-Produkt, Lizenz, Kontrolle über die Identity-Schicht.
5. SSH user certificates statt Host-Key-Pinning: Bootstrap-Muster per cloud-init,
   Principals-Verwaltung, Rotation, Praxisberichte aus großen Flotten.

Ergebnis: Empfehlungsmatrix je Provider (GCP/AWS/Hetzner/BYO-Box) mit erstem Schritt,
Ausbaustufe und was niemals gemacht werden sollte.
```

## P5 — Workspace-Sandbox-Zahlen

*Speist Sprint 20 WP7/E6 (gVisor/`runsc`, Degradationsverhalten).*

```
THEMA: gVisor (runsc) vs. Kata vs. Firecracker vs. runc — gemessene Overheads für
agentische Workloads

Recherchiere echte Messungen (Quelle + Datum, keine Marketing-Zahlen):
1. Syscall-Overhead gVisor Systrap vs. KVM-Plattform: neueste Zahlen, getrennt nach
   I/O-lastig und CPU-lastig.
2. Startzeiten: runsc, Kata (VM-Boot), Firecracker MicroVM.
3. Netzwerk: gVisor Netstack-Durchsatz vs. Host-Stack; Muster "--network=none +
   Egress-Proxy".
4. Kompatibilitätsprobleme in der Praxis: was bricht unter runsc (Docker-in-Docker,
   Dev-Server, Playwright/Browser-Automation)?
5. Kata ohne Nested-Virtualization: welche Provider liefern /dev/kvm in normalen VMs
   (Hetzner? AWS nur *.metal? GCP nested-virt-Flag)?
6. Wer betreibt LLM-Agenten in gVisor/Kata in Produktion (E2B, Modal, Fly Machines,
   Architektur-Berichte zu Code-Interpreter-Systemen)?

Ergebnis: Entscheidungstabelle "Workspace je Task": Sicherheitsstufe, Startzeit,
Overhead, Kompatibilitätsrisiko.
```

## P6 — IODD / IO-Link

*Externer Fachbereich (Beispiel aus dem TMG-TE-Faden); demonstriert die Vorlage für
fremde Domänen.*

```
THEMA: IO-Link-Gerätebeschreibungen (IODD) programmatisch verarbeiten

Kontext: Ein Web-Dashboard soll IODD-Dateien (XML) von Herstellerseiten wie tmgte.de
laden, parsen und als Device-Dokumentation rendern.

Recherchiere:
1. IODD-Spezifikation: aktuelle Version, Schema-Struktur (ProcessData, Parameters,
   Diagnosis), Lizenz der Spezifikation.
2. Bezugsquellen: IODD-Finder (ioddfinder.io-link.com) — gibt es maschinellen Zugang
   (API, Downloads) oder nur Browser-Download?
3. Existierende Parser/Interpreter: IODD-Interpreter (Java?), Python-/JS-Bibliotheken,
   was ist open source?
4. Rendering-Referenzen: wer rendert IODDs als Web-UI (Herstellerportale, IODD-Checker)?
5. Lizenzfalle: dürfen Hersteller-IODDs in ein Produkt eingebettet/weitergezeigt werden?

Ergebnis: realistischer Implementierungspfad "IODD-Link einfügen → geparste
Device-Doku im Dashboard", mit dem größten rechtlichen und dem größten technischen Risiko.
```

## P7 — Agenten-Angriffsfläche im Trading

*Produktrelevant (Trading-Bots, Coin-Deployments); speist K-LAF-Threat-Modelle.*

```
THEMA: Prompt Injection auf autonome KI-/Trading-Agenten — dokumentierte Fälle und
Abwehrmuster

Recherchiere mit Belegen:
1. Dokumentierte Incidents: Agenten, die über eingehende Daten manipuliert wurden
   (Token-Namen, Webinhalte, Repo-Dateien) — welche Fälle sind öffentlich belegt
   (Datum, Quelle), welche nur Gerücht?
2. Forschung: indirect prompt injection über On-Chain-Felder (Solana-Memo, Token-
   Metadaten, DEX-Listing-Daten) — Studien oder Demonstrationen?
3. Abwehrmuster: strukturierte Tool-Ausgabe statt Freitext, Allowlist pro Agent-Rolle,
   Budget-/Signature-Gating, Human-in-the-loop-Schwellen für Transaktionen — was davon
   ist in Produkten realisiert und wie?
4. Post-Mortem-Praxis: welche Spuren speichern Teams bei Agenten-Incidents (Prompt,
   Tool-Calls, Syscalls) und wie lange?

Ergebnis: drei konkrete Abwehrregeln, die in ein Deployment-Template einbaubar sind —
je mit stärkstem Gegenargument.
```

## P8 — CDC für JiMesh: Debezium vs. direkte WAL-Replikation

*Neues Utility-Ebenen-Mandat (Datenbank-Discovery, -Management & CDC); Vorläufer:
Sprint 8, Roadmap §8, Referenz: `docs/reference/debezium/`.*

```
THEMA: Change Data Capture für JiMesh — Debezium (Kafka Connect), Debezium Server,
direkte WAL-Replikation

Kontext: Go-Gateway (CGO_ENABLED=0), Postgres via pgx v5. Die Utility-Ebene
verwaltet Projekte per Docker+SSH. CDC soll Events/Audit/Sync speisen; Kafka soll
NICHT im Default-Stack laufen.

Recherchiere mit Zahlen (Quelle + Datum je Zahl):
1. Debezium (Kafka Connect) vs. Debezium Server (standalone): RAM/Startzeit,
   verfügbare Sinks (Redis, HTTP, Pulsar, Kinesis), Connector-Abdeckung.
2. Debezium Embedded Engine: aktueller Status (deprecated?), ohne Kafka betreibbar?
3. Direkte WAL-Replikation aus Go (pglogrepl/jackc): Reifegrad, Slot-Verwaltung,
   Lag-Monitoring — und was Debezium übernimmt, das man dann selbst bauen muss
   (Schema-Evolution, Typ-Mapping, Initial-Snapshot, Offset-Store).
4. Postgres-Grundlagen: wal_level=logical, max_replication_slots, minimale Rechte
   (REPLICATION), Slot-Leck-Risiko (WAL wächst bis die Disk voll ist), replica
   identity für UPDATE/DELETE-Events.
5. Multi-Tenant-Muster: ein Connector pro Tenant-DB vs. pro Instanz — Limits
   (walsender, Slots), Praxiserfahrungen.
6. Alternativen je eine Zeile: wal2json, PGLogical, Flink CDC, Airbyte, GoldenGate.

Ergebnis: Empfehlung für JiMesh — was in den Default-Compose-Stack kommt, was
opt-in Addon pro Projekt wird, was nie; je mit stärkstem Gegenargument.
```

---

## Nach dem Einfügen eines Ergebnisses (Checkliste für die Sortierung)

- [ ] R-Doc angelegt? Kopf mit `Quelle`/`Status`/`⚠️` gesetzt?
- [ ] Abgleich gegen Sprints + `PRODUCT-ROADMAP.md`: was ist neu, was schon entschieden?
- [ ] Korrekturen der Quelle explizit ins R-Doc (Beispiel R19: BPFJailer-Zuordnung,
      „Apalachee", LiteLLM „Go/Python").
- [ ] Offene Fragen als `O-R<n>-*` notiert — und in den Prompt der nächsten Runde
      übernommen (P1–P7 oben sind genau so entstanden).
- [ ] BACKLOG-Research-Tabelle ergänzt, Querverweise in Sprint-/Roadmap-Docs gesetzt.

---

## Prompts aus dem saits-Repo-Review (6.9.2026, TASK-006)

Schließen die im Review gesammelten offenen Fragen (→ TASK-006 §4, R21 §6).
Basisblock-Regeln gelten unverändert (Quelle+Datum je Claim, Korrekturen markieren,
Vergleichstabelle, 3–5 offene Fragen, Deutsch).

### P-R1 — Policy-Engine-Entscheid für das Go-Gateway
Frage: Casbin-Go (inline, keyMatch2-Policies) vs. OPA-Sidecar (REST/gRPC, Rego) vs.
Gateway-eigene Middleware — für JiMesh §2 Access Policy (HTTP-Header-Claims,
Redis-Streams-Analogie zu MQTT-Topic-ACLs, kaskadierende Scopes VOR dem Budget-Check).
Vergleiche: Enforcement-Flächen, Latenz (p99), Policy-Format + Versionierung,
Testbarkeit, Betriebslast auf einer Einzel-VM. Empfehlung mit Begründung.
Quellen: DAP `acl.md` (Casbin 3-Layer-Stack), saits-cloud (OPA `/iam/decide` + opa-cache).

### P-R2 — Persistente Agent-Memory: Letta vs. Mem0 vs. CrewAI-Memory vs. pgvector-native
Frage: Interfaces (save/search/summarize), Token-Kosten pro Abruf, Multi-Agent-Isolation
(per-agent Namensraum), Self-Edit-Risiken, Write-back mit quality_score. Empfehlung für
Epic 18 Memory-Layer (dynamische Backstory-Injektion). Quellen: DAP `crew-memory.md` /
`rag.md` (SurrealMemoryBackend), st-2 `skill_doc.py` (Two-Tier-Memory).

### P-R3 — DPoP-Replay-Guard-Referenz (Redis-JTI-Window)
Frage: Redis `SET NX EX` vs. EVALSHA (Lua) vs. Redis-7-Functions; Clock-Skew-Fenster
(±30 s), TTL-Bounds (1..600 s, fail-closed), Speicher-Bounding (peak QPS × TTL),
Verhalten bei Replica-Failover (Race). Empfehlung für WP1.
Quellen: `dpop-jti-dedup.lua` + RFC 9449 §4.3.
