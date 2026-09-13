---
id: "R23"
title: "R23 — Terminal-Only Deployment, OpenCode, tmux/VNC"
type: research
date: 2026-09-08
status: final
tags: [mesh, ssh, docker, vault, rbac]
license: CC-BY-4.0
---

# R23 — Terminal-Only Deployment, OpenCode, tmux/VNC

## Frage
Braucht JiMesh einen simplen "nur Terminal"-Deployment-Typ, ist "OpenCode" schon
ein echtes Angebot, und was würde tmux+VNC als Deployment-Mechanismus
bedeuten? Zusätzlich: gibt es einen Plan für "Utility-Deployment beim Anlegen
eines neuen SSH-Endpoints"?

---

## 1. Current State

### 1.1 Plain-terminal deployment — does NOT exist as a deploy option

`store.ProjectRow.Framework` (`src/backend/internal/store/store.go:1542`) is a
free-text column whose only real values are enumerated in the comment:
`dsh | opencode | code-server | dsh_code_server | opencode_code_server |
jimesh`. There is no `terminal` (or `ttyd`/`gotty`) case anywhere in the
deploy dispatch switch — `frameworkStartsWorkspace()`
(`src/backend/internal/deploy/projects_ssh.go:182-191`) and the docker-run
branch chain in `executeDeploy()` (same file, ~line 974 onward: `isRuntimePreset`
→ `dsh`/`dsh_code_server` → `opencode`/`opencode_code_server` → `jimesh`)
cover exactly those six values and nothing else.

What *does* exist named "terminal"/"ttyd"/"gotty" is entirely on the
**discovery/classification** side, not deployment:
- `src/backend/internal/network/port_detection.go:38` — `7681: "ttyd"` in
  `KnownPorts`, used to label an already-running service found by scanning a
  node, not to deploy one.
- `src/backend/internal/metadata/ontology.go:207-215` — `ttyd` and `gotty`
  entries under `Category: "Terminals"`, again metadata for classifying
  discovered ports/services (icon, display name).
- `src/backend/internal/store/rbac.go:358-362` — `TypeToCategory` maps both
  `"terminal"` and `"ttyd"` to `"Terminals"` for the app-category
  smart-suggestion feature (Sprint 16 WP5), not for the Framework deploy enum.
- `src/backend/internal/security/exposure.go:169` and
  `exposure_test.go:32,72-74` — the exposure scanner classifies ttyd
  (found on a node) as a remote-execution-capable admin surface for risk
  scoring.

So "terminal" is a recognized *ontology entry* for describing something the
scanner found, but there's no code path that lets a user pick "Terminal" in
the deploy form and get a container. Confirmed by grepping the frontend: the
only `Framework` union in `src/frontend/src/views/ProjectsPage.tsx:30` is the
same six-value list, and the `<select>` options at lines 1239/1242/1504/1507
only offer `opencode`, `opencode_code_server` (plus dsh/code-server variants
elsewhere in the file) — no terminal option in the UI either.

`backlog (internal):120,164,328` records this as a known gap: `ttyd
sidecar (replace custom terminal)` is listed `[ ]` (open) under Epic 5, and
the packages table lists `Terminal | @xterm/xterm + ttyd sidecar | planned`.
Sprint 25's xterm.js work (`sprint docs (internal):14`)
is a **different feature** — it's a rich-text/link-rendering layer for
displaying existing agent log output in the dashboard, not a PTY-over-
WebSocket deploy target. Don't conflate the two.

**Verdict: plain-terminal deploy needs to be built from scratch — nothing
wires it today, though the ontology/category plumbing to *display* one
already exists.**

### 1.2 OpenCode — real and working, but VNC-desktop shaped, not "just a CLI"

`opencode` / `opencode_code_server` are fully wired as Framework values:
- `projects_ssh.go:987-1002` — the actual `docker run` for `opencode`:
  ```
  docker run -d --name jimesh-framework-<id>-<run> -p 127.0.0.1:$ALLOC_VNC:6080 \
    -v <workspace>:/workspace <net/host env> ghcr.io/ji-workstation/opencode-vnc:latest
  ```
