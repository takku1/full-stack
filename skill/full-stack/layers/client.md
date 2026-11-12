---
layer: client
decides: [client kind (web, native, desktop, CLI, none), UI framework, rendering strategy, client state ownership, offline behavior, accessibility approach]
constrains: [interface, runtime, platform]
criteria: [fit to user tasks and devices, rendering and offline needs, accessibility, team familiarity, bundle and startup cost, maturity, license]
evidence: [current release and support policy, platform and browser support, accessibility support, documented limits]
tags: [browser, server-rendered, static-site, single-page-app, offline-first, native-mobile, desktop-native, cli, terminal-ui, client-holds-cache-only]
---

# Client layer

Decides how people (or scripts) operate the system, and what the client
may own. Start from representative user tasks, not screens.

## Establish first

1. **Users and tasks**: who uses it, the three to five representative
   tasks, on which devices, and with what connectivity.
2. **State ownership**: what the client only caches, what it owns
   temporarily (drafts, offline queue), and what the server owns.
3. **Rendering needs**: first-load speed, search indexing, interactivity,
   and whether content works without client scripting.
4. **Offline and failure behavior**: what each task does when the network
   or server is down, slow, or returns an error.
5. **Accessibility and localization** obligations.

## Choosing

Pick the client kind from the tasks: a CLI or form can beat an app.
Prefer the framework the team already ships. Choose server rendering,
static output, or a client-side app from the rendering needs, not fashion.
Keep domain policy out of the client unless offline operation requires a
local copy, and then name the server as the authority.

## Traps to check

- Client and server both enforcing (or neither enforcing) a business rule.
- Optimistic UI without a rollback path for rejected writes.
- Offline edits without the conflict policy the data layer defined.
- A rendering mode the chosen platform cannot host.
- Inaccessible custom controls replacing native ones.

## Neighbor assumptions to record

What the interface must provide (sync, pagination, error detail), what the
platform must host (server rendering, static files, app stores), and any
shared types or validation with the runtime.
