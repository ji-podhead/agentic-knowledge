---
okf_version: "1.0"
id: "okf-con-san-tetragon-gvisor-kata-comparison"
title: "R25 — Tetragon + gVisor / Kata Containers: Verification & Einordnung for Milestone"
topic: "general/container-runtime-security"
subtopic: "sandboxing"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - container-runtime-security
  - sandboxing
summary: "> Source: System Administrator-Research (8.9.2026, KI-Antworttext) + own Verification per"
---

# R25 — Tetragon + gVisor / Kata Containers: Verification & Einordnung for Milestone

> Source: System Administrator-Research (8.9.2026, KI-Antworttext) + own Verification per
> Websuche am 8.9.2026. Sortiert gegen `Milestone.md`,
> `K-LAF-ARCHITECTURE.md` §5 (Isolationsmodell), §8b (Jailer/Tetragon).
> Status: Research, Corrections vermerkt. Re-verify prior to production deployment.
> Primärquellen prüfen.

---

## 1. Was verifiziert ist

### Tetragon (Cilium) — real, non-K8s nutzbar

* eBPF-basierte Security-Observability **and** Runtime-Enforcement (in-kernel
  Filter + Aktionen bis SIGKILL). TracingPolicies als YAML — funktionieren auch
  **without Kubernetes** via `--tracing-policy`-Flags bzw. `tetra` gRPC-CLI
  (https://tetragon.io/docs/concepts/tracing-policy/).
* Einordnung gegen unsere Frage (Pre-Commit-Guard): Tetragon triggert
  kprobes/tracepoints/uprobes im **Host-Kernel**. LSM-Hook-Support
  (BPF-LSM-Enforcement à la AntCWPP) ist not der Kern; Enforcement läuft
  about Hook-Aktionen (Sigkill/Override), not about `security_*`-LSM-Programme.
* **Aber:** K-LAF §8b bleibt korrekt — Tetragon ist die fertige
  Beobachtungs-/Policy-Maschine, wenn wir not rohes `cilium/ebpf` bauen
  wollen. Decision bleibt E-S2 (Milestone), jetzt with besserer Datenlage.

### gVisor trace points (seccheck) — real, aber **nur Beobachtung**

* gVisor hat eingebaute **Runtime Monitoring**-Trace-Points (alle Syscalls +
  Container-Events), gestreamt about einen **UDS/Remote-Sink** (protobuf) an
  einen externen Prozess — offiziell dokumentiert:
  https://gvisor.dev/docs/user_guide/runtimemonitoring/ and
  https://gvisor.dev/docs/tutorials/falco/ (Falco-Integration, seit ~0.33/2022).
* Das Sentry-User-Kernel-Modell stimmt: 1 Sentry-Prozess pro Sandbox; from
  Host-Kernel-Sicht ist die Sandbox **ein Prozess**. Host-eBPF (Tetragon & Co.)
  sieht deshalb nur die Syscalls des Sentry — grob korreliert, without
  In-Sandbox-Attribution (welcher `git`-Prozess im Sandbox-Inneren).
* Kommerzielles Muster: Upwind streamt gVisor-Trace-Points in denselben
  Event-Pfad wie eBPF-Events (https://docs.upwind.io/public/getting-started/install-sensor/kubernetes/advanced-features/gvisor-support).

### Kata Containers + eBPF im Gast-Kernel (AntCWPP) — real, produktionsreif

* **Ant Group AntCWPP**: Whitepaper (Juli 2025,
  https://katacontainers.io/collateral/kata-containers-ant-group-cwpp-ebpf_whitepaper.pdf)
  + eBPF-Foundation-Case-Study (Oktober 2025,
  https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/).
  Produktionsstabiler Betrieb, inkl. **AI-Agent-Workloads**.
* Muster: Node-Security-Agent lädt eBPF-Programme **in den Kernel der
  Kata-VM** („veBPF-Kanal"), Policies in eBPF-Maps; Enforcement an
  **LSM-Hooks im Gast-Kernel** (`security_inode_permission`, inode→Policy-Map)
  plus execve-Tracepoints, Netz- and FIM-Kontrolle.
* Relevanz for uns: Das ist der Beweis, dass „Pre-Commit-Guard **in** der
  isolierten Umgebung" not nur Theorie ist — aber unter einer
  Kata-ähnlichen VM-Kernel-Architektur, not unter gVisor.

## 2. Corrections am Source Specification (wichtig)

* ❌ **„gVisor pausiert den Container, bis das Host-Tool freigibt"** — not
  belegt. gVisor Runtime Monitoring ist laut Doku **Beobachtung/Threat
  Detection**, die Falco-Integration alarmiert nur. Ein synchroner
  Block-until-Verdict-Fluss about den UDS-Sink existiert in der Dokumentation
  not. Enforcement *innerhalb* von gVisor müsste gVisor-own Mechanismen
  nutzen (not eBPF, not externes Verdict). Für Milestone heißt das:
  **T2 (gVisor) hat keinen echten Kernel-Pre-Commit-Block** — dort gilt
  Variante (c) async remediation (Event → Worktree-Reset + Freeze-Leiter) or
  die Hooks-Fallback-Stufe (Work Package).
* ❌ **„gVisor + Tetragon" als fertige Kombination with Blocking** — no
  offizielle Integration gefunden. Tetragon sieht on dem Host nur den
  Sentry-Prozess (siehe oben). Die Vergleichstabelle im Quelltext ist
  Marketing-nah, not Dokumentations-nah.
* ⚠️ **Kata braucht Nested Virtualization** in Cloud-VMs — steht schon in
  K-LAF §5. Zusätzlich entschied K-LAF for T3 **KVM/libvirt statt eines
  zweiten Container-Runtime-Stacks**. Kata wäre ein *alternativer* T3-Runtime-Pfad
  with dem AntCWPP-Vorteil (eigener Gast-Kernel → eBPF im Gast), no Ersatz
  der bestehenden Decision. Neu bewerten nur, wenn T3-Enterprise tatsächlich
  gebaut wird.

## 3. Konsequenz: Enforcement-Matrix pro Isolationstier (Milestone)

| Tier (K-LAF §5) | Kernel-Sicht | Pre-Commit-Enforcement | Mechanismus |
|---|---|---|---|
| T1 rootless Docker | Host-Kernel, no BPF-LSM garantiert | ❌ nur Best-Effort | Work Package-Fallback (globale Git-Hooks) |
| T1+ Host with BPF-LSM | Host-Kernel, LSM verfügbar | ✅ echtes Kernel-Blocking | Work Package: eBPF-LSM am Host-Kernel (cilium/ebpf or Tetragon, E-S2) |
| T2 gVisor | Sandbox without echten Kernel; Host sieht nur Sentry | ⚠️ no Sync-Block möglich | seccheck-Trace-Points → eigener Sink (Beobachtung) + async Remediation (Freeze-Leiter) |
| T3 KVM/libvirt | echter Kernel pro VM | ✅ realistisch, AntCWPP-Muster | eBPF-LSM **im Gast-Kernel**, Agent↔Host-Kanal (vsock-Muster) — Enterprise-Pfad, später |

**Ein echtes „eBPF + gVisor + Kata" Alles-Könner gibt es not — pro Tier ist
der Mechanismus ein anderer.** Das ist selbst Artikelstoff: dieselbe Garantie
(„no Secret landet im Commit") wird pro Isolationsstufe with einem anderen
Werkzeug erzwungen, and nur die Identitätskette macht die Resultate
vergleichbar.

## 4. Sources (verifiziert 8.9.2026)

* Tetragon Tracing Policies (inkl. non-K8s-Loading): https://tetragon.io/docs/concepts/tracing-policy/
* gVisor Runtime Monitoring / seccheck: https://gvisor.dev/docs/user_guide/runtimemonitoring/
* Falco × gVisor (UDS-Sink, protobuf, observe-only): https://falco.org/blog/intro-gvisor-falco/ · https://gvisor.dev/docs/tutorials/falco/
* Upwind gVisor-Support (Trace-Points → Sensor-Pipeline): https://docs.upwind.io/public/getting-started/install-sensor/kubernetes/advanced-features/gvisor-support
* AntCWPP Whitepaper: https://katacontainers.io/collateral/kata-containers-ant-group-cwpp-ebpf_whitepaper.pdf
* AntCWPP Case Study (eBPF Foundation): https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/
* Kata-Blog zur Whitepaper-Veröffentlichung: https://katacontainers.io/blog/kata-containers-ant-container-security-with-ebpf-whitepaper/
