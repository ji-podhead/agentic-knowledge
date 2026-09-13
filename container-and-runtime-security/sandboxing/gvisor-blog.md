---
okf_version: "1.0"
id: "okf-con-san-gvisor-blog"
title: "Basics"
topic: "container-and-runtime-security"
subtopic: "sandboxing"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - container-and-runtime-security
  - sandboxing
summary: "Describe gVisor's internal architecture precisely enough that I can draw a correct technical diagram: the exact relationship between the Sentry (the u"
---

# Basics

Describe gVisor's internal architecture precisely enough that I can draw a correct technical diagram: the exact relationship between the Sentry (the userspace kernel), the Gofer (the file-system proxy process), and Netstack (the userspace network stack) — which process intercepts what, which one talks to the host kernel and how (ptrace vs. KVM platform), and where exactly application syscalls get intercepted versus where real host syscalls still happen. I want the accurate box-and-arrow relationship, not a simplified "gVisor is a secure sandbox" summary.

 Hier ist die präzise, technische Architecture von gVisor, aufgeteilt after Prozessen, Sicherheitsgrenzen and Datenströmen, damit du daraus ein exaktes Box-and-Arrow-Diagramm zeichnen kannst.1. Die beteiligten Komponenten (Die Boxen)Für dein Diagramm benötigst du drei primäre Security-Ebenen (von oben after unten):Application Space (Untrusted User Space)gVisor Sandbox Layer (Trusted User Space)Host Kernel Space (Privileged System Space)Komponente A: Die Anwendung (App Process)Ort: Läuft als normaler Linux-Prozess im User Space, ist aber innerhalb der Sandbox eingesperrt.Verhalten: Denkt, sie läuft on einem echten Linux-Kernel. Feuert Standard-Syscalls (z.B. sys_open, sys_socket, sys_read).Komponente B: Der Sentry (Das Herzstück / Der Userspace-Kernel)Ort: Ein separater, in Go geschriebener Prozess im User Space.Rolle: Emuliert die Linux-Kernel-Schnittstelle. Er besitzt die Implementation von about 300 Linux-Syscalls im Speicher.Enthält intern: Netstack. Netstack ist no separater Prozess, sondern eine eingebettete Go-Bibliothek innerhalb des Sentry-Prozesses. Er implementiert den gesamten TCP/IP-Stack (IPv4/v6, TCP, UDP, ARP) in reinem Go-Code.Komponente C: Der Gofer (Der Dateisystem-Proxy)Ort: Ein separater, isolierter Prozess im User Space (einer pro Container).Rolle: Verwaltet den Zugriff on das echte Dateisystem des Hosts. Er agiert als restriktiver Chroot/Seccomp-Wächter. Der Sentry darf das Host-Dateisystem niemals direkt anfassen.Komponente D: Die Plattform (Der Interceptor-Mechanismus)Rolle: Das technische Bindeglied, das Syscalls der Anwendung abfängt. Es gibt zwei austauschbare Backend-Plattformen:Systrap (Standard, ehemals KVM/Ptrace-basiert optimiert): Nutzt standardmäßig Linux ptrace (or moderne, optimierte Stub-Prozesse), um CPU-Instruktionen abzufangen.KVM: Verwandelt den Sentry mithilfe von /dev/kvm in einen schlanken Hypervisor. Die Anwendung läuft quasi als vCPU-Gast (without jedoch ein echtes Betriebssystem-Image zu booten).2. Die Beziehungen and Pfeile (Arrows & Data Flow)Datenstrom 1: Syscall Interception (Das Abfangen)Pfeil: App Process ──[ Feuert Syscall (z.B. open) ]──> Richtung Host Kernel.Die Barriere (Die Plattform): Bevor der Syscall den echten Host-Kernel erreicht, fängt die Plattform (Systrap/KVM) die CPU-Instruktion ab.Pfeil: Plattform ──[ Leitet Syscall um ]──> Sentry.Architecture-Detail: Der Syscall der Anwendung erreicht niemals direkt den Host-Kernel. Er wird im User Space abgefangen and in den Sentry umgelenkt.Datenstrom 2: Dateisystem-Zugriff (Sentry zu Gofer)Der Sentry verarbeitet den Syscall (z.B. open("/etc/passwd")). Da er selbst no Rechte hat, on die Festplatte des Hosts zuzugreifen, muss er den Gofer fragen.Pfeil: Sentry ──[ 9P-Protokoll or Custom IPC via Unix Domain Socket / Pipes ]──> Gofer.Verarbeitung im Gofer: Der Gofer validiert, ob der Container diesen Pfad überhaupt sehen darf.Pfeil: Gofer ──[ Macht echten Host-Syscall open() ]──> Host Kernel.Rückweg: Host Kernel ──[ File Descriptor / Daten ]──> Gofer ──[ IPC ]──> Sentry ──[ Emulierter Return ]──> App Process.Datenstrom 3: Netzwerk-Zugriff (Sentry / Netstack zu Host)Die Anwendung ruft socket() or send().Verarbeitung im Sentry: Der in den Sentry eingebettete Netstack fängt das ab and baut das Paket (SYN, ACK, TCP-Header) komplett im Go-Speicher zusammen. Es verlässt den Sentry bereits als fertiges L2/L3-Paket.Pfeil (Netzwerk-Ausgang): Sentry (Netstack) ──[ Schreibt rohe Ethernet-Frames via AF_PACKET or TUN/TAP ]──> Host Kernel.Echter Host-Syscall: Der Sentry nutzt hierfür meist nur sehr wenige, streng limitierte Host-Syscalls (wie write() on ein TUN-Device or sendmsg()), die about eine extrem restriktive seccomp-Whitelist on Host-Ebene abgesichert sind.3. Logische Struktur for dein DiagrammWenn du das Diagramm zeichnest, ordne die Boxen wie folgt an:text+-----------------------------------------------------------------------+

| LAYER 1: UNTRUSTED USER SPACE (Application)                           |
|   +---------------------------------------------------------------+   |
|   |                      App Process (z.B. Node.js)               |   |
|   +------------------------------+--------------------------------+   |
+----------------------------------|------------------------------------+
                                   | (App feuert Syscall)
================== ABFANG-SCHICHT: PLATFORM (Systrap / KVM) =============
                                   |
                                   v (Umgelenkt in den User Space)
+-----------------------------------------------------------------------+

| LAYER 2: TRUSTED USER SPACE (gVisor Sandbox)                          |
|                                                                       |
|   +-----------------------------------------+   +-----------------+   |
|   | SENTRY (Go Kernel-Emulator)             |   | GOFER           |   |
|   |                                         |   | (FS-Proxy)      |   |
|   |  +-----------------------------------+  |   |                 |   |
|   |  | NETSTACK (Embedded Network-Lib)   |  |   |                 |   |
|   |  +-----------------+-----------------+  |   |                 |   |
|   +--------------------+--------------------+   +--------+--------+   |
|                        | (IPC / 9P)                      |            |
|                        +---------------------------------+            |
|                        | (Nur sichere L3/L4 / FS Calls)  |            |
+------------------------|---------------------------------|------------+
                         v                                 v
+-----------------------------------------------------------------------+

| LAYER 3: PRIVILEGED SYSTEM SPACE (Host OS)                            |
|                                                                       |
|   +---------------------------------------------------------------+   |
|   |                          Host Linux Kernel                    |   |
|   +---------------------------------------------------------------+   |
+-----------------------------------------------------------------------+

---
ür ein lückenloses, hochpräzises Diagramm müssen wir die IPC-Schicht (Inter-Process Communication) zwischen dem Sentry and dem Gofer sowie den Kernel-Stubs abbilden. gVisor nutzt hier no trägen, standardmäßigen Unix-Pipes, sondern eine extrem optimierte Architecture basierend on Shared-Memory-Ringpuffern.Hier sind die genauen technischen Details, wie diese Pfeile in deinem Diagramm beschriftet sein müssen:1. Das Shared-Memory-Konzept (Sentry ⇄ Gofer)Da das serverseitige Auslesen von Dateien (z. B. at jedem read()- or write()-Syscall) about klassische Prozesswechsel (Context Switches) die Performance ruinieren würde, nutzen Sentry and Gofer ein geteiltes Speicherelement.Die Box im Diagramm: Zeichne eine kleine, überlappende Box zwischen Sentry and Gofer namens Shared Memory Ring Buffer (LISFS) (gVisors internes, hochoptimiertes Dateisystem-Protokoll, das das alte 9P-Protokoll weitgehend abgelöst hat).Der Pfeil (Sentry → Ringpuffer): Wenn der Sentry Daten vom Gofer braucht, schreibt er eine Nachricht in diesen Ringpuffer and signalisiert dies about einen atomaren CPU-Befehl (without den Host-Kernel einzubinden).Der Pfeil (Gofer → Sentry): Der Gofer-Prozess pollt diesen Puffer (or wartet on ein Signal), verarbeitet die Dateisystem-Anfrage on dem echten Host and legt das Ergebnis zurück in den Shared Memory.2. Die Systrap-Architecture & Die Stub-ProzesseWenn du dich for die standardmäßige Systrap-Plattform entscheidest (die im Jahr 2026 die performanteste and am häufigsten genutzte Variante in gVisor ist), sieht die Interception-Schicht im Detail so from:Die Boxen: Für jeden CPU-Kern des Hosts existiert ein sogenannter Stub-Prozess. Diese Stubs sind extrem leichtgewichtige Hilfsprozesse im User Space.Der Ablauf beim Abfangen (App → Stub):Wenn die Kunden-App einen Syscall ausführt, fängt die CPU dies ab and springt in die Adressräume des Stubs.Der Stub nutzt ein spezielles Linux-Kernel-Feature (oft via seccomp with dem Flag SECCOMP_RET_TRAP or optimierten ptrace-Erweiterungen), wodurch der Thread der Anwendung sofort schlafen gelegt wird.Der Pfeil (Stub ⇄ Sentry): Der Stub kommuniziert with dem Sentry ebenfalls about einen separaten Shared Memory Queue-Pfeil. Er meldet dem Sentry: „Anwendungsthread X möchte gerade den Syscall Y ausführen.“ Der Sentry übernimmt, emuliert das Ergebnis im Go-Code and weckt den Anwendungsthread about den Stub wieder on.Ergänzung deines Diagramms um die IPC-DetailsIntegriere diese Beschriftungen in die Pfeile deines Box-and-Arrow-Diagramms:text[ Application Process ]
       │
       ▼ (Feuert Syscall)
