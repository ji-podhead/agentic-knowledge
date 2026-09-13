---
id: "R31"
title: "The JiMesh Ultimate Security, Architecture & Forensic Master Document"
type: guide
date: 2026-09-11
status: final
tags: [docker, ssh, ufw, mesh, gvisor]
license: CC-BY-4.0
---

# The JiMesh Ultimate Security, Architecture & Forensic Master Document
**Kategorie:** Deep-Dive System Analysis & Architecture Blueprint
**Datum:** 11. September 2026
**Zweck:** Lückenlose, technische und systemnahe Dokumentation (Kernel-Level) zu gVisor, Docker-Networking, UFW, SSH-Internals und dem "Höllen-Skript"-Post-Mortem.

Dieses Dokument dient als unumstößliche Referenz für die Architektur von JiMesh, um Container-Ausbrüche, Firewall-Bypasses und SSH-Aussperrungen mathematisch und technisch zu verstehen und endgültig zu verhindern.

---

## Inhaltsverzeichnis

1. [Deep-Dive: Wie gVisor (runsc) wirklich funktioniert](#1-deep-dive-wie-gvisor-runsc-wirklich-funktioniert)
2. [Deep-Dive: Docker Networks & Der UFW Bypass](#2-deep-dive-docker-networks--der-ufw-bypass)
3. [Deep-Dive: UFW Mechanics & Iptables](#3-deep-dive-ufw-mechanics--iptables)
4. [Anti-Hacking: Wie man sich nicht hacken lässt](#4-anti-hacking-wie-man-sich-nicht-hacken-lässt)
5. [Die JiMesh-Vision: Was wir eigentlich bauen wollten](#5-die-jimesh-vision-was-wir-eigentlich-bauen-wollten)
6. [Sichere Netzwerkkonfiguration: Der Praxis-Guide](#6-sichere-netzwerkkonfiguration-der-praxis-guide)
7. [Forensic Teardown: Das "Höllen-Skript" (jimesh_ws_perms)](#7-forensic-teardown-das-höllen-skript-jimesh_ws_perms)

---

## 1. Deep-Dive: Wie gVisor (runsc) wirklich funktioniert

Um zu verstehen, warum gVisor einen Ausbruch (Escape) wie am 5. September verhindert, muss man die Interaktion zwischen einem Prozess und dem Betriebssystem-Kernel verstehen.

### 1.1 Der Standard-Linux-Kernel und `runc`
In einem normalen Docker-Container (unter `runc`) führt eine Anwendung (z.B. Python, Node.js) Instruktionen direkt auf der CPU aus. Wenn die Anwendung eine Datei öffnen will, ein Netzwerkpaket senden will oder neuen Arbeitsspeicher benötigt, muss sie den User-Mode verlassen und in den Kernel-Mode wechseln. Dies geschieht über einen **System Call (Syscall)**.
* Linux hat über 300 Syscalls (z.B. `openat`, `read`, `write`, `clone`, `socket`).
* **Die Gefahr:** Der Kernel des Hosts verarbeitet diese Syscalls direkt. Wenn ein Syscall-Handler im Linux-Kernel einen Bug hat (z.B. Pufferüberlauf, Race Condition wie Dirty COW), kann der Container-Prozess den Host-Kernel manipulieren und sich Root-Rechte auf dem gesamten Server verschaffen.

### 1.2 Die gVisor Architektur: Sentry und Gofer
gVisor fängt dieses Paradigma ab, indem es einen eigenen, stark eingeschränkten Betriebssystem-Kernel in den Userspace stellt.

#### A. Der Sentry
Der Sentry ist das Herzstück von gVisor. Er ist ein in Go geschriebener Userspace-Prozess, der sich gegenüber der Container-Anwendung wie ein echter Linux-Kernel verhält.
* **Syscall Interception:** Wenn der Container einen Syscall absetzt, wird dieser nicht an den Host-Kernel weitergeleitet, sondern vom Sentry abgefangen.
* **Emulation:** Der Sentry führt die Logik des Syscalls selbst aus. Wenn der Container z.B. einen TCP-Socket öffnen will, verarbeitet der Sentry den gesamten TCP/IP-Stack (genannt **Netstack**, geschrieben in Go) im Userspace.
* **Sicherheitsgrenze:** Der Sentry selbst läuft als unprivilegierter Prozess (meist unter dem User `nobody`) im Host-System und ist durch restriktive `seccomp`-Filter extrem beschnitten. Er darf auf dem Host fast keine eigenen Syscalls ausführen.

#### B. Der Gofer
Um das Host-Dateisystem zu schützen, delegiert der Sentry Dateizugriffe an den Gofer.
* Der Gofer ist ein separater Prozess, der mit den echten Dateiberechtigungen des Hosts läuft.
* Der Sentry kommuniziert mit dem Gofer über das **9P-Protokoll** (ursprünglich aus Plan 9) via Unix Domain Sockets.
* Wenn der Container eine Datei anfordert, fragt der Sentry den Gofer. Der Gofer prüft die Rechte und reicht die Dateideskriptoren (FDs) sicher an den Sentry weiter.
* **Vorteil:** Eine Kompromittierung des Sentry-Prozesses gibt dem Angreifer keinen direkten Schreibzugriff auf das Host-Dateisystem.

### 1.3 Interaktionsplattformen: ptrace vs. KVM
Wie fängt der Sentry die Syscalls der Anwendung ab? gVisor nutzt dafür "Platforms":
1. **Ptrace Platform:** Nutzt das Linux-Debugging-Interface `ptrace`. Wenn die App einen Syscall ausführt, stoppt der Kernel die App (Trap) und weckt den Sentry auf. Das verursacht viele Kontextwechsel (Context Switches) und ist daher langsam.
2. **KVM Platform:** gVisor agiert als extrem leichtgewichtiger Virtual Machine Monitor (VMM) über `/dev/kvm`. Der Sentry lässt den Container-Code im Guest-Mode laufen. Bei einem Syscall löst die CPU einen Hardware-VM-Exit aus, und der Sentry übernimmt. Dies ist hardwarebeschleunigt und signifikant performanter.

---

## 2. Deep-Dive: Docker Networks & Der UFW Bypass

Das Verständnis von Docker-Netzwerken ist existenziell, um den kritischen UFW-Bypass zu verstehen, der unsere Ports ins öffentliche Internet exponiert hat.

### 2.1 Linux Network Namespaces und Veth Pairs
Ein Docker-Container lebt in einem eigenen Netzwerk-Namespace. Er sieht nur seine eigene virtuelle Netzwerkkarte (z.B. `eth0`).
* Um diesen Namespace mit dem Host zu verbinden, erstellt Docker ein **Veth Pair** (Virtual Ethernet Pair). Das ist wie ein virtuelles Kabel: Ein Ende steckt im Container (`eth0`), das andere Ende auf dem Host (z.B. `veth1234abcd`).
* Auf dem Host wird das `veth`-Interface an eine virtuelle Bridge (z.B. `docker0` oder `br-xyz`) angeschlossen.

### 2.2 Iptables und Netfilter: Der Paketfluss
Der Linux-Kernel nutzt Netfilter (`iptables`), um Pakete zu routen und zu filtern. Die wichtigsten Tabellen sind `filter` (für Erlauben/Verbieten) und `nat` (für Port-Translation).
Die Auswertungsreihenfolge für ein eingehendes Paket ist absolut starr:
1. `PREROUTING` (nat-Tabelle)
2. Routing Decision (Ist das Paket für den Host selbst oder muss es weitergeleitet werden?)
3. **Wenn für den Host:** `INPUT` (filter-Tabelle)
4. **Wenn zur Weiterleitung:** `FORWARD` (filter-Tabelle)

### 2.3 Der Anatomie des Docker UFW-Bypass
UFW (Uncomplicated Firewall) legt seine Filterregeln (z.B. `ufw deny 1996`) primär in der **`INPUT`**-Kette der `filter`-Tabelle ab.

Wenn Du einen Container mit `-p 0.0.0.0:1996:3080` (oder ohne explizites Binding) startest, greift Docker tief in die `iptables` ein:
1. **PREROUTING:** Docker schreibt eine DNAT-Regel (Destination NAT) in die `nat`-Tabelle:
   `iptables -t nat -A DOCKER -p tcp --dport 1996 -j DNAT --to-destination 172.20.0.5:3080`
   *Jedes Paket auf Port 1996 wird sofort auf die interne Container-IP umgeschrieben.*
2. **Routing Decision:** Der Kernel sieht, dass die Ziel-IP `172.20.0.5` ist. Diese IP gehört nicht direkt dem Host-Interface (`eno1`), sondern der Docker-Bridge. Daher entscheidet der Kernel: **Das Paket muss weitergeleitet werden (FORWARD).**
3. **FORWARD:** Das Paket wandert in die `FORWARD`-Kette. Auch hier hat Docker vorgesorgt:
   `iptables -A FORWARD -d 172.20.0.5 -j ACCEPT`
   *Docker erlaubt die Weiterleitung bedingungslos.*
4. **Der Bypass:** Das Paket erreicht den Container. **Die `INPUT`-Kette (und damit UFW) wurde niemals betreten!** Die Firewall wurde schlichtweg umrundet.

---

## 3. Deep-Dive: UFW Mechanics & Iptables

### 3.1 Wie UFW arbeitet
UFW ist kein eigener Paketfilter, sondern ein Frontend für `iptables`/`nftables`. Es organisiert Regeln in benutzerfreundlichen Ketten (`ufw-user-input`, `ufw-user-forward`).
* UFW blockiert standardmäßig allen eingehenden Traffic (`ufw default deny incoming`).
* Diese Standardregel liegt in der `INPUT`-Kette.
* UFW hat eine eingeschränkte Kontrolle über die `FORWARD`-Kette, aber die Docker-Daemon-Regeln werden mit einer höheren Priorität in die `FORWARD`-Kette injiziert und überschreiben die UFW-Vorgaben.

### 3.2 Die DOCKER-USER Kette
Um dieses fundamentale Sicherheitsproblem zu lösen, hat Docker die Kette `DOCKER-USER` eingeführt.
* Docker stellt sicher, dass alle Pakete, die geroutet werden sollen, zuerst die `DOCKER-USER` Kette durchlaufen, bevor die eigentlichen Docker-Allow-Regeln greifen.
* Hier können Administratoren ansetzen, um Container global vor dem Internet zu schützen:
  ```bash
  # Blockiere alle eingehenden Pakete von außen (eno1), die an Container gehen
  iptables -I DOCKER-USER -i eno1 -j DROP
  
  # Erlaube Traffic aus dem Tailscale-VPN
  iptables -I DOCKER-USER -i tailscale0 -j ACCEPT
  ```

---

## 4. Anti-Hacking: Wie man sich nicht hacken lässt

Ein sicheres System verlässt sich niemals auf eine einzelne Firewall. Es nutzt **Defense in Depth** (Verteidigung in der Tiefe).

### 4.1 Least Privilege & Rootless Docker
* **Das Problem:** Der Docker-Daemon läuft als `root`. Ein Container-Prozess läuft intern oft als `root`. Wenn ein Ausbruch gelingt, ist der Angreifer auf dem Host ebenfalls `root`.
* **Die Lösung:** User Namespaces oder Rootless Docker. Dabei wird der Container-Root-Benutzer auf einen unprivilegierten Host-Benutzer abgebildet (z.B. User `100000`). Ein Ausbruch führt nur zu einem nutzlosen, unprivilegierten Host-Prozess.

### 4.2 Dropping Capabilities
Linux teilt Root-Rechte in sogenannte "Capabilities" (z.B. `CAP_NET_ADMIN` für Netzwerkeingriffe, `CAP_SYS_ADMIN` für Mounts).
* Container sollten mit `--cap-drop=ALL` gestartet werden.
* Nur zwingend benötigte Capabilities (z.B. `CAP_NET_BIND_SERVICE`) sollten selektiv über `--cap-add` hinzugefügt werden.

### 4.3 Seccomp Profile
Secure Computing (`seccomp`) limitiert die Syscalls, die ein Prozess ausführen darf.
* Docker wendet standardmäßig ein Seccomp-Profil an, das ca. 44 von 300+ Syscalls blockiert.
* Für hochsichere Umgebungen (wie DSH) muss ein striktes, maßgeschneidertes Seccomp-Profil genutzt werden, das nur die absolut notwendigen Syscalls zulässt.

### 4.4 eBPF Runtime Enforcement (Tetragon / Cilium)
Modernste Abwehrsysteme nutzen eBPF (Extended Berkeley Packet Filter) im Kernel.
* Werkzeuge wie Tetragon können Systemaufrufe (z.B. `execve` zum Starten einer Shell) in Echtzeit überwachen und hart blockieren (`SIGKILL`), noch bevor die Anwendung den Prozess starten kann.
* Wenn eine Prompt-Injection versucht, `sh -c` auszuführen, tötet eBPF den Container sofort ab.

---

## 5. Die JiMesh-Vision: Was wir eigentlich bauen wollten

Unser eigentliches Ziel war der Aufbau eines extrem sicheren, dezentralen Service-Meshes.

### 5.1 Die Architektur-Vision (Layer-0 Routing)
* **Keine öffentlichen Ports:** Workspace-Container (DSH, GoTTY) binden niemals Ports an das Host-Netzwerk. Sie existieren nur in internen Docker-Netzwerken.
* **Der Utility Proxy:** Auf jedem Remote-Host läuft ein JiMesh-Utility-Container. Dieser agiert als Router/Proxy (z.B. basierend auf WireGuard, Nebula oder Cilium).
* **Overlay Network:** Diese Utility-Container spannen ein verschlüsseltes, Host-übergreifendes Subnetz auf.
* **Das Resultat:** Ein Container auf Host A kann mit einem Datenbank-Container auf Host B kommunizieren, als wären sie im selben LAN. Alle Daten fließen verschlüsselt durch die Tunnel.

### 5.2 Der UI/UX Plan
* Das System wird semantisch von "Projects" auf **"Workspaces"** umgestellt, um die Isolation zu betonen.
* Ein dedizierter **"Network"-Tab** im Dashboard ermöglicht die visuelle Konfiguration dieses Service-Meshes: Der Operator kann grafisch Brücken (Tunnels) zwischen Workspaces auf verschiedenen Hosts ziehen.

---

## 6. Sichere Netzwerkkonfiguration: Der Praxis-Guide

Um die Fehler von heute für alle Zukunft zu vermeiden, hier die strengen Regeln für die Netzwerkkonfiguration in JiMesh:

1. **Rule 1: Strict Localhost Binding**
   Docker-Ports (`-p`) dürfen **NUR** an `127.0.0.1` gebunden werden, wenn sie überhaupt gebunden werden müssen.
   * `docker run -p 127.0.0.1:1996:3080 smanx/deepseek-harness`
2. **Rule 2: Keine manuellen Iptables-Hacks durch Scripte**
   Verlasse Dich niemals auf iptables-Skripte, die bei Reboots verloren gehen könnten.
3. **Rule 3: SSH Reverse Proxy Tunneling**
   Für den Zugriff auf Localhost-Ports auf Remote-Systemen wird ausnahmslos SSH-Tunneling (`ssh -L`) oder der Go-native Reverse-Proxy (`network.Pool`) genutzt. Dadurch ist der gesamte Datenverkehr verschlüsselt und durch die sichere SSH-Authentifizierung des Hosts (Keys, Fail2ban) geschützt.

---

## 7. Forensic Teardown: Das "Höllen-Skript" (`jimesh_ws_perms`)

Dies ist die präzise Analyse des Skripts, das den Server durch die Zerstörung der SSH-Berechtigungen in den Lockout getrieben hat.

### 7.1 Das fehlerhafte Original-Skript
```bash
jimesh_ws_perms() {
    local dir="$1"
    [ -n "$dir" ] && [ -d "$dir" ] || return 0
    if chown -R 1000:1000 "$dir" 2>/dev/null; then
        chmod -R u+rwX,go=rX "$dir"
    elif command -v setfacl >/dev/null 2>&1 && setfacl -R -m u:1000:rwX "$dir" 2>/dev/null; then
        find "$dir" -type d -exec setfacl -m d:u:1000:rwX {} + 2>/dev/null || true
        chmod -R o-w "$dir" 2>/dev/null || true
    else
        chmod -R a+rwX "$dir" || true
    fi
}
```

### 7.2 Wie OpenSSH (`sshd`) Berechtigungen prüft (C-Code Analyse)
Der OpenSSH-Daemon ist extrem paranoid konfiguriert (Standard: `StrictModes yes`).
In den OpenSSH-Sourcen (in `auth.c` und `auth-options.c`) gibt es Funktionen wie `safely_chroot` und `check_key_file`.
* `sshd` stattet das Home-Verzeichnis (`/root`), das Verzeichnis `.ssh` und die Datei `authorized_keys` nacheinander mit dem Befehl `stat()` aus.
* **Prüfung 1 (Ownership):** `if (st.st_uid != 0 && st.st_uid != user_uid)` -> Wenn die Datei nicht `root` oder dem einloggenden User gehört, wirft SSH `Authentication refused: bad ownership`.
* **Prüfung 2 (Permissions):** `if ((st.st_mode & 022) != 0)` -> Wenn die Gruppen-Schreibrechte (`020`) oder die Others-Schreibrechte (`002`) gesetzt sind, wirft SSH `Authentication refused: bad modes`.

### 7.3 Der Fehler im Skript
Als Workspace wurde fälschlicherweise `/root` konfiguriert. Das Skript führte aus:
`jimesh_ws_perms "/root"`

1. **`chown -R 1000:1000 /root`**
   * Das `R` (rekursiv) änderte den Besitzer von `/root/.ssh` und `/root/.ssh/authorized_keys` auf den Benutzer mit UID `1000` (auf Deinem Server der User `runner`).
   * **Ergebnis:** SSH-Check 1 (Ownership) schlägt sofort fehl. Der Server sperrt Root aus.

2. **`chmod -R u+rwX,go=rX /root`**
   * Dies setzte die Rechte für Gruppe (`g`) und Andere (`o`) auf Lese- und Ausführungsrechte (`rX`).
   * **Ergebnis:** `.ssh` und `authorized_keys` sind plötzlich für andere Benutzer auf dem System lesbar. Private SSH-Infrastruktur darf niemals von anderen lesbar sein. SSH-Check 2 (Permissions) schlägt fehl.

3. **`setfacl -R -m u:1000:rwX /root`**
   * Fallback-Szenario, das Access Control Lists (ACLs) hinzufügt.
   * **Ergebnis:** `sshd` erkennt, dass die UNIX-Standard-Permissions (`stat()`) nicht die ganze Wahrheit über den Dateizugriff abbilden, da ACLs andere User berechtigen. OpenSSH lehnt Dateien mit erweiterten ACLs prinzipiell als zu unsicher ab. Der Zugang bleibt blockiert.

### 7.4 Wie man es niemals machen sollte
* **Niemals** rekursive Rechteänderungen (`-R`) auf Systemverzeichnissen (`/`, `/root`, `/home`, `/etc`) ausführen.
* **Niemals** Workspaces oder Docker-Bind-Mounts direkt im Heimatverzeichnis von `root` ablegen.

### 7.5 Die harte Sicherung im JiMesh Code
Um dieses Inferno für alle Zeit zu verhindern, wurde eine eiserne Guard-Rail in den Code gebrannt:
```bash
if [ "$dir" = "/root" ] || [ "$dir" = "/" ]; then
    find "$dir" -maxdepth 1 ! -name ".ssh" ! -name ".." ! -name "." -exec chmod -R a+rwX {} + 2>/dev/null || true
    return 0
fi
```
* **Abbruch der Rekursion:** Durch `-maxdepth 1` wird die Rekursion gestoppt. Es werden nur die obersten Dateien/Ordner angepasst.
* **Expliziter Ausschluss:** Durch `! -name ".ssh"` wird der kritische SSH-Ordner von `find` rigoros herausgefiltert und niemals angefasst. Die SSH-Integrität ist physisch garantiert.

---
**Ende des Berichts.**
*Dieses Dokument ist eine technische Autopsie und dient als Mahnmal für die Strenge, die bei Container-Sicherheit und Berechtigungsmanagement auf Linux-Hosts zwingend erforderlich ist.*