# Field report 2 — updated SKILL.md, design flow, Recurspec repo (2026-10-03)

Follows [field-report-2026-10-03-mochios.md](field-report-2026-10-03-mochios.md).
The revision that report prompted was installed and re-run on a
non-routine **design-only** request in the same MochiOS session: the
next resize-damage rung (occlusion of shadow changes under an opaque
window body). The design landed in the project's existing note
(`docs/notes/WINDOWING.md`) with registry row R-266 in
`docs/ROADMAP.md`. Nothing was built.

**Verdict.** The first report's five fixes all landed and read
naturally; no friction recurred from them. The design flow's readiness
gate earned its keep. Three new frictions, all about **where things
go** in a project that already has strong conventions.

## Confirmed fixed (from report 1)

| Report 1 item | Observed in this run |
|---|---|
| F1 derive criteria | Not exercised (design only); wording reads cleanly. |
| F2 registry resolution | Applied — but see G1: the rule picks the wrong file in Recurspec repos. |
| F3 routine/registry consistency | Consistent across both flows now. |
| F4 "formal" → "structured" | Applied. |
| Concurrent-edit check | Applied; checked `git status` on every target before editing. See G4 for the gap. |

## What worked

- **Package shape + readiness gate.** Scope / ownership & contracts /
  choices / increments / blockers fit in ~60 lines inside an existing
  note. Requiring *prerequisites and checks* is what turned "build
  occlusion" into "measure first, build only if the baseline says
  so" — the most valuable output of the run.
- **"State consequential assumptions with their cost if false."**
  Prompted checking whether the window body is actually opaque.
  It isn't under one theme (Dusk's surface is 24% translucent), which
  would have made a naive occlusion cull leave stale pixels. That became
  the design's main condition rather than a bug found later.
- **`never: expand scope`.** Kept the more valuable but product-level
  alternative (ghost/outline resize, an open owner decision) as a
  recorded alternative + blocker instead of quietly designing it.

## Friction found

### G1 — registry rule and the Recurspec reference disagree, and the order hides it

`contract.registry` now says "subject work tracker nearest the changed
component". `references/existing-projects.md` says for Recurspec
projects "`ROADMAP.md` [is] the work registry". In the implement run I
followed the contract and picked the nearest tracker (a feature notes
file); the reference — loaded later — says that was wrong.

The ordering makes this structural: `design` reads registry entries
during grounding, but `existing-projects.md` (which says *which* file
is the registry) only loads near the end, under "if subject has
existing contracts, providers, or registries".

**Fix.** Resolve registry identity during grounding:

```logic
  if subject is known:
    read instructions from subject as context
    if subject has existing contracts, providers, or registries:
      read integration guide from references/existing-projects.md as integration
    apply grounding with context as scope
```

and make the contract path say it: `path: the subject's declared work
registry (Recurspec: ROADMAP.md); else the tracker nearest the changed
component; none → skip`.

### G2 — `write design with design_docs` vs subject rules that forbid new doc files

MochiOS's CLAUDE.md says "NEVER create documentation files unless
explicitly requested"; plenty of repos have similar rules. The flow's
final write is unconditional, and `existing-projects.md`'s standalone
default is `docs/design/` — a new tree. I resolved it by appending to
the existing proposal note for the component, which the subject rule
allows, but the skill gave no guidance on precedence.

**Fix.** Add to `always`: `subject instructions take precedence over
package defaults`. Change the write to:

```logic
  if subject has a design note for the affected component:
    write design into that note
  otherwise:
    write design with design_docs
```

with `never: create a design file the subject's instructions forbid`.

### G3 — no step for contract-node evidence after implementation

Recurspec nodes carry "current implementation" evidence bullets
(MochiOS `interface/compositor/SYSTEM.md` has one for the very
mechanism changed). `implement` updates the registry but says nothing
about the owning node's evidence, and `existing-projects.md` says
accepted contract edits follow the repo's own validation. I left the
node untouched and flagged it, which was the safe reading, but the
skill should say so explicitly.

**Fix.** In `implement`, after the registry write:
`if subject uses Recurspec: report owning-node evidence updates as
proposed, not applied` (keeps contract edits in Recurspec's workflow
while ensuring they aren't forgotten).

### G4 — concurrency check covers files, not shared run resources

The new `always: confirm target files have no concurrent uncommitted
edits` worked. What actually collided was a **shared executable**:
another agent session's `cargo xtask` held `target/release/xtask.exe`,
so my verification run failed with "Access is denied". Waiting for the
other process (not killing it) was right, but the skill only frames
concurrency as file edits.

**Fix.** Widen it: `confirm targets and shared build/run resources
(locked binaries, emulators, ports) are not in use by another session;
wait rather than interrupt`.

### G5 — install path: I bypassed `install.ps1`

Not a skill defect — operator error worth noting for the README. Both
reinstalls this session used `cp -r`, which worked only because no
stale files existed; `install.ps1 -Target Claude` hash-verifies and
refuses unexpected files ("Installed and SHA256-verified 9 files").
The apparent whole-file diff of `references/design-method.md` was the
old installed copy being CRLF; source is LF under `.gitattributes`.
Suggest one README line: "reinstall with `install.ps1`; do not copy".

## Suggested edit list (priority order)

1. G1 — resolve registry identity in grounding; Recurspec → ROADMAP.md.
2. G2 — subject-instruction precedence + write into existing design note.
3. G4 — concurrency check covers shared run resources.
4. G3 — propose (don't apply) contract-node evidence updates.
5. G5 — README: install via `install.ps1` only.
