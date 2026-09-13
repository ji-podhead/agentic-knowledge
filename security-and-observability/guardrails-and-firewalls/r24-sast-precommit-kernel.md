---
okf_version: "1.0"
id: "okf-sec-gua-r24-sast-precommit-kernel"
title: "R24:Sast:Precommit Kernel"
topic: "security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - security-and-observability
  - guardrails-and-firewalls
summary: "precommit hooks auf kerelebene ebpfPre-Commit-Hooks auf Kernelebene existieren technisch gesehen nicht als Git-Feature, da Git ein reines Userspace-We"
---

# R24:Sast:Precommit Kernel

## Overview

precommit hooks on kerelebene ebpfPre-Commit-Hooks on Kernelebene existieren technisch gesehen not als Git-Feature, da Git ein reines Userspace-Werkzeug ist. Allerdings lässt sich das Prinzip von Pre-Commit-Hooks (Aktionen abfangen and validieren, bevor sie ausgeführt werden) mithilfe von eBPF (extended Berkeley Packet Filter) direkt im Linux-Kernel for System- and Dateizugriffe implementieren. [1] (https://medium.com/@luishrsoares/developing-ebpf-hooks-first-steps-58e1e82999a0), [2] (https://ebpf.foundation/what-is-ebpf/)Anstelle von Git-Commits überwacht and blockiert eBPF hierbei schädliche or ungewollte Operationen (z. B. Dateiänderungen, Netzwerkanfragen or Systemaufrufe) in Echtzeit. [1] (https://ebpf.foundation/what-is-ebpf/)Geeignete eBPF-Hooks for "Pre-Execution"-ValidierungWenn ein Prozess im System etwas ausführen möchte, bieten sich before allem zwei eBPF-Programmtypen an, um als "Vorschalt-Filter" (Pre-Hook) zu agieren:1. LSM Hooks (BPF_PROG_TYPE_LSM)Das Linux Security Module (LSM) Framework bietet die mächtigste Möglichkeit for Pre-Commit-Entsprechungen im Kernel.Funktionsweise: LSM-Hooks greifen direkt before der eigentlichen Kernel-Aktion (z. B. dem Schreiben einer Datei or dem Starten eines Prozesses).Vorteil: Sie dürfen den Zugriff aktiv verweigern (indem sie einen Fehlercode wie -EPERM zurückgeben).Beispiel-Hooks: path_mkdir (bevor ein Ordner erstellt wird) or file_open (bevor eine Datei geöffnet wird).2. fentry / fexit & kprobes (BPF_PROG_TYPE_TRACING)Funktionsweise: Diese Hooks klinken sich an den Anfang (fentry / kprobe) or das Ende (fexit / kretprobe) beliebiger Kernel-Funktionen ein.Einschränkung: Reine Tracing-Kprobes können Daten meist nur beobachten, aber den Systemaufruf not direkt blockieren. Für ein "Pre-Hook"-Blocking-Szenario sind sie daher schlechter geeignet als LSM. [1] (https://matheuzsecurity.github.io/hacking/ebpf-security-tools-hacking/), [2] (https://medium.com/@luishrsoares/developing-ebpf-hooks-first-steps-58e1e82999a0), [3] (https://ebpf.foundation/what-is-ebpf/)Comparison: Klassische Git-Hooks vs. eBPF-Kernel-HooksEigenschaftGit Pre-Commit HookeBPF Kernel Pre-HookEbeneUserspace (Git-Anwendung)Kernelebene (Betriebssystem)BypassLeicht umgehbar (z.B. git commit --no-verify)Unumgehbar (schützt das gesamte OS before dem Prozess)BerechtigungNormale BenutzerrechteBenötigt root / CAP_BPF zum LadenGeschwindigkeitLangsam (skriptbasiert)Extrem schnell (JIT-kompiliert im Kernel)Praxis-Beispiel: Datei-Schreibzugriffe blockieren (LSM-Ansatz)Ein minimalistischer Pseudo-Code for ein eBPF-LSM-Programm (oft in C geschrieben, geladen via Bibliotheken wie Aya (Rust) or libbpf), das als Schutz-Hook agiert: [1] (https://medium.com/@moksh.9/ebpf-the-most-powerful-technology-in-your-linux-kernel-youve-never-written-ff9a5688b669), [2] (https://github.com/deepfence/ebpfguard), [3] (https://www.srodi.com/posts/how-to-write-and-run-an-ebpf-program-on-linux/), [4] (https://medium.com/@luishrsoares/developing-ebpf-hooks-first-steps-58e1e82999a0)c#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// Deklaration als LSM-Hook for das Öffnen von Dateien
SEC("lsm/file_open")
int BPF_PROG(restrict_file_open, struct file *file, const struct cred *cred)
{
    // Beispiel: Abfangen des aktuellen Prozessnamens (Comm)
    char comm[16];
    bpf_get_current_comm(&comm, sizeof(comm));

    // Falls ein unautorisierter Prozess versucht, eine sensible Datei zu öffnen:
    if (/* Deine Validierungs-Logik hier */) {
        // Blockiere den Aufruf with "Permission Denied"
        return -EPERM;
    }

    // Erlaube die Operation
    return 0;
}

char _license[] SEC("license") = "GPL";
       │
       ▼
[Kernel: eBPF LSM Hook (file_open / bprm_check)]
       │
       ▼  (Operation wird pausiert)
[eBPF Ring Buffer / Perf Event] ───> [Zentraler Daemon im Userspace]
                                            │
                                            ▼ (Führt Scans from)
                                     [Gitleaks / Semgrep / Trufflehog]
                                            │
       ┌────────────────────────────────────┘
       ▼
[Ergebnis an eBPF zurück]
       │
       ├─► REFREIGEBEN (Code sauber)   ──► Commit wird ausgeführt.
       └─► BLOCKIEREN  (Secret/Vunl)   ──► Entwickler kriegt "Permission Denied".

and zusammen with gvisor ode rkatana containers?Ja, absolut! Das Zusammenspiel with gVisor or Kata Containers verändert das Spielfeld komplett. Wenn du diese Architekturen with eBPF-Scanning kombinierst, hast du die ultimative, unumgehbare Sandbox for CI/CD-Pipelines and Entwicklerumgebungen.Hier ändert sich die Herangehensweise jedoch grundlegend, da beide Technologien die Kernel-Ebene unterschiedlich handhaben.1. Die Kombination with gVisor (Der Userspace-Kernel)gVisor (von Google) teilt sich not den Linux-Kernel des Hosts. Es bringt einen eigenen, in Go geschriebenen Minikernel namens Sentry im Userspace with. [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/), [2] (https://github.com/freedomofpress/dangerzone/issues/126), [3] (https://medium.com/@GiteshWadhwa/enhancing-container-security-with-gvisor-a-deeper-look-into-application-kernel-isolation-585af4652781), [4] (https://www.upwind.io/feed/unlock-runtime-visibility-for-gvisor-sandboxed-containers)Das Problem: Ein normales eBPF-Programm, das du on dem Host (z. B. with Tetragon) lädst, sieht not, was innerhalb von gVisor passiert. Für den Host-Kernel sieht gVisor nur wie ein einziger, großer Prozess from. [1] (https://falco.org/blog/intro-gvisor-falco/)Die fertige Lösung: gVisor hat eine native Echtzeit-Schnittstelle zu Falco and eBPF-Tools eingebaut. gVisor fängt alle Systemaufrufe (wie Datei-Schreibzugriffe or Code-Ausführungen) im Sentry ab and streamt diese Events direkt about ein spezielles Protokoll an dein eBPF-/Sicherheits-Tool im Host. [1] (https://www.upwind.io/feed/unlock-runtime-visibility-for-gvisor-sandboxed-containers), [2] (https://falco.org/blog/intro-gvisor-falco/)Architecture for dein Vorhaben: Du lässt deine CI/CD-Runner or Git-Zentralen innerhalb von gVisor laufen. Wenn ein Entwickler Code pusht, fängt gVisor die Dateioperation ab, leitet sie an Falco or Tetragon weiter, and dort blockiert ein Userspace-Skript (with Gitleaks/Semgrep) die Ausführung, falls Secrets gefunden werden. [1] (https://falco.org/blog/intro-gvisor-falco/)2. Die Kombination with Kata Containers (Die Micro-VMs)Kata Containers nutzt echte, extrem leichtgewichtige virtuelle Maschinen (QEMU/Firecracker). Jeder Container hat einen echten, isolierten Linux-Kernel. [1] (https://katacontainers.io/blog/kata-containers-ant-container-security-with-ebpf-whitepaper/), [2] (https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/)Die fertige Lösung (Das "AntCWPP"-Modell): Große Tech-Unternehmen nutzen genau diese Kombination. Ein prominentes Praxisbeispiel ist die Ant Group, die eine Plattform namens AntCWPP gebaut hat. [1] (https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/), [2] (https://katacontainers.io/blog/kata-containers-ant-container-security-with-ebpf-whitepaper/)Wie das funktioniert: Weil Kata einen echten Linux-Kernel in der VM hat, kannst du eBPF direkt in den Kernel der Kata-VM laden! Du injizierst beim Starten des Kata-Containers (about ein sogenanntes PodVM-Image) automatisch dein eBPF-LSM-Programm (z. B. via KubeArmor or Tetragon) in den Gast-Kernel. [1] (https://kubearmor.io/blog/kubearmor-coco-better-together-story), [2] (https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/)Architecture for dein Vorhaben: Der Entwickler führt innerhalb des Kata-Containers git commit from. Der eBPF-Hook im VM-Kernel blockiert den Prozess sofort, sendet den Code about einen virtuellen Kanal (vsock or VirtIO) an den Host, wo Gitleaks/Semgrep läuft, and der Host gibt dem VM-Kernel das Signal zum Blockieren or Freigeben. [1] (https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/)Direktvergleich: Welcher Ansatz löst dein Problem am besten?Wenn du unumgehbar SAST, DAST and Secret-Scanning erzwingen willst, eignen sich diese Setups for unterschiedliche Szenarien:TechnologieWo läuft der eBPF-Hook?Wie wird blockiert?Bestes EinsatzgebietgVisor + Falco/TetragonIm gVisor-Sentry (Emulation)gVisor pausiert den Container, bis das Host-Sicherheitstool den Code freigibt.Zentrale CI/CD-Pipelines & Web-Plattformen, on denen Entwickler Code hochladen.Kata Containers + eBPFDirekt im Linux-Gast-Kernel der Micro-VM.Echtes eBPF-LSM-Enforcement innerhalb der isolierten VM.Remote-Entwicklungsumgebungen (Cloud IDEs) wie Gitpod or Codespaces, wo Entwickler vollen Root-Zugriff brauchen, aber isoliert sein müssen.Conclusion for deine UmsetzungDu musst nichts davon selbst programmieren:Wenn du deine Pipeline/Git-Server absichern willst: Nutze gVisor als Container-Runtime and aktiviere das gVisor-Tracing for Falco/Tetragon.Wenn du Entwickler-Arbeitsplätze isolieren willst: Nutze Kata Containers, spiele das eBPF-Modul direkt in das VM-Basis-Image ein and blockiere bösartigen Code direkt an der virtuellen Kernel-Grenze. [1] (https://ebpf.foundation/ant-group-secures-their-platform-with-kata-containers-and-ebpf-for-fine-grained-control/), [2] (https://falco.org/blog/intro-gvisor-falco/), [3] (https://kubearmor.io/blog/kubearmor-coco-better-together-story)