[ Systrap Stub Process ]
       │
       ▼ [ Pfeil-Label: Shared Memory Queue / Fast Path ]
[ SENTRY (Go-Kernel) ]
       │
       ▼ [ Pfeil-Label: LISFS Protocol via Shared Memory Ring Buffer ]
[ GOFER (FS-Proxy) ]
       │
       ▼ [ Pfeil-Label: Restricted Host Syscalls via seccomp-bpf ]
[ Host Linux Kernel ]
Die Industrie bezeichnet die Kombination from Kernel-Sandbox (gVisor), lokaler Netzwerk-Segmentierung and Identitäts-Routing explizit als „Foundational Security Through Defense in Depth“. Das Kubernetes Agent Sandbox (SIG Apps)-Framework wurde speziell for das sichere Ausführen von unvertrauenswürdigem Code geschaffen and unterstützt gVisor zur Reduzierung der Kernel-Angriffsfläche. For more details, visit GitHub. [1] (https://medium.com/@tahirbalarabe2/kubernetes-agent-sandbox-ai-security-d24978512179), [2] (https://northflank.com/blog/agent-sandbox-on-kubernetes), [3] (https://github.com/kubernetes-sigs/agent-sandbox)
---

▎ Are there any documented real-world platforms or published architectures that combine all three of: (a) a kernel-isolating sandbox runtime per workload (gVisor, Kata Containers, or similar), (b) local network-layer segmentation between tenants on the same host (VLANs or equivalent), and (c) identity-based reverse-proxy routing instead of exposed ports — as three deliberately layered, complementary defenses? I'm looking for named examples or technical blog posts describing this specific three-layer combination, to cite as prior art, not just single-layer examples of each in isolation.
Ja, diese exakte dreistufige Kombination from Kernel-Sandbox, lokaler L2/L3-Netzwerksegmentierung and identitätsbasiertem Proxy-Routing ist die Blaupause for moderne Cloud-Infrastrukturen, die unvertrauenswürdigen Drittanbieter-Code ausführen.Es gibt drei namhafte, hochgradig dokumentierte Plattformarchitekturen, die du als exakten Stand der Technik (Prior Art) for dieses 3-Ebenen-Verteidigungsmodell anführen kannst:1. Das offizielle CNCF / Kubernetes "Agent Sandbox"-Referenzdesign (2026)Das von der Kubernetes Special Interest Group (SIG) veröffentlichte Framework Kubernetes Agent Sandbox Framework wurde speziell for das sichere Ausführen von unvertrauenswürdigem Code (wie AI Agents, LLM-generierten Skripten or interaktiven IDE-Arbeitsbereichen) geschaffen. Die offizielle Dokumentation beschreibt exakt deine kaskadierende Drei-Ebenen-Verteidigung: [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/), [2] (https://rywalker.com/research/container-vm-runtimes)Ebene A (Kernel-Isolierung): Jedes Tenant-Workload (z. B. ein Python-Coding-Agent or eine VS Code-Instanz) wird zwingend in gVisor (runtimeClassName: gvisor) gekapselt. Systemaufrufe (Syscalls) werden im Userspace abgefangen, um den Host-Kernel before Escapes zu schützen. [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/)Ebene B (Lokale Netzwerksegmentierung): Da gVisor in diesem Setup herkömmliches, direktes Pod-Port-Forwarding inkompatibel macht, erzwingt die Architecture eine strikte L2/L3-Segmentierung unterhalb der Pods on Host-Ebene. [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/)Ebene C (Identity-Proxy-Routing): Anstatt rohe Ports after außen zu öffnen, setzt das Framework den Sandbox Router ein. Dies ist ein schlanker, identitätsbasierter Reverse Proxy. Er fängt sämtlichen Datenverkehr am Rand ab and routet Anfragen basierend on Identitätsmerkmalen (about einen dedizierten X-Sandbox-ID-Header) an den internen Port des jeweiligen isolierten Pods weiter. [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/)2. Die Gitpod / Ona Enterprise-ArchitekturDie Entwicklungsplattform Gitpod (Ona) betreibt Millionen paralleler Entwickler-Workspaces on geteilter Cloud-Infrastruktur and dokumentiert dieses komplementäre Sicherheitsmodell transparent in ihren Whitepapers and Architecture-Diagrammen: [1] (https://ona.com/docs/classic/admin/reference/architecture), [2] (https://github.com/gitpod-io/gitpod)Ebene A (Kernel-Isolierung): Jeder gestartete Workspace läuft standardmäßig unter gVisor (runsc), um zu verhindern, dass ein böswilliger Entwickler or ein gehacktes npm-Paket with Root-Rechten im Container den Host-Node kompromittiert.Ebene B (Lokale Netzwerksegmentierung): Gitpod segmentiert die Workspaces on Netzwerkebene unter Verwendung von eBPF-gesteuerten Netzwerkrichtlinien (Cilium) and dedizierten Tunneln. Container verschiedener Tenants on demselben Host können sich untereinander weder pingen, noch deren Sockets scannen.Ebene C (Identity-Proxy-Routing): Die Plattform schließt rohe Ports standardmäßig komplett vom Internet ab. Der Zugriff erfolgt about einen zentralen Ingress-Layer (basierend on Envoy Proxy). Dieser liest die Subdomain (z. B. https://gitpod.io), validiert das Session-Cookie des angemeldeten Nutzers and tunnelt den Datenverkehr erst after erfolgreicher Authentifizierung an das interne Interface des gVisor-Containers. [1] (https://ona.com/docs/classic/admin/getting-started/networking)3. Das Fly.io Produktions-MusterObwohl Fly.io on der untersten Ebene anstelle von gVisor eine andere Sandbox-Technologie verwendet, ist das dortige Zusammenspiel der drei Ebenen das in der Industrie am intensivsten dokumentierte Referenzbeispiel: [1] (https://fly.io/docs/reference/architecture/), [2] (https://fly.io/learn/firecracker-vs-gvisor/)Ebene A (Kernel-Isolierung): Fly.io isoliert Kunden-Workloads in hardware-virtualisierten Firecracker MicroVMs, wodurch jeder Tenant einen eigenen isolierten Gast-Kernel erhält.Ebene B (Lokale Netzwerksegmentierung): Die MicroVMs werden on demselben physischen Bare-Metal-Host about ein striktes, proprietäres Layer-2-Netzwerk (genannt 6PN) komplett voneinander isoliert. Es gibt no direkte lokale Route zwischen den VMs on demselben Server.Ebene C (Identity-Proxy-Routing): Fly.io betreibt on jedem Host den fly-proxy (einen in Rust geschriebenen Edge-Proxy). Dieser Proxy fängt den Traffic ab, übernimmt die TLS-Terminierung and mappt die Verbindungen identitäts- and routingbasiert direkt in die VM. Rohe, ungeschützte Port-Belichtung on dem Host-Server existiert not. [1] (https://fly.io/learn/firecracker-vm/), [2] (https://fly.io/docs/reference/architecture/), [3] (https://fly.io/learn/firecracker-vs-gvisor/), [4] (https://vibe-eval.com/safety/fly-io/)Nutzen for deine DokumentationDieses Drei-Schichten-Modell bildet eine klassische Defense-in-Depth-Kaskade:Falls ein Angreifer die Identitätsprüfung am Proxy (C) überwindet, scheitert er an der Netzwerksegmentierung (B), die ihm den Zugriff on andere Tenants verwehrt. Sollte er auch das Netzwerk manipulieren, schützt die gVisor/MicroVM-Sandbox (A) den zugrunde liegenden physischen Host before einer Übernahme. [1] (https://agent-sandbox.sigs.k8s.io/docs/use-cases/gvisor-isolation/)Wenn du an deiner technischen Spezifikation schreibst, kann ich dir dabei helfen, die formale Begründung (Sicherheitsanalyse) for diese drei Ebenen zu formulieren, um sie Investoren or Auditoren vorzulegen. Wäre das for dich hilfreich?

---

▎ For each of these three isolation layers — kernel-syscall sandboxing (gVisor), local network-layer segmentation (VLANs/macvlan), and identity-based reverse-proxy routing — what is the one thing that specific layer does NOT protect against, that one of the OTHER two layers has to cover instead? I want a precise "if you only had this layer, here's exactly how you'd still get owned" framing for each of the three, so the article can show why all three are needed together rather than any one being sufficient alone.

Hier ist die präzise „If you only had this layer, here’s exactly how you’d still get owned“-Gegenüberstellung for dein Dokument. Sie zeigt mathematisch sauber, warum jedes einzelne Layer isoliert versagt and erst die Kaskade absolute Security bietet.Layer 1: Kernel-Syscall Sandboxing (gVisor)Was es NICHT schützt: Die lokale Netzwerkumgebung (Layer 2/3) and die Anwendungsebene (Layer 7).Wie du with diesem Layer allein untergehst:Szenario: Du betreibst gVisor on einer Standard-Docker-Bridge without VLANs and without auth-geprüften Proxy.Der Exploit: Ein Angreifer startet ein legitimes Projekt on deiner Plattform, öffnet ein Terminal im Container and führt ein einfaches nmap-Scanning on dem lokalen Subnetz from. Da gVisor den Netzwerk-Traffic des Containers als Standard-Ethernet-Frames an den Host übergibt, kann der Angreifer die IPs and offenen Ports aller anderen Kunden-Workspaces on derselben Bridge sehen. Er greift nun about ein ungeschütztes lokales API (z.B. eine offene Redis-Instanz eines anderen Kunden on Port 6379) direkt deren Daten ab.Wer hier rettet: VLANs/macvlan (Layer 2) blockieren das Scannen and den Datenfluss zwischen den Containern komplett; der Reverse-Proxy (Layer 7) verhindert, dass der Angreifer überhaupt unauthentifiziert von außen an diese Ports herankommt.Layer 2: Lokale Netzwerk-Segmentierung (VLANs / macvlan)Was es NICHT schützt: Den Host-Kernel (Layer 0/1) before Privilegieneskalation.Wie du with diesem Layer allein untergehst:Szenario: Du nutzt harte 802.1Q VLANs and isolierst jeden Kunden on Netzwerkeschnittstellen-Ebene, betreibst die Container aber with der Standard-Runtime runc.Der Exploit: Ein Kunde lädt ein bösartiges Skript hoch, das eine Zero-Day-Schwachstelle im echten Linux-Kernel des Hosts ausnutzt (z.B. ein Exploit im Memory-Management or den Namespaces). Da der Container direkt with dem Host-Kernel spricht, bricht der Angreifer from dem Container from (Kernel Escape) and erlangt root-Rechte on dem eigentlichen Blech (dem Host-OS). Von dort from kontrolliert er den gesamten Server, liest alle Festplatten from and hebelt deine mühsam konfigurierten VLANs with einem einzigen ip link-Befehl im Host-OS from.Wer hier rettet: gVisor, indem es den Zugriff on den echten Host-Kernel komplett blockiert and den Exploit in seiner Go-Sandbox verpuffen lässt.Layer 3: Identitätsbasiertes Reverse-Proxy RoutingWas es NICHT schützt: Die Ausführung von unvertrauenswürdigem Code after erfolgreicher Authentifizierung and laterale Bewegungen (Lateral Movement).Wie du with diesem Layer allein untergehst:Szenario: Du hast den sichersten Proxy der Welt. Er prüft JWTs perfekt and lässt Nutzer X nur on die URL von Workspace X. Aber im Workspace läuft unisolierter Code (runc on Standard-Netzwerk).Der Exploit: Nutzer X loggt sich völlig legal in seinen eigenen Workspace ein. Sobald er drin ist, führt er Schadcode from. Da der Proxy nur den eingehenden Verkehr von außen kontrolliert, der Container intern aber ungeschützt on dem Host läuft, nutzt der User die fehlende Kernel-Barriere for einen Escape or greift lateral andere Container on derselben Netzwerkbrücke an. Der Proxy sieht von diesem internen „Ost-West-Traffic“ absolut gar nichts, da er nur am Rand („Nord-Süd“) steht.Wer hier rettet: gVisor (verhindert den Ausbruch from dem eigenen Container) and VLANs (verhindern, dass der legitime Ausbruchversuch on Netzwerkebene andere Mieter erreicht).Die Argumentations-Kette for deinen Artikel:Der Proxy (Layer 7) ist der Türsteher: Er stellt sicher, dass nur berechtigte Personen den Raum betreten. Er weiß aber not, ob der Gast im Raum eine Bombe baut.Die VLANs (Layer 2) sind die schalldichten Wände: Sie sorgen dafür, dass selbst wenn ein Gast im Raum randaliert, die Nachbarn davon nichts mitbekommen and not belästigt werden.gVisor (Layer 0/1) ist die Zwangsjacke: Sie sorgt dafür, dass der Gast im Raum das Gebäude selbst (den physischen Server) not zum Einsturz bringen kann.Möchtest du diese drei prägnanten „Türsteher, Wand, Zwangsjacke“-Metaphern or die genauen Angriffsvektoren (Ost-West vs. Nord-Süd) in einer Einleitung for den Artikel weiter ausformulieren?

---

hole mir gute quellen and example flow charts and bilde rzu den topicsHier sind exzellente, offizielle Quellen, Whitepapers and visuelle Flussdiagramme zu den drei Sicherheitsarchitekturen. Du kannst diese direkt als technische Grundlage (Prior Art) for deine Dokumentation and dein Whitepaper verwenden.1. Offizielle Fachquellen & WhitepapersgVisor Kernel-Isolierung & Netstack:gVisor Architecture Guide (Google / gVisor.dev): Dokumentiert im Detail, wie der integrierte Netstack (Go-Anwendungs-Kernel) rohe Ethernet-Frames liest and den Host-Kernel before direkten Syscalls abschirmt.gVisor Networking Security Blog: Zeigt on, warum gVisor nur bis zu 3 Host-Syscalls benötigt and unvertrauenswürdigen Paketcode isoliert. [1] (https://gvisor.dev/docs/user_guide/networking/), [2] (https://gvisor.dev/docs/architecture_guide/networking/), [3] (https://gvisor.dev/blog/2020/04/02/gvisor-networking-security/)3-Ebenen-Plattform-Kombination (Defense in Depth):Kubernetes Agent Sandbox (SIG Apps): Ein Open-Source-Projekt, das exakt diese 3-Layer-Architecture (gVisor + Netzwerksegmentierung + Identity-basierter Ingress-Router) for AI-Agents and Entwickler-Workspaces standardisiert.Fly.io Architecture Whitepaper: Die Referenz for isoliertes Identity-Proxy-Routing (fly-proxy) in Kombination with harter lokaler Netzwerksegmentierung on Host-Ebene. [1] (https://kubernetes.io/blog/2026/03/20/running-agents-on-kubernetes-with-agent-sandbox/), [2] (https://github.com/kubernetes-sigs/agent-sandbox)2. Visuelles Flussdiagramm: Der Paket-Lebenszyklus(Dieses Flussdiagramm zeigt die Kaskade vom Client-Request bis tief in den sandboxten Go-Kernel von gVisor)text [ NUTZER / CLIENT ]
         │
         │ (1) Request: https://platform.test
         ▼
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 3: IDENTITY-BASED PROXY (Traefik / Envoy)        │
 │                                                        │
 │  • Terminiert TLS                                      │
 │  • Prüft Session-Cookie / JWT (Better Auth)            │
 │  • Extrahiert Port (3000) & AppID (app123)            │
 └─────────────────────────┬──────────────────────────────┘
                           │
                           │ (2) Proxy fügt Header hinzu & routet
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 2: LOCAL NETWORK SEGMENT (VLAN 102 / ipvlan)     │
 │                                                        │
 │  • Isoliert "Ost-West-Traffic" on dem Host            │
 │  • Paket erhält 802.1Q VLAN Tag (vlan.id == 102)       │
 │  • Verhindert IP-Scanning on benachbarte Container    │
 └─────────────────────────┬──────────────────────────────┘
                           │
                           │ (3) Paket erreicht das Container-Interface
                           ▼
 ┌────────────────────────────────────────────────────────┐
 │ LAYER 1: KERNEL-SYSCALL SANDBOX (gVisor Sentry)        │
 │                                                        │
 │  • Systrap-Stub fängt den Netzwerk-Syscall ab          │
 │  • Userspace-Netstack (Go) verarbeitet TCP/IP-Handshake│
 │  • Übergabe an App-Prozess without Host-Kernel-Kontakt     │
 └────────────────────────────────────────────────────────┘

CAPTURED PACKETS:
─────────────────────────────────────────────────────────────────────────────
FRAME 1: Ingress Traffic to App
  -> Ethernet II (Src: Traef42:ac, Dst: gVisor02:42)
  -> 802.1Q Virtual LAN (ID: 102, Priority: 0)                     <-- VLAN TAG!
  -> Internet Protocol Version 4 (Src: 172.18.0.1, Dst: 172.18.0.5)
  -> Transmission Control Protocol (Src Port: 54321, Dst Port: 3000)
Host: 3000-app123.platform.test
X-Forwarded-For: 203.0.113.195
X-Authenticated-User: user_99
X-App-ID: customer-app-123          <-- Identitätsnachweis im HTTP-Stream
Authorization: Bearer eyJhbGciOi...

---

![Diagram showing the MAGI system: three agents running in gVisor, along with a lot of side-services in gVisor-sandboxed containers. Evangelion style.](https://gvisor.dev/assets/images/2026-04-15-magi/magi.png)

Get in the sandbox, Agents.

**Does gVisor work with OpenClaw?** This question has been asked a lot, so let’s answer it here and now: **Yes**.

In this post, we will set up a triple-agent system combining **[OpenClaw](https://openclaw.ai/)**, **[PicoClaw](https://github.com/sipeed/picoclaw)**, and **[Hermes Agent](https://hermes-agent.nousresearch.com/)**, each in separate gVisor sandboxes, all with local inference powered by **[Ollama](https://ollama.com/)** in a gVisor sandbox using three different models, convening together in a self-hosted **[Matrix.org](https://matrix.org/)** server (naturally, also running in a gVisor sandbox). Each agent will be given its own set of capabilities, each of which will be sandboxed. At the end of the day, you will have a fully self-sovereign triple-agent system that can answer queries, browse the web, and cogitate with itself.

**Does this particular setup make practical sense?** *No, but it is cool*. More importantly, it demonstrates the versatility of gVisor at sandboxing basically any component that an agentic system may need. gVisor’s compatibility has grown significantly over the last few years, and agent harnesses fit well within what gVisor is capable of.

Let’s go.

### Basic machine setup: Docker/gVisor/NVIDIA drivers

We will use a `g2-standard-96` GCE VM running stock Ubuntu for this, but any Linux machine with similar GPUs would work. This section describes its basic setup.

Getting a GCE VM:

```shell
$ gcloud compute instances create magi \
    --project=eperot-gke-dev \
    --zone=europe-west1-c \
    --machine-type=g2-standard-96 \
    --maintenance-policy=TERMINATE \
    --accelerator=count=8,type=nvidia-l4 \
    --create-disk=auto-delete=yes,boot=yes,device-name=magi,image=projects/ubuntu-os-cloud/global/images/ubuntu-2404-noble-amd64-v20260316,mode=rw,size=2048,type=pd-ssd
```

We will be using the following ports:

- `8008`: Matrix.org server (Synapse)
- `8084`: Cinny web UI (Matrix.org client)
- `11434`: Ollama (inference API server)
- `18789`: OpenClaw gateway web UI
- `18790`: PicoClaw gateway
- `3002`: Self-hosted Firecrawl

If SSHing into a VM, you can forward some of them for convenient access:

```
-L 8008:127.0.0.1:8008 -L 8084:127.0.0.1:8084 -L 11434:127.0.0.1:11434 -L 18789:127.0.0.1:18789
```

Setting up the GCE VM (once SSH’d as `root`):

```bash
sudo apt-get update && sudo apt-get -y upgrade

# NVIDIA driver
DRIVER_VERSION=590.48.01; \
  sudo apt-get install -y build-essential linux-headers-$(uname -r) && \
  curl -fSsl -O "https://us.download.nvidia.com/tesla/$DRIVER_VERSION/NVIDIA-Linux-x86_64-$DRIVER_VERSION.run" && \
  sudo sh NVIDIA-Linux-x86_64-$DRIVER_VERSION.run && \
  rm NVIDIA-Linux-x86_64-$DRIVER_VERSION.run

# Docker
sudo apt update && \
  sudo apt install -y ca-certificates curl && \
  sudo install -m 0755 -d /etc/apt/keyrings && \
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
  sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update && \
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# NVIDIA container toolkit
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  gnupg2 && \
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg && \
  curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list && \
    sudo apt-get update && \
    export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.19.0-1 && \
    sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

# gVisor
sudo apt-get update && \
  sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg && \
  curl -fsSL https://gvisor.dev/archive.key | sudo gpg --dearmor -o /usr/share/keyrings/gvisor-archive-keyring.gpg && \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gvisor-archive-keyring.gpg] https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list > /dev/null && \
  sudo apt-get update && sudo apt-get install -y runsc && \
  sudo runsc install -- --nvproxy=true --nvproxy-allowed-driver-capabilities=all --net-raw=true --allow-packet-socket-write=true --host-uds=all --debug-log=/tmp/runsc/ && \
  sudo systemctl restart docker
```

Verifying everything works:

```shell
$ nvidia-smi
$ docker run --runtime=runsc --gpus=all --rm ubuntu:latest sh -c 'ls -al /dev/nvidia*'
```

## Self-hosted Matrix.org server + Cinny web frontend setup

![Diagram showing the MAGI system with the 'Synapse' and 'Cinny' containers blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/synapse.blink.gif)

Setting up Synapse and Cinny.

Let’s set up the **Matrix.org server** for communication, and the **Cinny** web client that we humans can use to communicate with it.

```shell
# Generate homeserver.yaml
$ docker run -it --runtime=runsc --rm \
    --mount=type=volume,src=synapse-data,dst=/data \
    -e SYNAPSE_SERVER_NAME=magi \
    -e SYNAPSE_REPORT_STATS=no \
    matrixdotorg/synapse:latest generate

# Run server
$ docker run --detach --runtime=runsc --restart=always --name=synapse \
    --mount=type=volume,src=synapse-data,dst=/data \
    -p 8008:8008 \
    matrixdotorg/synapse:latest

# Create admin user
$ docker exec -it synapse register_new_matrix_user \
    -c /data/homeserver.yaml \
    --user gendo --password yui --admin

# Run cinny (Matrix client)
$ docker run -it --runtime=runsc --restart=always --name=cinny \
    --link=synapse:synapse \
    -p 8084:80 \
    ghcr.io/cinnyapp/cinny:latest

# Access Cinny web UI at http://localhost:8084
# Log in as:
#   Homeserver: http://127.0.0.1:8008
#   Username: gendo
#   Password: yui
```

## Self-hosted inference server: Ollama

![Diagram showing the MAGI system with the 'Ollama' and 'NVIDIA GPU' boxes blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/ollama.blink.gif)

Setting up Ollama for GPU inference.

Setting up **Ollama**, the GPU-enabled inference server and the brain of it all.

```shell
$ docker run --detach --runtime=runsc --restart=always --name=ollama \
    --gpus=all \
    --mount=type=volume,src=ollama-data,dst=/root \
    -p 11434:11434 \
    ollama/ollama:0.20.0

# Pull and load some models.
$ docker exec -it ollama sh -c 'ollama pull qwen3.5:27b-q4_K_M   && ollama run --keepalive=9001h qwen3.5:27b-q4_K_M     Say hello.'
$ docker exec -it ollama sh -c 'ollama pull glm-4.7-flash:q4_K_M && ollama run --keepalive=9001h glm-4.7-flash:q4_K_M   Say hello.'
$ docker exec -it ollama sh -c 'ollama pull gpt-oss:20b          && ollama run --keepalive=9001h gemma4:26b-a4b-it-q8_0 Say hello.'
$ docker exec -it ollama sh -c 'ollama pull gpt-oss:20b          && ollama run --keepalive=9001h nomic-embed-text:137m-v1.5-fp16 ""'

# Make sure they all fit together in VRAM, otherwise you'll get bad performance.
$ docker exec -it ollama ollama ps
NAME                      ID              SIZE     PROCESSOR    CONTEXT    UNTIL
gemma4:26b-a4b-it-q8_0    6bfaf9a8cb37    89 GB    100% GPU     262144     12 months from now
glm-4.7-flash:q4_K_M      d1a8a26252f1    40 GB    100% GPU     202752     12 months from now
qwen3.5:27b-q4_K_M        7653528ba5cb    44 GB    100% GPU     262144     12 months from now
```

## Containerized OpenClaw setup with Browser Use

![Diagram showing the MAGI system with the 'OpenClaw' and 'Chrome' containers blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/openclaw.blink.gif)

Setting up OpenClaw and Chrome browser.

Now let’s set up **OpenClaw** and hook it up to a web browser for fully-local Browser Use.

We will use the official `ghcr.io/openclaw/openclaw` OpenClaw container image, but we will also modify it to install the Google Chrome, as per [recommended in the OpenClaw docs](https://docs.openclaw.ai/tools/browser-linux-troubleshooting#solution-1-install-google-chrome-recommended). This will allow the agent to use a web browser, all running in gVisor.

```shell
$ export MELCHIOR="$HOME/agents/melchior-1"; mkdir -p "$MELCHIOR"
$ cat <<EOF > "$MELCHIOR/Dockerfile"
FROM ghcr.io/openclaw/openclaw:2026.4.2

USER 0:0
RUN export DEBIAN_FRONTEND=noninteractive; apt update -y && \
    apt install -y wget chromium libvulkan1 && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt --fix-broken install -y
EOF

$ docker build -t openclaw:melchior-1 "$MELCHIOR"
```

Note that the resulting image runs as root. This is not a security risk; “root” in a gVisor sandbox doesn’t imply any root-like level access on the host.

Let’s create a Matrix account for it and seed its configuration:

```shell
$ mkdir -p "$MELCHIOR/config" "$MELCHIOR/home"

$ docker exec -it synapse register_new_matrix_user \
    -c /data/homeserver.yaml \
    --user melchior --password akagi --no-admin

$ cat <<EOF > "$MELCHIOR/config/openclaw.json"
{
  "auth": {
    "profiles": {
      "ollama:default": {
        "provider": "ollama",
        "mode": "api_key"
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "ollama/gemma4:26b-a4b-it-q8_0": {}
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "ollama": {
        "baseUrl": "http://ollama:11434",
        "api": "ollama",
        "apiKey": "OLLAMA_API_KEY",
        "models": [
          {
            "id": "gemma4:26b-a4b-it-q8_0",
            "name": "gemma4:26b-a4b-it-q8_0",
            "reasoning": true,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 8192
          }
        ]
      }
    }
  },
  "channels": {
    "matrix": {
      "enabled": true,
      "homeserver": "http://synapse:8008",
      "userId": "@melchior:magi",
      "password": "akagi",
      "deviceName": "Melchior",
      "allowPrivateNetwork": true,
      "encryption": false,
      "groupPolicy": "open",
      "autoJoin": "always",
      "dm": {
        "policy": "open",
        "allowFrom": [
          "*"
        ]
      }
    }
  },
  "gateway": {
    "mode": "local",
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "dangerouslyAllowHostHeaderOriginFallback": true
    }
  },
  "skills": {
    "install": {
      "nodeManager": "npm"
    }
  },
  "browser": {
    "enabled": true,
    "executablePath": "/usr/bin/google-chrome-stable",
    "headless": true,
    "noSandbox": true
  },
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "duckduckgo"
      },
      "fetch": {
        "enabled": true
      }
    }
  },
  "plugins": {
    "entries": {
      "matrix": {
        "enabled": true
      },
      "browser": {
        "enabled": true
      }
    }
  }
}
EOF
```

Note: for the purpose of simplifying demo setup, the above configuration disables authentication, allows the bot to auto-join all Matrix channels it is invited to, etc. For real deployments, do not use these settings.

Let’s run it!

```shell
$ export MELCHIOR="$HOME/agents/melchior-1"; docker run --detach \
    --name=melchior \
    --runtime=runsc \
    --restart=always \
    --env=OPENCLAW_GATEWAY_TOKEN="dummy-token-for-sandbox" \
    --env=OPENCLAW_CONFIG_PATH="/etc/openclaw/openclaw.json" \
    -p 18789:18789 \
    --env=HOME=/home/node \
    --link=synapse:synapse \
    --link=ollama:ollama \
    -v "$MELCHIOR/home":/home/node/.openclaw \
    -v "$MELCHIOR/config":/etc/openclaw \
    openclaw:melchior-1 \
    node \
        dist/index.js \
        gateway \
           --bind=lan \
           --port=18789 \
           --allow-unconfigured \
           --verbose
```

Run `docker exec -it melchior openclaw configure` for further interactive configuration.

You can now go to `http://127.0.0.1:18789/?token=dummy-token-for-sandbox` and talk to your OpenClaw instance!

![The OpenClaw gateway web UI displaying a chat with the dmesg output, confirming that it is running in gVisor.](https://gvisor.dev/assets/images/2026-04-15-magi/openclaw-ui.png)

OpenClaw web UI running in gVisor. The dmesg output is characteristic of gVisor.

### Browser Use

The `Dockerfile` we built earlier contains the Google Chrome web browser, which OpenClaw knows how to use. You can ask it to open websites and take screenshots. Here is the gVisor website rendered in Chrome-in-gVisor by OpenClaw:

![gVisor website rendered by Chrome running in gVisor.](https://gvisor.dev/assets/images/2026-04-15-magi/gvisor-website.png)

gVisor website rendered by Chrome in gVisor, orchestrated by OpenClaw. Funnily enough, the OpenClaw web interface didn't provide the means for OpenClaw to display this image directly. OpenClaw autonomously solved this problem by uploading this picture to a temporary image hosting service and responding with the uploaded image URL.

Now let’s bring the other two brains to life.

## Containerized PicoClaw with web and GitHub skills

![Diagram showing the MAGI system with the 'PicoClaw' container blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/picoclaw.blink.gif)

Setting up PicoClaw.

Moving on to PicoClaw, the minimal agent.

We will use the [PicoClaw Docker image](https://hub.docker.com/r/sipeed/picoclaw), and enable a few skills for GitHub interaction with the [gVisor repository](https://github.com/google/gvisor).

Note that while this demo was on a x86-64 VM, PicoClaw has also been confirmed to work in **gVisor on arm64 on a Raspberry Pi 4 Model B**.

```shell
$ export BALTHASAR="$HOME/agents/balthasar-2"; mkdir -p "$BALTHASAR/picoclaw"
$ docker exec -it synapse register_new_matrix_user \
    -c /data/homeserver.yaml \
    --user balthasar --password ritsuko --no-admin
$ matrix_token="$(curl -X POST -H "Content-Type: application/json" \
    "http://127.0.0.1:8008/_matrix/client/v3/login" \
    -d \
    '{"type": "m.login.password", "user": "balthasar", "password": "ritsuko"}' | \
    jq -r .access_token)"
$ cat <<EOF > "$BALTHASAR/picoclaw/config.json"
{
  "model_list": [
    {
      "model_name": "glm-4.7-flash",
      "model": "ollama/glm-4.7-flash:q4_K_M",
      "api_base": "http://ollama:11434/v1"
    }
  ],
  "agents": {
    "defaults": {
      "model_name": "glm-4.7-flash"
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  },
  "channels": {
    "matrix": {
      "enabled": true,
      "homeserver": "http://synapse:8008",
      "user_id": "@balthasar:magi",
      "access_token": "${matrix_token}",
      "join_on_invite": true,
      "allow_from": []
    }
  }
}
EOF
$ docker run -it \
    --name=balthasar \
    --runtime=runsc \
    --restart=always \
    -v "$BALTHASAR/picoclaw:/root/.picoclaw" \
    --link=synapse:synapse \
    --link=ollama:ollama \
    --entrypoint=/usr/local/bin/picoclaw \
    sipeed/picoclaw:latest gateway
```

PicoClaw should start, although it does not have a lot of functionality out of the box. Let’s enable some skills:

```shell
$ cp "$BALTHASAR/picoclaw/config.json" "$BALTHASAR/picoclaw/config.json.bak" && \
  jq '.tools.web.enabled = true |
      .tools.web.prefer_native = true |
      .tools.exec.enabled = true |
      .tools.exec.allow_remote = true |
      .tools.skills.enabled = true |
      .tools.skills.github = {
        "enabled": true,
        "token": "YOUR_GITHUB_TOKEN_HERE",
        "timeout": 30,
        "max_results": 5
      } |
      .tools.skills.max_concurrent_searches = 5
      | .tools.skills.search_cache = {
        "max_size": 100,
        "ttl_seconds": 300
      } |
      .tools.web_fetch.enabled = true' \
      < "$BALTHASAR/picoclaw/config.json.bak" \
      > "$BALTHASAR/picoclaw/config.json"

# Restart PicoClaw to apply config changes.
$ docker restart balthasar

# You can re-attach to an interactive CLI for PicoClaw with:
$ docker exec -it balthasar picoclaw agent
```

Now we can ask it to interact with GitHub.

![PicoClaw starting up and being tasked with looking up the top trending GitHub repositories that day.](https://gvisor.dev/assets/images/2026-04-15-magi/picoclaw-1.png)

PicoClaw being tasked with looking up the current trending GitHub repositories.

Funnily enough, the top GitHub repository today is Hermes Agent, which we will install next. For now, let’s review a small gVisor PR:

![PicoClaw being tasked with explaining and reviewing a gVisor pull request.](https://gvisor.dev/assets/images/2026-04-15-magi/picoclaw-2.png)

PicoClaw being tasked with explaining and reviewing \[gVisor pull request #12911\](https://github.com/google/gvisor/pull/12911). Which was later reviewed by a human as well.

## Modularized & sandboxed Hermes Agent setup

![Diagram showing the MAGI system with the 'Hermes Agent' container blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/hermes-agent.blink.gif)

Setting up Hermes Agent.

Finally, let’s set up **Hermes Agent**, and fully load it with sandboxed **Browser Use**, sandboxed **web crawling**, and sandboxed **code execution**.

We will use [Hermes Agent’s official Docker image](https://hermes-agent.nousresearch.com/docs/user-guide/docker): `nousresearch/hermes-agent`, expanded with the dependencies needed to perform local text-to-speech and Matrix.org integration, all running in gVisor. Additionally, for extra security, we will do the following:

- Run [Camofox Browser](https://github.com/jo-inc/camofox-browser) in a separate gVisor container, for browser use.
- Run [self-hosted Firecrawl](https://github.com/firecrawl/firecrawl/blob/main/SELF_HOST.md) in a separate gVisor container, for agentic search.
- Run [Docker-in-gVisor](https://gvisor.dev/docs/tutorials/docker-in-gvisor/) in a separate container, for Hermes Agent to execute arbitrary code safely.

Note that the `--net-raw=true --allow-packet-socket-write=true` runsc flags are [required for Docker to work in gVisor](https://gvisor.dev/docs/tutorials/docker-in-gvisor/). For this reason, we need to install a secondary runtime for the Docker-in-gVisor container, and enable host UDS (`--host-uds=all`) so that the Docker daemon socket file can be exported out of that sandbox into the Hermes Agent sandbox.

![Hermes Agent running in gVisor.](https://gvisor.dev/assets/images/2026-04-15-magi/hermes-agent-in-gvisor.png)

Hermes Agent running in gVisor.

### Setting up Docker-in-gVisor for code execution

![Diagram showing the MAGI system with the 'Docker' box blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/docker.blink.gif)

Setting up Docker-in-gVisor for code execution.

**gVisor is capable of [running Docker inside of itself](https://gvisor.dev/docs/tutorials/docker-in-gvisor/)**. Since Hermes Agent has [Docker as a code execution backend](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#docker-backend), we will use this to spawn a separate Docker-in-gVisor container which Hermes Agent can use to run code safely.

```shell
$ export CASPER="$HOME/agents/casper-3"
$ runsc install --runtime=docker-in-gvisor -- --net-raw=true --allow-packet-socket-write=true --host-uds=all

# Reload *host* dockerd configuration to make it notice the new runtime we just added.
$ kill -HUP "$(pidof dockerd)"

# Run Docker-in-gVisor container.
# Note: The \`--cap-add=all\` flag does *not* grant the container any
# capabilities on the host. It only enables the sandboxed workload to use
# elevated privileges **within the sandbox**.
# This is necessary to be able to run \`dockerd\` inside a container.
$ mkdir -p "$CASPER/docker-run"; docker run --detach \
    --name=hermes-exec \
    --runtime=docker-in-gvisor \
    --restart=always \
    --cap-add=all \
    --mount="type=bind,src=$CASPER/docker-run,dst=/var/run" \
    us-central1-docker.pkg.dev/gvisor-presubmit/gvisor-presubmit-images/basic/docker_x86_64

# Verify that we can talk to the \`dockerd\` server running in gVisor.
# We need --security-opt=seccomp=unconfined here, because otherwise
# Docker's default seccomp profile would block the \`syslog(2)\` syscall that
# the \`dmesg\` process uses to read the kernel logs (which here is actually
# reading the gVisor kernel logs). This is not a security problem, since we
# are still all running in gVisor.
$ DOCKER_HOST="unix://$CASPER/docker-run/docker.sock" docker run \
    --rm \
    --security-opt=seccomp=unconfined \
    debian:latest \
    dmesg
# [...]
[    0.000000] Starting gVisor...
[    0.429798] DeFUSEing fork bombs...
[    0.782957] Adversarially training Redcode AI...
# [...]
```

### Building Camofox Docker image in Docker-in-gVisor

![Diagram showing the MAGI system with the 'Camofox' container blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/camofox.blink.gif)

Setting up Camofox Browser.

[Camofox](https://github.com/jo-inc/camofox-browser) is a Firefox-based web browser for agentic browsing. Let’s run it in its own sandboxed container.

Camofox comes with an image that also contains `Xvfb` to simulate an X11 display server, and `yt-dlp` for YouTube video extraction, all working in gVisor. Let’s build it.

The Camofox project doesn’t provide pre-built Docker images, so we need to build it ourselves. But wait! Camofox may or may not be a fishy project. What if it contains malicious code?

**Have no fear, gVisor is here!** We can simply build the image inside gVisor. Let’s spin up an ephemeral Docker-in-gVisor container, run the Camofox Docker image build process within, extract the image out, and import it into the host `dockerd` ’s local image repository.

![I heard you like containers so we put Docker build in Docker in gVisor in Docker.](https://gvisor.dev/assets/images/2026-04-15-magi/turtles.jpg)

It's containers all the way down.

```shell
# Start Docker-in-gVisor with large-enough /var/lib/docker tmpfs
$ mkdir -p /tmp/docker-tmp && docker run --detach \
    --name=docker-tmp \
    --runtime=docker-in-gvisor \
    --restart=always \
    --cap-add=all \
    --mount="type=bind,src=/tmp/docker-tmp,dst=/tmp/docker-tmp" \
    -e DOCKER_TMPFS_SIZE=8G \
    us-central1-docker.pkg.dev/gvisor-presubmit/gvisor-presubmit-images/basic/docker_x86_64

# Build image within the in-gVisor Docker.
# The \`make\` command will run \`docker build\` in-sandbox.
$ docker exec docker-tmp sh -c 'true && \
    apt update -y && \
    apt install -y git build-essential && \
    git clone https://github.com/jo-inc/camofox-browser.git && \
    cd camofox-browser && \
    make'

# Extract the image out of the container and import as host Docker image.
# The \`docker save\` command dumps the image to stdout, which gets piped
# to the out-of-sandbox \`docker load\` command.
$ docker exec docker-tmp docker save camofox-browser | docker load
Loaded image: camofox-browser:135.0.1-x86_64

# You now have the image on the host Docker:
$ docker images | grep camofox
camofox-browser:135.0.1-x86_64      80c072259479      4.6GB      2.27GB

# Clean up.
$ docker rm -f docker-tmp
```

Now that we have our Camofox image, let’s run it:

```shell
$ docker run --detach \
    --name=camofox \
    --runtime=runsc \
    --restart=always \
    camofox-browser:135.0.1-x86_64

# Camofox binds on port 3000 by default; we don't need to expose it
# to the host though, as we will use inter-container networking.
# Nonetheless, let's make sure it works:
$ docker exec -e DEBIAN_FRONTEND=noninteractive camofox sh -c 'true && \
    apt update -y >/dev/null && \
    apt install -y curl jq >/dev/null && \
    tabId="$(curl -q -X POST http://127.0.0.1:3000/tabs -H "Content-Type: application/json" -d "{\"userId\": \"me\", \"sessionKey\": \"task\", \"url\": \"https://gvisor.dev\"}" | jq -r .tabId)" && \
    curl -q --output - "http://127.0.0.1:3000/tabs/${tabId}/screenshot?userId=me"
  ' > /tmp/screenshot.png
$ file /tmp/screenshot.png
/tmp/screenshot.png: PNG image data, 1280 x 720, 8-bit/color RGBA, non-interlaced
```

### Running self-hosted Firecrawl in gVisor

![Diagram showing the MAGI system with the 'Firecrawl', 'Redis', 'RabbitMQ', 'Playwright', and 'PostgreSQL' containers blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/firecrawl.blink.gif)

Setting up the Firecrawl stack.

We will use the [Firecrawl `docker-compose.yaml` template](https://github.com/firecrawl/firecrawl/blob/main/docker-compose.yaml), simply modified to run all containers in gVisor. Because [the way `docker-compose` sets up DNS](https://github.com/google/gvisor/issues/7469) is incompatible with gVisor’s per-container network stack, we need to use pre-assigned IPs rather than container hostnames in the `docker-compose` file.

```shell
$ export CASPER="$HOME/agents/casper-3"; git clone https://github.com/firecrawl/firecrawl.git "$HOME/agents/casper-3/firecrawl"
$ cat <<EOF > "$CASPER/firecrawl/.env"
PORT=3002
HOST=0.0.0.0
OLLAMA_BASE_URL=http://172.17.0.1:11434/api
MODEL_NAME=qwen3.5:27b-q4_K_M
MODEL_EMBEDDING_NAME=nomic-embed-text:137m-v1.5-fp16
BULL_AUTH_KEY=CHANGEME
EOF
$ git apply <<EOF
diff --git a/docker-compose.yaml b/docker-compose.yaml
index 46829cafb..819f9cc87 100644
--- a/docker-compose.yaml
+++ b/docker-compose.yaml
@@ -10,8 +10,6 @@ x-common-service: &common-service
     nofile:
       soft: 65535
       hard: 65535
-  networks:
-    - backend
   extra_hosts:
     - "host.docker.internal:host-gateway"
   logging:
@@ -22,13 +20,13 @@ x-common-service: &common-service
       compress: "true"

 x-common-env: &common-env
-  REDIS_URL: \${REDIS_URL:-redis://redis:6379}
-  REDIS_RATE_LIMIT_URL: \${REDIS_URL:-redis://redis:6379}
-  PLAYWRIGHT_MICROSERVICE_URL: \${PLAYWRIGHT_MICROSERVICE_URL:-http://playwright-service:3000/scrape}
+  REDIS_URL: \${REDIS_URL:-redis://172.16.0.30:6379}
+  REDIS_RATE_LIMIT_URL: \${REDIS_URL:-redis://172.16.0.30:6379}
+  PLAYWRIGHT_MICROSERVICE_URL: \${PLAYWRIGHT_MICROSERVICE_URL:-http://172.16.0.20:3000/scrape}
   POSTGRES_USER: \${POSTGRES_USER:-postgres}
   POSTGRES_PASSWORD: "\${POSTGRES_PASSWORD:-postgres}"
   POSTGRES_DB: \${POSTGRES_DB:-postgres}
-  POSTGRES_HOST: \${POSTGRES_HOST:-nuq-postgres}
+  POSTGRES_HOST: \${POSTGRES_HOST:-172.16.0.50}
   POSTGRES_PORT: \${POSTGRES_PORT:-5432}
   USE_DB_AUTHENTICATION: \${USE_DB_AUTHENTICATION:-false}
   NUM_WORKERS_PER_QUEUE: \${NUM_WORKERS_PER_QUEUE:-8}
@@ -58,6 +56,10 @@ x-common-env: &common-env

 services:
   playwright-service:
+    runtime: "runsc"
+    networks:
+      backend:
+        ipv4_address: 172.16.0.20
     # NOTE: If you don't want to build the service locally,
     # comment out the build: statement and uncomment the image: statement
     # image: ghcr.io/firecrawl/playwright-service:latest
@@ -71,8 +73,6 @@ services:
       BLOCK_MEDIA: \${BLOCK_MEDIA}
       # Configure maximum concurrent pages for Playwright browser instances
       MAX_CONCURRENT_PAGES: \${CRAWL_CONCURRENT_REQUESTS:-10}
-    networks:
-      - backend
     # Resource limits for Docker Compose (not Swarm)
     cpus: 2.0
     mem_limit: 4G
@@ -88,13 +88,17 @@ services:

   api:
     <<: *common-service
+    runtime: "runsc"
+    networks:
+      backend:
+        ipv4_address: 172.16.0.10
     environment:
       <<: *common-env
       HOST: "0.0.0.0"
       PORT: \${INTERNAL_PORT:-3002}
       EXTRACT_WORKER_PORT: \${EXTRACT_WORKER_PORT:-3004}
       WORKER_PORT: \${WORKER_PORT:-3005}
-      NUQ_RABBITMQ_URL: amqp://rabbitmq:5672
+      NUQ_RABBITMQ_URL: amqp://172.16.0.40:5672
       ENV: local
     depends_on:
       redis:
@@ -113,6 +117,7 @@ services:
     memswap_limit: 8G

   redis:
+    runtime: "runsc"
     # NOTE: If you want to use Valkey (open source) instead of Redis (source available),
     # uncomment the Valkey statement and comment out the Redis statement.
     # Using Valkey with Firecrawl is untested and not guaranteed to work. Use with caution.
@@ -120,7 +125,8 @@ services:
     # image: valkey/valkey:alpine

     networks:
-      - backend
+      backend:
+        ipv4_address: 172.16.0.30
     command: redis-server --bind 0.0.0.0
     logging:
       driver: "json-file"
@@ -130,9 +136,11 @@ services:
         compress: "true"

   rabbitmq:
+    runtime: "runsc"
     image: rabbitmq:3-management
     networks:
-      - backend
+      backend:
+        ipv4_address: 172.16.0.40
     command: rabbitmq-server
     healthcheck:
       test: ["CMD", "rabbitmq-diagnostics", "-q", "check_running"]
@@ -148,6 +156,7 @@ services:
         compress: "true"

   nuq-postgres:
+    runtime: "runsc"
     # NOTE: If you don't want to build the image locally,
     # comment out the build: statement and uncomment the image: statement
     # image: ghcr.io/firecrawl/nuq-postgres:latest
@@ -157,7 +166,8 @@ services:
       POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-postgres}
       POSTGRES_DB: \${POSTGRES_DB:-postgres}
     networks:
-      - backend
+      backend:
+        ipv4_address: 172.16.0.50
     logging:
       driver: "json-file"
       options:
@@ -168,3 +178,8 @@ services:
 networks:
   backend:
     driver: bridge
+    ipam:
+      config:
+        - gateway: 172.16.0.1
+          subnet: 172.16.0.0/16
+      driver: default
EOF

# Run.
$ ( cd "$CASPER/firecrawl"; docker compose build && docker compose up )

# Make sure it works:
$ curl -X POST http://localhost:3002/v1/crawl \
    -H 'Content-Type: application/json' \
    -d '{
      "url": "https://firecrawl.dev"
    }'
{"success":true,"id":"019d7a78-e77a-70af-9f49-8e03421dad32","url":"http://localhost:3002/v1/crawl/019d7a78-e77a-70af-9f49-8e03421dad32"}
```

This brings up all the following applications in separate gVisor containers on their own inter-container network:

- **Redis** for key/value storage.
- **RabbitMQ** for message queuing.
- **Playwright** for browser automation.
- **PostgreSQL** for long-term storage.
- **Firecrawl** as main API endpoint for Hermes Agent to interact with.

### Putting it all together

![Diagram showing the MAGI system with the 'Hermes Agent' container blinking.](https://gvisor.dev/assets/images/2026-04-15-magi/hermes-agent.blink.gif)

Setting up Hermes Agent and connecting it.

Let’s put the pieces together for the Hermes Agent container.

```shell
$ export CASPER="$HOME/agents/casper-3"; mkdir -p "$CASPER"

# Register Matrix user.
$ docker exec -it synapse register_new_matrix_user \
    -c /data/homeserver.yaml \
    --user casper --password naoko --no-admin

# Hermes requires a non-root user for its home directory.
$ groupadd --gid=10337 hermes && \
    useradd --home-dir=/dev/null --no-create-home --shell="$(which nologin)" \
      --uid=10337 --gid=10337 hermes

# Build Docker image with extra packages.
$ cat <<EOF > "$CASPER/Dockerfile"
FROM nousresearch/hermes-agent:v2026.4.13

# Install basic packages.
RUN export DEBIAN_FRONTEND=noninteractive; apt update -y && \
    apt install -y sudo wget curl git build-essential python3-pip

# Install dependencies for Hermes Agent's Matrix.org support.
RUN export DEBIAN_FRONTEND=noninteractive; apt update -y && \
    apt install -y libolm-dev && \
    python3 -m pip config set global.break-system-packages true && \
    pip install 'matrix-nio' 'mautrix[encryption]'

# Install espeak-ng and NeuTTS model for local text-to-speech capabilities.
RUN export DEBIAN_FRONTEND=noninteractive; apt update -y && \
    apt install -y espeak-ng && \
    pip install 'neutts[all]'

# Install Docker; not required for dockerd since that's running in a separate
# container, but Hermes Agent still needs the Docker **client** CLI.
RUN export DEBIAN_FRONTEND=noninteractive; apt update -y && \
    apt install -y docker.io
EOF

$ docker build -t hermes-agent:casper-3 "$CASPER"
```

As Hermes Agent does not easily support non-interactive configuration, we need to configure it manually. Let’s run it for interactive configuration purposes:

```shell
$ export CASPER="$HOME/agents/casper-3"; \
    mkdir "$CASPER/home" && chown hermes:hermes "$CASPER/home"
$ docker run -it \
    --name=casper \
    --runtime=runsc \
    --restart=always \
    --shm-size=1g \
    --link=synapse:synapse \
    --link=ollama:ollama \
    --link=camofox:camofox \
    --mount="type=bind,src=$CASPER/home,dst=/opt/data" \
    --mount="type=bind,src=$CASPER/docker-run,dst=/docker-run" \
    -e HERMES_UID="$(id -u hermes)" \
    -e HERMES_GID="$(id -g hermes)" \
    -e DOCKER_HOST="unix:///docker-run/docker.sock" \
    hermes-agent:casper-3 setup
```
<video src="https://gvisor.dev/assets/images/2026-04-15-magi/hermes-agent-setup.webm" controls=""></video>

Going through Hermes Agent's interactive setup process in gVisor.

#### Interactive setup instructions

Expand this section for a text version of the screen recording above.

- Choose `Full setup`
- Inference Provider: `More providers` → `Custom endpoint`
- API base URL: `http://ollama:11434/v1`
- API key: (leave empty)
- Select model: `qwen3.5:27b-q4_K_M`
- Context length in tokens: `262144` (per the [Qwen3.7-27B model card](https://huggingface.co/Qwen/Qwen3.5-27B))
- Select TTS provider: `NeuTTS` (local on-device)
- Terminal Backend: `Docker`
- Docker image: (leave default)
- Container Resource Settings: Up to you
- Max iterations / Tool progress mode/ \[…\] / Inactivity timeout: Up to you
- Select platforms: `Matrix`
- Homeserver URL: `http://synapse:8008`
- Access token: (leave empty)
- User ID: `@casper:magi`
- Password: `naoko`
- Enable end-to-end encryption (E2EE): Up to you
- Allowed user IDs: `@gendo:magi`
- Home room ID: (leave empty)
- Install gateway as systemd service: No, as this isn’t relevant for a containerized install.
- Tools: Feel free to configure.
- Browser provider: `Camofox`
- Camofox server URL: `http://camofox:3000`
- Image generation FAL API key: (leave empty unless you have one)
- TTS provider: Skip
- Search provider: `Self-hosted Firecrawl`
- Firecrawl instance URL: `http://172.17.0.1:3002`

You can verify that Hermes Agent’s “terminal” backend is the Docker-in-gVisor by running `htop` in the `hermes-exec` container.

```shell
$ docker exec -it hermes-exec sh -c 'apt update -y && apt install -y htop'

# Watch this command while asking Hermes Agent to run \`curl https://gvisor.dev\`:
$ docker exec -it hermes-exec htop
```

To make Hermes Agent actually join the Matrix room, you need to restart the container in gateway mode.

```shell
$ docker rm -f casper; docker run --detach \
    --name=casper \
    --runtime=runsc \
    --restart=always \
    --shm-size=1g \
    --link=synapse:synapse \
    --link=ollama:ollama \
    --link=camofox:camofox \
    --mount="type=bind,src=$CASPER/home,dst=/opt/data" \
    --mount="type=bind,src=$CASPER/docker-run,dst=/docker-run" \
    -e DOCKER_HOST="unix:///docker-run/docker.sock" \
    hermes-agent:casper-3 gateway
```

Now invite the bot to your Matrix room and send `/sethome` on the main channel.

You now have Hermes Agent running in gVisor. To recap, Hermes Agent has:

- **Hermes Agent** running in its own gVisor container
- **`dockerd`** running in a separate gVisor container, for subcommand execution
- **Camofox Browser** running with a virtual display (**`Xvfb`**) for browser use, in its own gVisor container
- Self-hosted **Firecrawl** for agentic search, in its own set of gVisor containers.
- **NeuTTS** for text-to-speech capabilities in Hermes Agent, evaluated within gVisor.
- **Ollama** for inference and **Matrix.org** for communication, same as the other agents.

### Putting these agents in a room

You can now ask your 3 agents to do your bidding and get various perspectives.

![All three agents together in a Matrix.org room displayed in the Cinny web UI, with each agent fetching the gVisor homepage and confirming that they are each running in gVisor.](https://gvisor.dev/assets/images/2026-04-15-magi/magi-three-way.png)

The three agents fetching the gVisor homepage and verifying that they are running in gVisor. Note: Hermes Agent cannot call dmesg, due to the default system call filter applied to the Docker container that its code execution tool runs in. However, the 4.4.0 kernel version is characteristic of gVisor.

## Sandboxing agents: What actually makes sense?

The setup described in this blog post is a contrived example of agent sandboxing, where every part of the stack is mutually sandboxed from one another. In closer-to-real-world settings, not all of these components are untrusted, some of them will run remotely, others may be delegated to off-machine APIs, etc. So what would a more practical setup look like?

At a high level, an autonomous agent stack looks like this:

- A **core daemon** (written in good old regular code, e.g. TypeScript for OpenClaw), typically listening on a TCP port. This daemon is responsible for:
	- Receiving user requests via a communications plugin (e.g. Signal, Mattermost…)
		- Running inference API calls
		- Dispatching tool calls
		- Running the control loop necessary to make forward progress on long-term tasks, using inference and tool calls
		- Running cron-like tasks and [heartbeats](https://docs.openclaw.ai/gateway/heartbeat) to keep the agent autonomous
- A pretty **web interface** (sometimes part of the core daemon, sometimes separate)
- A **plugin ecosystem**, adding new tools, communication channels, etc. to the agent
- A database of **skills and general knowledge** (memory) that the agent can evolve over time as they learn from its mistakes, or learn more about their raison d’être and the user they are dealing with.
- A **policy engine** that can decide on the security policies needed for any action the agent would like to take (tool call, API call, credential access, etc.).

When you send a message to such an agent, it ends up running a control loop to handle your query. This control loop will initially run inference, then very likely follow this up by a sequence of tool calls and further inference requests, until a satisfying conclusion is reached. These tool calls can include:

- **Data lookups** on the web
- **API requests** to external services, often requiring sensitive credentials to “act as” the user
- **Browser use**, sometimes with similar credential needs
- **Code snippet** executions
- **Memory** reads and writes, database-like
- **Introspection requests**, where the agent can modify its own configuration or skill database, sometimes fixing its own setup/configuration issues rather than requiring a human to get it unstuck.

Where does sandboxing fit in?

- **Sandboxing individual tools**: Most tool calls don’t do anything fancy. They just make web requests and are not expected to have side-effects. They have no business reading local files or modifying the agent’s own configuration. Sandboxing these tools allows for defense-in-depth.
	- Concrete example: One can craft malicious `.mov` videos which can refer to arbitrary file paths on the host. What if your agent gets tricked into converting a video that tries to embed a subtitle file pointing to `/etc/shadow`? Sandbox your tool calls and avoid this problem.
- **Sandboxing subsystems**: Some agent functionality may depend on long-running daemons which themselves don’t need system-wide access. This can be important for network-exposed or network-accessing subsystems.
	- Concrete example: If using Signal as communications layer, the [`signal-cli` daemon](https://github.com/AsamK/signal-cli) can run in a sandbox for defense-in-depth.
		- Similarly, in the examples above, we sandbox `dockerd` and Camofox browser in separate containers.
- **Sandbox the core daemon**: The need for the agent to be able to **change its own environment** to debug or update itself is a very powerful feature. To do so, the agent requires effectively root control over its own core code and configuration. Therefore, **sandboxing the entire agent’s core daemon** makes sense: the agent can leverage its own intelligence to make itself better, while still being confined to a box. That box is useful because:
	- Destructive changes can be **rolled back**.
		- The agent’s **policy engine can live outside** the core sandbox. This prevents the agent from changing the policy engine’s policies maliciously.
		- Relatedly, sensitive **credentials can live outside** the core sandbox. This ensures that all credential use is mediated through components the agent can’t modify. This includes API keys, crypto wallet keys for agentic commerce, and user-authenticated browser sessions.

*Other parts of the stack typically run fully-trusted code with little to no need for sandboxing. For example, the memory subsystem may be a local vector lookup or similar database, with no internet connectivity and no need to run arbitrary code. Thus, similar to the [gVisor production guide](https://gvisor.dev/docs/user_guide/production/), it does not need to be sandboxed.*

We see some of these ideas being implemented across the ecosystem:

- OpenClaw supports agent-level containerization via [Docker](https://docs.openclaw.ai/install/docker) and [Podman](https://docs.openclaw.ai/install/podman).
- NemoClaw uses [OpenShell](https://github.com/NVIDIA/OpenShell) to ensure tool calls have initially-restricted access which can then be widened as needed by the tool.
- Hermes Agent implements [checkpoints and rollbacks](https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints-and-rollback) to protect against destructive operations.
- [IronClaw](https://www.ironclaw.com/) segregates API keys out of the agent’s core sandbox and injects them at egress time.

Security practices for these tools are rapidly evolving, and gVisor has a role to play.

## Should I use gVisor to sandbox my agent?

gVisor dramatically **reduces the attack surface** for sandbox escapes. It does so by reimplementing a large portion of Linux in userspace, preventing the sandboxed application from attacking the host kernel. Read [more about gVisor’s security architecture](https://gvisor.dev/docs/architecture_guide/intro/).

For autonomous agents, you don’t just need a strong sandbox, you also need **strong policies around *when* and *what* to sandbox**. As a sandboxing technology, gVisor does not help you with these decisions. gVisor only **enhances the level of security of the sandboxing capabilities that the agent already has**. Thus, **gVisor is *necessary*, but not *sufficient***.

gVisor’s capabilities are also uniquely well-suited to agentic workloads:

- Sandboxes **start and stop in milliseconds**, critical to keeping these systems responsive and minimizing time between inference calls.
- Thanks to its process-like model (not a virtual machine), gVisor can achieve **superior density**, i.e. more sandboxes running concurrently on the same host.
- gVisor supports **checkpoint/restore**, making slow-to-initialize repetitive actions quick to replay, and checkpoints/rollbacks can be done seamlessly without sandboxed-workload-specific support.

One current drawback of gVisor is its relative difficulty to integrate within existing applications that have such sandboxing needs. For example, this is one reason why the above demo does not sandbox Hermes Agent tool calls in **separate** gVisor instances. This is being worked on. Watch this space!

![Diagram showing the MAGI system: three agents running in gVisor, along with a lot of side-services in gVisor-sandboxed containers. Evangelion style.](https://gvisor.dev/assets/images/2026-04-15-magi/magi.gif)

\*cogitation intensifies\*
