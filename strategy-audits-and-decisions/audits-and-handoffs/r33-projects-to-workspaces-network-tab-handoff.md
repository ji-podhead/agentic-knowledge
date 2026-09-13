---
okf_version: "1.0"
id: "okf-str-aud-r33-projects-to-workspaces-network-tab-handoff"
title: "SPECIFICATION HANDOFF: Workspaces Renaming & Networks Tab (Scanopy)"
topic: "strategy-audits-and-decisions"
subtopic: "audits-and-handoffs"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - strategy-audits-and-decisions
  - audits-and-handoffs
summary: "---"
---

# SPECIFICATION HANDOFF: Workspaces Renaming & Networks Tab (Scanopy)

---
**Date:** September 11, 2026
**Sprint:** Sprint 34 Planning & Implementation Blueprint
**Status:** High-Signal Specification / Ready for Claude
**Target File:** `docs/research/R33-projects-to-workspaces-network-tab-handoff.md`

---

## 🎯 1. Overview
The operator has requested a clean, secure, and professional pivot from the generic **"Projects"** terminology to **"Workspaces"** across the entire application stack. This rename is not merely aesthetic; it establishes a clear conceptual boundary representing isolated, secure gVisor container environments.

Additionally, a dedicated **"Networks" Tab** must be created in the frontend sidebar to prepare the layout for **Scanopy**—our future decentralized service mesh and secure gVisor filesystem sharing configurator.

---

## 🏗️ 2. Chapter 1: The Global Rename (Projects ➔ Workspaces)

Claude must execute this rename surgically across all three layers of the monorepo without breaking the build or data integrity:

### A. Database Migration (PostgreSQL via pgx/v5)
In `src/backend/internal/store/store.go`, inside the `migrate()` function:
1.  Add an idempotent table-rename migration:
    ```sql
    ALTER TABLE projects RENAME TO workspaces;
    ```
2.  Add migrations to rename any project-specific foreign key columns or indexes (such as in the `containers` table from `project_id` to `workspace_id`).
3.  Ensure all SQL queries throughout the repository (especially in `store.go`) are updated from `SELECT ... FROM projects` to `SELECT ... FROM workspaces`.

### B. Go Backend Refactoring (`src/backend/`)
1.  **Rename Structs:** Change `ProjectRow` to `WorkspaceRow` inside `store.go`.
2.  **Rename Handler Functions:** Update Go methods from `UpsertProject` to `UpsertWorkspace`, `GetProject` to `GetWorkspace`, and `ListProjects` to `ListWorkspaces`.
3.  **Rename HTTP Routes:** Inside `internal/gateway/gateway.go` and `internal/deploy/deploy.go`, update the API route patterns:
    *   `/api/projects/deploy` $\rightarrow$ `/api/workspaces/deploy`
    *   `/api/projects/discover` $\rightarrow$ `/api/workspaces/discover`
    *   `/api/projects/{id}/tunnel/{port}` $\rightarrow$ `/api/workspaces/{id}/tunnel/{port}`

### C. Frontend React Refactoring (`src/frontend/`)
1.  **Rename Page File:** Rename `src/frontend/src/views/ProjectsPage.tsx` to `src/frontend/src/views/WorkspacesPage.tsx`.
2.  **Update Routing Imports:** Update Next.js/Vite routing definitions to load `WorkspacesPage.tsx`.
3.  **Rename Variables:** In React states, convert:
    *   `projects` $\rightarrow$ `workspaces`
    *   `activeProject` $\rightarrow$ `activeWorkspace`
    *   `localStorage` key `openmesh_projects` $\rightarrow$ `openmesh_workspaces`
4.  **UI Text Refactoring:** Systematically replace all occurrences of the word **"Project"** with **"Workspace"** across the entire interface (buttons, headers, modals, place-holders).

---

## 🌐 3. Chapter 2: The "Networks" Tab (Scanopy Blueprint)

Claude must build a new sidebar navigation reiter and view panel representing the global network configurations:

### A. Sidebar Integration
*   Add a new nav item to the sidebar: **`Networks`** (alongside "Workspaces", "KeyPool", etc.).
*   Icon: `Network` or `Globe` (using lucide-react).

### B. The Networks Dashboard Panel
When selected, render a gorgeous dashboard grid showing:
1.  **Global Network Profiles (Presets):**
    *   **Secure Userspace NAT (gVisor Netstack):** (Default, Highly Recommended) — Isolated user-space network layer, full Outbound NAT, zero exposed Host ports.
    *   **Airgapped Sandbox (No Network):** — Total network isolation, no Inbound/Outbound.
    *   **Host Passthrough:** — High performance, bypasses kernel isolation (Displays a prominent red Warning badge).
2.  **Scanopy Filesystem Share Configurator:**
    *   Draw an interactive or structured interface where the operator can configure **Shared Sentry Mount Groups**.
    *   Allows selecting multiple Workspaces and configuring them to **share the same secure, sandboxed gVisor volume** under a common filesharing group.
    *   Provides a preview of which workspaces have active folders, shared volume mount points, and their isolated NAT statuses.

---

## 🛡️ 4. Rules & Mandates for Claude
1.  **No Wildcard Bindings:** Do not let any code change bind to `0.0.0.0` or expose host ports.
2.  **Pure SSH Tunneling:** Operator-access iframe proxies must go strictly through the secure `/api/workspaces/{id}/tunnel/{port}` route, which direct-dials the isolated container IP (`172.x.x.x`) inside the SSH channel.
3.  **Strict Mode Protection:** The permissions script must never recursively chown/chmod `/root` or `.ssh`.
