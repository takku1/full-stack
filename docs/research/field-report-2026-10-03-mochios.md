# Field report — logic-first SKILL.md in a live repo (2026-10-03)

**Context.** First real use of the logic-first `SKILL.md` (installed from
`skill/full-stack` on 2026-10-03, replacing the 2026-09-09 prose version).
Task: in MochiOS (a large Rust OS monorepo, several agent sessions active
at once), implement a contained performance fix — geometry-aware damage
in the UI frame differ plus a damage-set merge rule — after a prior
investigation turn in the same conversation. Invoked as
`full-stack` with a one-line args summary; the user had said "yeah and
let's do it clean".

**Verdict.** Low friction overall. The routine-edit short-circuit and the
compact `always`/`never` contract did their job. Three points made me
stop and decide something the skill should have decided for me.

## What worked

- **Routine-edit branch.** `if request is an isolated routine edit:
  generate minimal edit note` fired cleanly — no architecture tree, no
  research pass, no design-doc write for a two-crate change. This is the
  single biggest frictionless win; keep it first in `design`.
- **Contract block is skimmable.** `always`/`never` fit in working memory
  and were actually applied (e.g. "mark unexecuted checks as unexecuted"
  shaped how I report `xtask run` status).
- **Ambiguity gate didn't fire spuriously.** Outcome and authority were
  clear from the prior turn; the skill did not force a clarification.

## Friction found

### F1 — `implement` asks for acceptance criteria the conversation already holds

`unless criteria are known: ask user to state the acceptance criteria`
gives no rule for what "known" means. Here the criteria were implicit in
the prior investigation (damage ⊇ changed pixels; resize damage shrinks
to edge bands; tests + build pass). I had to decide on my own that this
counted as known; a stricter reading would have produced a needless
question mid-flow.

**Fix.** Derive before asking:

```logic
  unless criteria are known:
    generate criteria from request and prior conversation as criteria
    if criteria cannot be derived:
      ask user to state the acceptance criteria as criteria
```

and state derived criteria in the completion report so the user can
correct them after the fact rather than before.

### F2 — `registry` is undefined for repos that have none

Both flows end with `apply registry update … write entry with registry`,
and the contract declares `registry: path: work registry` without saying
how to find it. MochiOS has several candidates (`docs/ROADMAP.md`, wiki
checklists, a per-feature notes file with an evidence log); a repo
without any leaves the step un-executable. I chose the feature's own
notes file (`docs/notes/WINDOWING.md` evidence log).

**Fix.** Resolve, don't assume:

```contract
  registry:
    path: the subject's existing work tracker (roadmap, notes evidence
          log, issue file) nearest the changed component; none → skip
    access: read+create
```

and add `never: create a new registry file without authorization` —
creating one would collide with "NEVER create documentation files unless
requested" rules common in project CLAUDE.md files.

### F3 — routine branch returns before the registry write, implement doesn't

`design` returns early for routine edits (no registry write), but
`implement` unconditionally writes a registry entry. Same task, two
answers. Pick one: either routine edits skip the registry in both flows,
or both record a one-line entry. Recommend: routine edits record only
when the subject already has a tracker for that component (ties into F2).

### F4 — the DSL verbs carry description, not control

`apply X with Y as Z`, `apply shape with patterns as design` read as
prose with variable names. That's fine for an agent, but the header
claims "control is formal". Either tone the claim down ("control is
structured") or narrow the verb set to ones with defined effects
(`read`, `write`, `ask`, `verify`, `return`) and push the rest into the
appendix as guidance. Not a blocker; it just costs a beat of "is this
step mandatory or advisory?".

## Not friction, but worth noting

- **Multi-session repos.** Nothing in the skill says to check for
  in-flight edits by other agents before touching files. I did it from
  project context (`git status` on the target paths). A one-line
  `always: confirm target files have no concurrent uncommitted edits`
  would make it portable.
- **Mid-task user messages** (two arrived during this run) didn't
  interact badly with the flow; the logic has no step that would block
  answering them.

## Suggested edit list (priority order)

1. F1 — derive-then-ask for acceptance criteria.
2. F2 — define registry resolution + no-new-registry rule.
3. F3 — make routine-edit registry behavior consistent across flows.
4. Concurrent-edit check in `always`.
5. F4 — reword "formal" or narrow verbs.
