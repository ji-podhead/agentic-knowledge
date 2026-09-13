---
okf_version: "1.0"
id: "okf-con-ter-r28-vnc-alternative"
title: "OpenCode Abhängigkeiten und ein gutes Terminal installieren"
topic: "container-and-runtime-security"
subtopic: "terminal-workspaces"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - container-and-runtime-security
  - terminal-workspaces
summary: "alternative zu vnc um interactive shells wie opencode die mouse input supporten im web denyamisch nutzbar zu machenFür die dynamische Nutzung interakt"
---

# OpenCode Abhängigkeiten and ein gutes Terminal installieren

## Overview

RUN apt-get update && apt-get install -y \
    openbox \
    xfce4-terminal \
    curl \
    && curl -fsSL https://opencode.ai/install | bash \
    && rm -rf /var/lib/apt/lists/*

# Openbox so konfigurieren, dass es das Terminal maximiert startet
COPY openbox-rc.xml /etc/xdg/openbox/rc.xml

# n.eko anweisen, das Terminal als Hauptanwendung zu nutzen
ENV NEKO_COMMAND="xfce4-terminal --drop-down --fullscreen -e 'opencode'"
OPENCODE_SERVER_PASSWORD=mein_sicheres_passwort opencode web --port 8080

welche interativen shells die fast sind nciht wie vnc gibt es denn noch?Wenn Sie die Trägheit and den massiven Overhead von VNC/grafischen Oberflächen komplett vermeiden wollen, gibt es moderne Terminal-Streaming-Technologien, die on Text- and ANSI-Sequenzen basieren.Da Sie eine Go-Anwendung with einem interaktiven Terminal-UI (TUI) wie OpenCode steuern möchten, ist das Weiterleiten von Maus-Events essenziell. Jedes Mal, wenn Sie im Browser on ein TUI-Element klicken or scrollen, muss das Web-Interface diesen Klick in ein ANSI-Protokoll-Event übersetzen (z. B. \x1b[M...) and an das Go-Programm senden. [1] (https://shuntksh.com/blog/202506/modern-terminal-app-with-mouse-support/)Folgende Alternativen sind extrem schnell, ressourcenschonend (perfekt for den gVisor-Netstack) and bieten nativen Maus-Support:1. ttyd (Der plattformübergreifende Go/C-Standard)ttyd ist ein extrem schlankes C-Tool, das jedes CLI-Programm or jede Shell direkt about WebSockets in den Browser streamt. Es nutzt im Frontend xterm.js, was die treibende Kraft hinter VS Codes integriertem Terminal ist. [1] (https://github.com/xtermjs/xterm.js/)Geschwindigkeit: Nahezu nativ, da nur rohe Text- and ANSI-Daten übertragen werden (no Bildkompression wie at VNC or n.eko).Maus-Support: Vollständig. Es leitet Klicks, Hover-Zustände, Drag-Aktionen and das Mausrad eins zu eins an das TUI weiter.gVisor-Vorteil: Läuft about einen einzigen TCP-Port (HTTP/WebSocket) and verbraucht fast null CPU im gVisor-Userspace-Kernel.Befehl for Ihren Docker-Container:bashttyd -p 8080 opencode
