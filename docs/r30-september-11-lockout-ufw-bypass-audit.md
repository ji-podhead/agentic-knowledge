---
id: "R30"
title: "Incident Audit Report: 11. September 2026 (Incident V3)"
type: audit
date: 2026-09-11
status: final
tags: [ssh, docker, ufw, mesh, netfilter]
license: CC-BY-4.0
---

# Incident Audit Report: 11. September 2026 (Incident V3)
**Thema:** Remote SSH Lockout, POSIX Scripting Syntax-Errors & Docker-UFW-Firewall Bypass.
**Speicherpfad:** `docs/research/R30-september-11-lockout-ufw-bypass-audit.md`
**Kategorie:** Security & Architecture Audit (Brutally Honest, Zero Slop)

---

## 🔍 I. Warum umgehen Docker-Container die UFW-Firewall? (Die Iptables-Schwachstelle)

Das schwerwiegendste Problem des heutigen Tages war, dass die Container-Ports (z. B. `1996`) trotz einer aktiven und korrekt konfigurierten **UFW-Firewall** offen im Internet zugänglich waren. Dies ist kein Bug in JiMesh, sondern ein **konzeptionelles Sicherheitsrisiko von Docker auf Linux-Systemen**.

### 1. Der technische Ablauf im Linux-Kernel:
*   Die Firewall **UFW** schreibt ihre Filterregeln standardmäßig in die **`INPUT`**-Kette von Netfilter (`iptables`). Dort blockiert sie eingehenden Datenverkehr von fremden IPs auf Port `1996`.
*   **Docker** verwaltet Container-Netzwerke über Network Address Translation (NAT). Dafür manipuliert Docker die Routingtabellen im Kernel direkt.
*   Docker fügt seine Regeln direkt in die **`PREROUTING`**-Kette der `nat`-Tabelle und in die **`FORWARD`**-Kette der `filter`-Tabelle ein.
*   **Der fatale Bypass:** Wenn ein Netzwerkpaket den Server erreicht, verarbeitet der Linux-Kernel die Ketten in dieser Reihenfolge:
    $$\text{PREROUTING} \rightarrow \text{FORWARD} \rightarrow \text{INPUT}$$
    Da die Docker-NAT-Regeln in der `FORWARD`-Kette ausgewertet werden, **bevor die `INPUT`-Kette der UFW-Firewall überhaupt erreicht wird, umgeht Docker UFW vollständig!**

### 2. Das Ergebnis bei HOST_BIND=0.0.0.0:
Als wir `HOST_BIND` im Backend und in der `docker-compose.yml` auf `0.0.0.0` umgestellt haben (um Iframe-Pfadfehler zu beheben), hat Docker den Port `1996` an alle Schnittstellen des Hosts gebunden.
*   **Die Konsequenz:** Jeder Angreifer aus dem weltweiten Internet konnte über Deine öffentliche Hetzner-IP `http://88.198.67.200:1996` direkt auf das DeepSeek Harness (DSH) zugreifen. Die UFW-Firewall war für diesen Port vollkommen wirkungslos geschaltet.
*   **Die Bestätigung aus dem Incident vom 5. September:** Im Post-Mortem vom 5. September wurde genau dieses Verhalten dokumentiert. Durch das Binden an `0.0.0.0` haben wir heute exakt denselben fatalen Fehler wiederholt!

### 3. Die einzig sichere Behebung:
Ports dürfen in Docker für sensible oder unauthentifizierte Dienste **niemals** auf `0.0.0.0` freigegeben werden. Sie müssen **strikt und unumstößlich an `127.0.0.1` (localhost) gebunden sein** (`-p 127.0.0.1:1996:3080`).
*   Da Loopback (`127.0.0.1`) physikalisch keine Verbindung nach außen zulässt, ist der Port für das Internet und das VPN gesperrt. Der Zugriff geht ausschließlich lokal oder über den verschlüsselten SSH-Tunnel (`ssh -N -L`).

---

## 📋 II. Lückenlose Aufstellung aller heutigen Fehler (The Forensic Audit)

Hier ist die lückenlose und schonungslose Rekonstruktion aller Fehler, die ich heute nacheinander erzeugt und auf Deinem System hinterlassen habe:

### 1. Der Berechtigungs-Lockout (V1, V2 & V3)
*   **Der Trigger:** Das DSH-Projekt hatte fälschlicherweise das Server-Verzeichnis `/root` (Heimatverzeichnis von root) als Workspace konfiguriert.
*   **V1 (Besitzer-Umschreibung):** Das Berechtigungsskript `jimesh_ws_perms` führte rekursiv `chown -R 1000:1000 /root` aus. Dies entzog dem System-User `root` den Besitz von `/root/.ssh`. OpenSSH (`sshd`) verweigerte daraufhin sofort alle Key-Logins für Root, da das Verzeichnis nicht mehr root gehörte.
*   **V2 (Rechte-Aufweichung):** Als Fallback führte das Skript `chmod -R a+rwX /root` aus. Dadurch wurden die Rechte von `/root/.ssh` und `/root/.ssh/authorized_keys` für andere Gruppen lesbar. `sshd` sperrte daraufhin jeglichen Anmeldeversuch hart ab, da der Schlüssel kompromittiert war.
*   **V3 (Extended ACLs):** Die Verwendung von `setfacl` vererbte Lese-/Schreibrechte an den User `1000`. Auch diese erweiterten Berechtigungslisten stufte `sshd` auf Systemordnern als Sicherheitsrisiko ein und blockierte die Key-Authentifizierung vollständig.
*   **Das Ergebnis:** Vollständige SSH-Aussperrung auf Port 22 für Root. Erst das gezielte Löschen aller ACLs (`setfacl -b`) und das Rücksetzen der Besitzer auf `root:root` mit den Rechten `700` / `600` behob den Aussperrungszustand.

### 2. Der POSIX-Chaining Syntaxfehler (Hängende Deployments)
*   **Der Fehler:** Das Go-Backend kettete Shell-Befehle fälschlicherweise mit dem Operator ` && ` aneinander.
*   **Die Ursache:** Durch das Zusammenfügen des gVisor-Aktivierungsblocks (`if/fi`) und der Port-Suche entstand die unzulässige Verkettung:
    `fi && find_free_port() { ... }`
*   **Die Auswirkung:** Dies ist in Bash/sh syntaktisch verboten (man kann keine Funktionsdefinitionen mit `&&` verketten). Die Remote-Shell stürzte sofort mit einem Parser-Fehler ab, noch bevor ein einziger Docker-Befehl ausgeführt wurde. Die SSH-Sitzung hing unendlich, und es wurden keine Container erstellt.

### 3. Das hardcodierte Bridge-Netzwerk (Remote-Fehlschläge)
*   **Der Fehler:** Der Parameter `--network jimesh_jimesh-net` wurde für Remote-Deployments hardcoded übergeben.
*   **Die Ursache:** Dieses Bridge-Netzwerk existiert nur auf Deiner lokalen Docker-Compose-Umgebung (`workstation`), nicht aber auf dem Remote-Server.
*   **Die Auswirkung:** Docker auf dem Remote-Server verweigerte den Start mit `network not found` sofort.

### 4. Der Trailing-Slash-Fehler (Iframe-404)
*   **Der Fehler:** Iframe-Tunnel-URLs wurden mit einem Schrägstrich vor den Query-Parametern generiert (`/1996/?token=...`).
*   **Die Ursache:** Go's Standard-Router ist extrem strikt. Er matcht den Pfad `/1996/` nicht auf die Route `/api/projects/{id}/tunnel/{port}`, was im Browser zu permanenten 404-Fehlern führte.

### 5. Der fehlende WebSocket-Proxy in Vite (Black Screens)
*   **Der Fehler:** Die `vite.config.ts` enthielt keinen `ws: true`-Eintrag für den `/api`-Proxy.
*   **Die Auswirkung:** Statische HTML-Seiten luden, aber der WebSocket-Verbindungsaufbau von GoTTY und DSH wurde von Vite blockiert. Das Iframe lud zwar, blieb aber als schwarzer, leerer Bildschirm hängen, da keine Terminal-Daten übertragen wurden.

---

## 🛡️ III. Ergriffene Sofort-Maßnahmen (Reverted & Gehärtet)

1.  **Revert HOST_BIND:** `HOST_BIND` in `docker-compose.yml` ist wieder starr auf `127.0.0.1` gesetzt. Es gibt keine `0.0.0.0`-Bindings mehr. Alle Container sind physisch abgeriegelt und blockiert.
2.  **Undeploy Cleanup:** Alle Reste der hängenden Container wurden von Deinem Server entfernt, wodurch alle offenen Ports (`1996`) augenblicklich geschlossen und verriegelt wurden.
3.  **Hardened Permission Shield:** Die Funktion `jimesh_ws_perms` in `projects_ssh.go` wurde mit einem Guard ausgestattet. Sie bricht die Ausführung bei `/root` oder `/` sofort ab und fässt `.ssh`-Ordner physisch niemals wieder an.
4.  **Iframe Tunnel-Bypass:** Das fehlerhafte Iframe-Tunnel-Routing im Frontend wurde für Remote-Nodes im Dashboard vollständig entfernt. Das Dashboard zeigt nun einen sicheren **SSH-Tunneling-Assistenten** an, der Dir Deinen exakten lokalen Tunnel-Befehl ausgibt. So bleibt Dein Server dauerhaft abgeriegelt und unberührt.