- `projects_ssh.go:1238-1239` — deploy-response security note: noVNC on 6080
  has **no known authentication** in that image (no Dockerfile/source in this
  repo to audit), and the SSH tunnel is the *only* protection. This is a
  standing, documented TODO (`TODO(security, noVNC)`, same file lines
  988-998).
- Frontend: `ProjectsPage.tsx:1239/1504` offers "OpenCode (VNC Desktop)" and
  "Combined: OpenCode + VS Code Server"; `vncPort`/`VncPort` plumbing exists
  end-to-end (`store.go:1549`, migration at `store.go:241-242` adding
  `vnc_port` column, request/response fields in `projects_ssh.go:42,83,1411`).
- `providerinfo.go:137`, `gateway.go:2738`, `quota.go:147,198` wire OpenCode
  Zen as an LLM *provider* (API base URL, quota classification) — a separate,
  already-working concern from the container deploy above; both use the same
  name "opencode" but are unrelated code paths.

So today's "OpenCode" deploy option is real, but it is specifically
**OpenCode-inside-a-noVNC-remote-desktop** via a third-party image
(`ghcr.io/ji-workstation/opencode-vnc`) this repo doesn't build or control. It is
not "OpenCode as a terminal-only CLI session" — that's the gap the user is
pointing at, and it's the same gap as 1.1/1.3 (no non-VNC terminal medium
exists to run OpenCode's CLI in).

### 1.3 tmux — no backend/frontend usage at all in this repo

`grep -rni tmux src/backend src/frontend/src docs` returns exactly one hit
outside this new doc: an example Dockerfile snippet inside
`docs/research/R11-port-detection-ssh-tunnel-e2e-deploy.md:213`
(`apt-get install -y curl git tmux nodejs npm`) — a research sketch, never
implemented. There is no tmux session management, no `tmux new-session`/
`send-keys` wiring, nothing.

### 1.4 VNC — wired only for the OpenCode framework, with a known auth gap

`VncPort` is a first-class field on `ProjectRow`/`DeployRequest` (see 1.2),
but VNC as a *mechanism* is only ever attached to the `opencode`/
`opencode_code_server` branch. There is no generic "attach VNC to any
container" path, and the noVNC image's lack of authentication
(`projects_ssh.go:988-998,1239`) is a currently-open security note, not
resolved anywhere in the codebase.

---

## 2. What TASK-005 / R9 already say, and implementation status

### R9 (`docs/research/R9-iframe-cache-http3-terminal-deploy.md`, §6 "Terminal
Deployment Type" and §6 "Layered Deployment Schemas", lines 79-220)

This is squarely the same idea the user is asking about now: a `terminal`
"base medium" (ttyd/gotty *or* xterm.js+WebSocket, ports `[7681]`), layered
with provider "addons" (Claude Code, Aider, jimesh-mesh auto-provision), a
`deployment_schemas` / `deployment_addons` JSONB schema-registry pair, and a
frontend form generator that merges base+addon+user-override schemas. It is
listed only under "Recherche-Aufgaben" checkboxes (unchecked) — there is **no
"Research Results" entry for §6** the way there is for §1-3 (HTTP/3 cache,
icons, composition schema JSON). So this was raised as a question, discussed
at length in an appended AI-chat transcript inside the same file (the R9 doc
file is corrupted/appended with several unrelated multi-thousand-line chat
dumps after line ~220 — worth a cleanup pass separately, flagged here only so
future readers aren't confused by it), but never got a "Research Results
(Operator-Provided)" answer, and:

- **Not implemented.** `deployment_schemas`/`deployment_addons` tables don't
  exist (`grep -rn "deployment_schemas\|deployment_addons" src/` → zero hits
  in code; only referenced in R9 itself and in
  `sprint docs (internal):50` as an open checkbox
  `[ ]`).
- **Superseded in part.** Two later research-audit passes
  (`docs/research/R15-advanced-research-audit.md` §"CUT", item 2, and
  `docs/research/R17-comprehensive-audit.md:28,161`) explicitly revisited the
  "custom xterm.js-to-SSH bridge in Go" idea from R11 and ruled it **CUT /
  overkill**: *"Terminal emulation in Go is months of fragile work... Replace
  with ttyd (or gotty) as sidecar container... E2E deployment starts ttyd
  sidecar, tunnels the port."* This is a standing architectural decision
  already on record — it's mirrored in `backlog (internal):120,328` as
  the still-open `ttyd sidecar` backlog item. **Any terminal-deploy proposal
  should follow this decision (ttyd/sidecar, not a custom Go PTY bridge)
  unless there's a new reason to reopen it.**
- The layered base-medium/addon *schema* idea (deployment_schemas/addons) was
  never revisited by R15/R17 and has no CUT/KEEP verdict — it's simply
  unbuilt, still-open design, not rejected.

### TASK-005 (`task docs (internal)`)

Status: ✅ done (6.9.2026), feeds `R20-jimesh-reuse-review.md`. It is a
structural review of `saits/st-2` and `jimesh-crew` (compose topology,
crew-agent registry/triggers, multi-node/secrets, DB/CDC, legacy debt) — it
does **not** analyze the terminal/tmux/VNC container internals at all (its
scope was compose-level: services, health checks, restart policies, agent
registries, triggers, secrets). Its one VNC-relevant line
(§5 Legacy-Schulden, line 57): *"VNC 6090–6096 ohne Auth — Sprint-19-Erbe;
JiMesh-noVNC hat dasselbe Problem (WP0-KRITISCH) — Muster nicht übernehmen,
Fix läuft in Sprint 19/20."* — i.e. TASK-005 already flagged that
`jimesh-crew`'s per-agent VNC ports have no auth, called out that JiMesh's
own noVNC has the identical gap, and said explicitly **not** to copy that
pattern. It did not go one level deeper into *how* jimesh-crew's VNC
containers are built (Xvfb/x11vnc/websockify/tmux/xterm) — that's new ground
covered in §4 below, and it directly contradicts the "no auth" characterization
for the *mechanism* (the mechanism does support a password; the observed
instances just didn't set one — see §4).

---

## 3. Utility-deployment-on-new-SSH-endpoint — nothing found

Searched:
- `src/backend/internal/deploy/projects_ssh.go` in full — the "node
  registration" surface is really just `DeployRequest.NodeHost/NodeUser/
  NodePort` passed straight into `executeDeploy()`; there is no separate
  "register a node" step, no companion/sidecar spawned once for a *node*
  (only per-*project* sidecars: the socket-guard sidecar and egress-allowlist
  network from TASK-019, which attach to the workspace container being
  deployed, not to the node as a whole — `projects_ssh.go:928-962`).
- `src/backend/internal/network/` (`egress.go`, `hostkey.go`, `mcp_splice.go`,
  `port_detection.go`, `tunnel.go`) — no comment or code referencing a
  companion/utility deploy triggered by SSH-node registration.
- `docs/reference/UTILITY-FLOW.md` — confirmed this is the broader PaaS
  vision (Keycloak login → OPA policy → project creation → deploy →
  Postgres/DB provisioning per *project*, not per SSH node). Its "DB
  PROVISIONIEREN" step provisions a database for a project that declares it
  wants one; it has nothing to do with SSH-endpoint registration specifically.
- `grep -rni "kv_storage\|kv storage\|utility kv"` across `docs/` and
  `src/backend/` — **zero hits.** The "vault direkt die utility kv storage
  gespeichert wird und keycloak und vault auch direkt verknüpft werden" idea
  referenced from an earlier session does not appear anywhere in the current
  doc corpus or code.

**Explicit conclusion: nothing found.** There is no documented or coded
"deploy a companion/utility service automatically when a new SSH-based
project/node is registered" plan anywhere in this repo. This is either from
an undocumented verbal/chat conversation that never got written down, or it
was conflated with UTILITY-FLOW.md's unrelated DB-provisioning-per-project
flow. Recommend writing it down explicitly (a short paragraph in
UTILITY-FLOW.md or a new short doc) the next time the idea comes up in
conversation, specifically distinguishing "per-project utility" (exists,
Sprint 26) from "per-SSH-node utility" (doesn't exist, unclear if wanted).

---

## 4. Findings from saits-crew / jimesh-crew (sibling repos)

TASK-005 already covered compose-level structure; this section goes one
level deeper into the one thing TASK-005 didn't: **how the VNC+terminal
container is actually built**, because it turns out to be close to exactly
what the user is asking about (tmux + VNC as a deployment mechanism).

`/home/ji/projects/jimesh-mirror/jimesh-crew/deploy/claude/` (built by
`docker-compose.yml`'s `crew1..crew7` services, each on its own
`127.0.0.1:609N` noVNC port) contains a working, production-run pattern:

**`Dockerfile`** (`node:20-bookworm-slim` base) installs `xvfb x11vnc
websockify fluxbox xterm ... tmux`, plus noVNC (v1.5.0, vendored via curl)
and the Claude Code CLI.

**`start-vnc.sh`** — the VNC mechanism itself:
```
DISPLAY_NUM=$((NOVNC_PORT - 6079))       # port → display/VNC-port derivation
VNC_PORT=$((5900 + DISPLAY_NUM))
Xvfb :${DISPLAY_NUM} -screen 0 1920x1080x24 &   # virtual framebuffer
fluxbox &                                        # minimal window manager
if [ -z "${VNC_PASSWORD}" ]; then
    echo "ERROR: VNC_PASSWORD is not set — refusing to start unauthenticated VNC" >&2
    exit 1
fi
x11vnc -display :${DISPLAY_NUM} -forever -passwd "${VNC_PASSWORD}" -shared \
  -rfbport $VNC_PORT -listen 127.0.0.1 &
websockify --web /usr/share/novnc "127.0.0.1:${NOVNC_PORT}" "127.0.0.1:${VNC_PORT}" &
```
This **is the fix** for JiMesh's own `TODO(security, noVNC)` in
`projects_ssh.go:988-998`: x11vnc supports a real password
(`-passwd`/`-rfbauth`) and this script hard-fails rather than starting
unauuthenticated. TASK-005's finding that "VNC 6090-6096 ohne Auth" is about
the *observed deployment* not setting `VNC_PASSWORD` (or accepting a weak
default) in some instances — the *mechanism itself is capable of real auth*,
contrary to a first read of TASK-005 line 57. This nuance is worth folding
back into TASK-005/Sprint-19/20 hardening notes if not already known.

**`entrypoint.sh`** — the tmux+xterm terminal mechanism:
```
tmux new-session -d -s "$SESSION" -x 220 -y 60
tmux send-keys -t "$SESSION" "exec $WRAPPER_PATH" Enter   # Claude CLI, top pane
tmux split-window -t "$SESSION" -v -l 10                  # bottom strip
tmux send-keys -t "$SESSION:0.1" "... log tail ..." Enter
tmux select-pane -t "$SESSION:0.0"
tmux attach-session -t "$SESSION"
...
xterm -fa 'DejaVu Sans Mono' -fs 12 -bg black -fg white -geometry 220x60+0+0 \
  -T "[${CLAUDE_ID}]" -e "bash $TMUX_LAUNCHER $WRAPPER"
```
i.e. `xterm` (running inside the Xvfb virtual display, so it's what x11vnc
renders and what noVNC streams to the browser) execs a launcher that starts a
detached **tmux** session (Claude CLI in the main pane, a log tail in a
bottom split), then attaches to it. tmux gives session persistence — if the
xterm process dies/restarts (the entrypoint has a restart/"keeper" loop,
lines ~192-235), re-attaching to the same tmux session preserves scrollback
and running state instead of losing it. A separate `INBOX_MODE=tmux` path
(`entrypoint.sh:275-298`) even delivers external messages into the running
Claude session non-destructively via `tmux send-keys`.

This is a complete, already-running answer to "spawn a container running
tmux, expose it over VNC": **Xvfb (virtual framebuffer) + fluxbox (minimal
WM, arguably droppable if xterm is maximized/fullscreen and no other windows
are needed) + xterm (the actual PTY, rendered on the virtual display) + tmux
(session persistence/multi-pane/programmatic input) + x11vnc (VNC server on
that display, password-gated) + websockify (WS↔VNC bridge for noVNC's
browser client)**. No custom Go PTY-over-WebSocket bridge, no ttyd even —
this sidesteps the "web-terminal" question entirely by tunnelling a real X11
desktop's xterm through VNC instead. It's heavier (a full Xvfb+WM stack per
agent) than a pure ttyd/xterm.js WebSocket terminal would be, but it's proven
running in production across 7 agent containers today, and it gets you tmux
detach/reattach + programmatic `send-keys` injection for free, which a plain
ttyd sidecar would not (ttyd wraps one command and dies with it — you'd
still want tmux underneath it for detach/reattach, so tmux is complementary
to either terminal-serving mechanism, not an alternative to it).

No CDC/DB-sync pattern was found (TASK-005 already noted this as a negative
result) and nothing new on multi-node secrets beyond what TASK-005 recorded.
`/home/ji/projects/trading` was **not** re-explored — a first grep attempt
there hit a huge, irrelevant vendored `.qoder/repowiki` metadata JSON tree
(11+ MB) with no signal, and TASK-005 already covered `st-2`'s compose/topology
structurally; going file-by-file into `/home/ji/projects/trading` beyond that
would violate this task's own time-box and TASK-005's explicit "no
module-depth" rule for `st-2`. If tmux/VNC specifics matter more for
trading-agent-infra specifically, that would need a dedicated follow-up task,
not a re-derivation here.

---

## 5. Proposal — scoped first version

Goal: a `terminal` Framework option (plain shell, no AI provider baked in)
and make OpenCode reachable as a CLI-only terminal session too, using the
jimesh-crew tmux+VNC pattern as the proven mechanism, while fixing the
existing noVNC auth gap in the same pass since the fix is now known and
concrete.

**New Framework enum value(s)** (`store.ProjectRow.Framework` comment +
callers): add `"terminal"` (plain shell + tmux, no VNC — pure SSH-tunnelled
web terminal, see mechanism choice below) and optionally `"opencode_terminal"`
(OpenCode CLI, no VNC desktop — the CLI-only sibling of today's
`opencode`/VNC-desktop framework, matching the "OpenCode as an offered
option" ask without dragging in noVNC for people who just want the CLI).
Follow the existing `_code_server` naming convention (`dsh_code_server`,
`opencode_code_server`) rather than inventing a new separator scheme.

**Terminal-serving mechanism — needs a decision, propose ttyd first:**
R15/R17 already ruled out a custom Go xterm.js-to-SSH bridge (CUT, overkill).
Two proven options now on the table:
1. **ttyd sidecar** (the standing backlog item, `BACKLOG.md:120,328`) — one
   binary, wraps a shell or `docker exec`, serves it over WebSocket directly;
   simplest for a *plain* terminal deploy with no desktop. Recommended
   default for the new `"terminal"` framework: lighter than Xvfb+VNC, no
   password-gated X11 stack needed, matches the existing backlog decision.
2. **jimesh-crew's Xvfb+fluxbox+xterm+tmux+x11vnc+websockify stack** (§4) —
   heavier, but battle-tested, and gives tmux detach/reattach +
   `send-keys` programmatic injection (useful if JiMesh ever wants an agent
   or the utility model to type into a running terminal session
   non-interactively). Recommended for the VNC-desktop frameworks
   (`opencode`, future `dsh`-desktop variants) rather than for the plain
   `"terminal"` option — reuse this exact `start-vnc.sh` password-mandatory
   pattern to finally close `TODO(security, noVNC)` in `projects_ssh.go`.

Either way, **tmux belongs underneath the terminal-serving layer regardless
of which one is picked** — it's what makes a container restart or a
websocket disconnect non-destructive to the running session, independent of
whether the transport is ttyd or an X11-desktop VNC.

**Provisioning/deploy changes** (`src/backend/internal/deploy/projects_ssh.go`):
- Add a new `docker run` branch alongside the existing
  `dsh`/`opencode`/`jimesh` cases (~line 982-1029) for `"terminal"`: pull a
  small base image (e.g. `ubuntu:24.04` or reuse the existing runtime-preset
  images) with `ttyd` installed, bind-mount the workspace, publish
  `$ALLOC_PORT` on `127.0.0.1` exactly like the other frameworks, run `ttyd
  tmux new-session -A -s main` (the `-A` makes ttyd attach-or-create, so
  reconnecting a browser tab re-attaches instead of spawning a second shell).
- Update `frameworkStartsWorkspace()` (line 182) to return `true` for the new
  value(s) so the egress-allowlist + socket-guard sidecar (TASK-019) attach
  correctly — this is a single-container framework like `dsh`/`opencode`, not
  a multi-container stack like `jimesh`.
- If `opencode_terminal` is added: same docker-run pattern as `opencode`
  minus the VNC port allocation/env, running OpenCode's CLI directly inside
  the ttyd/tmux session instead of the noVNC desktop image.
- If the VNC-desktop path adopts jimesh-crew's mechanism: replace the current
  bare `ghcr.io/ji-workstation/opencode-vnc:latest` run line (line 1001) with a
  JiMesh-built image (Dockerfile checked into this repo, so it can actually be
  audited — closing the "no source, can't audit for auth" problem noted at
  line 989) using the Xvfb/fluxbox/xterm/tmux/x11vnc/websockify recipe with a
  generated `VNC_PASSWORD` wired in exactly like `codeServerPassword` already
  is for code-server.

**Frontend changes** (`src/frontend/src/views/ProjectsPage.tsx`):
- Extend the `framework` union (line 30) with `'terminal'` (and
  `'opencode_terminal'` if adopted).
- Add `<option value="terminal">Terminal (no IDE)</option>` to both
  framework `<select>`s (~lines 1239, 1504), without the VNC-port field
  shown (`disabled`/hidden the way the code-server-port field already is
  conditionally hidden for non-VS-Code frameworks, e.g. line 1355/1620
  pattern).
- `hasVSCode` boolean checks (lines 726, 367, 423, 572, 701) stay `false` for
  `terminal` — no change needed there, it already defaults to false for
  unmatched frameworks.
- Reuse the existing iframe embed path (the "Active Framework UI" iframe,
  line 1003 area) pointed at `http://<host>:<allocatedPort>` for ttyd's own
  web UI — no new embed mechanism needed, ttyd already serves a full HTML
  page.
- `src/backend/internal/store/rbac.go:353` (`TypeToCategory`) already has a
  `"terminal": "Terminals"` mapping from the app-category work — reusable
  as-is for widget/smart-suggestion display of this new Framework option; no
  change needed there.

**Explicitly out of scope for a "first version"** (flag for a future task,
don't build now): the full `deployment_schemas`/`deployment_addons`
layered-schema/addon-composition system from R9 §6 — that's a much bigger
schema-registry + frontend-form-generator project, orthogonal to just adding
one or two new Framework values, and R15/R17 never gave it a CUT/KEEP
verdict either way. Land the concrete Framework value(s) first; revisit the
generic schema layer only if/when a third or fourth "medium type" makes the
enum approach genuinely unwieldy.

No utility-deployment-on-new-SSH-endpoint proposal is included here since
§3 found no existing plan to build on — that would need its own
requirements conversation before a task file could be written.
