# Modular layer orchestration (proposed)

Status: **implemented as package 0.4.0, not yet evaluated** ([D-017](../design-decisions.md#d-017-modular-layer-orchestration-package-040)). The package structure, layer modules, templates, rules, and `check_stack.py` with tests exist (FS-011 to FS-014). No live trial or comparative evaluation has run (FS-015, FS-016). Package 0.3.0 is recoverable from git (`2d96942`). Rationale and sources: [modular-redesign.md](../research/modular-redesign.md).

## Outcome

Full Stack chooses and connects technologies layer by layer (data, runtime and scripting, interface, client, platform, and cross-cutting concerns) for a new system or a change that needs a new technology. One orchestrator keeps the layers consistent. For changes that need no new technology, it behaves no worse than the 312-token brief from [FS-009](../../evals/results/context-dose-2026-10-05.md), at similar cost.

Excluded: a catalog or ranking of "best" tools; replacing a project's existing stack without a request; agents that negotiate or bid; a runtime, CLI, or service beyond scripts.

## Constraints carried forward

- **No universal catalog or fixed stack** ([project framing](../project-framing.md#initial-non-goals)). Layer modules hold questions, criteria, and evidence requirements. A run researches current candidates for *this* brief.
- **Existing authority wins.** In an existing repository each layer starts as "keep current". It is reopened only when the selected outcome cannot be met with the current choice, and that finding is recorded as a prerequisite (D-005). Discovering a weakness does not authorize migration.
- **Costly-to-reverse commitments ask first** (D-015). Introducing a new datastore, language, or hosting platform usually qualifies.
- **Executed evidence over self-report** (D-016). Compatibility is checked by script.
- **Small always-loaded core** (FS-009, [30]–[34] in the register).

## Package structure

```
skill/full-stack/
  SKILL.md               core (always): ~brief-sized rules + routing to flows and layers
  flows/
    design.md            design flow (loaded for design work)
    stack.md             stack orchestration (loaded when a layer needs a technology choice)
    implement.md         implement flow (loaded for build requests)
  templates/
    stack-brief.md       brief the orchestrator writes once
    decision-record.md   ADR-shaped record per affected layer
  layers/                one module per layer, loaded only for affected layers
    data.md              data model, storage engine, schema and migration, consistency
    runtime.md           language, framework, scripting and build tooling
    interface.md         API style, contract format, versioning, events
    client.md            web, native, or CLI front end; state and rendering
    platform.md          hosting, packaging, CI/CD, environments
    crosscut.md          security and auth, observability, test strategy (checked against all)
    custom.md            template for domain layers (kernel, firmware, pipeline stage)
  references/            existing method references (terminology, design method, artifacts, ...)
  rules/
    compatibility.json   seed requires / excludes rules over layer tags
  scripts/
    run_guard.py         existing write-set and check guard
    check_stack.py       validates decision records against rules and each other
```

The layer set is a default, not an ontology. A project with a different decomposition (MochiOS's compositor, shell, and kernel services) uses `custom.md` per layer. Layers are split where hidden decisions and authority differ (Parnas; D-003), not by directory.

## Distribution

The same folder ships two ways ([D-019](../design-decisions.md#d-019-ship-as-a-claude-code-plugin-around-the-portable-skill)). As a plain skill, the install scripts copy `skill/full-stack` for Codex and Claude Code. As a Claude Code plugin rooted at `skill/`, it adds `hooks/hooks.json` (the guard runs automatically through `scripts/guard_hook.sh`) and `agents/stack-evidence.md` (evidence rows on a small model).

## Stack brief

The orchestrator writes the brief once. Every layer reads it, and only the orchestrator edits it.

| Field | Content |
|---|---|
| Outcome | Selected outcome and requirement IDs |
| Quality scenarios | Observable targets: load, latency, durability, offline, cost ceiling, accessibility |
| Constraints | Existing stack, team skills, licenses, platforms, deployment targets, budget |
| Futures | Two to four plausible changes used for regret (for example tenfold load, team handover, new client type) |
| Innovation budget | How many non-boring choices are allowed (default one) |
| Affected layers | Layers this outcome touches; all others are "keep current" or out of scope |
| Settled contracts | Cross-layer contracts already fixed (from the existing repo or earlier decisions) |

## Layer module interface

Every module has the same shape so the orchestrator treats them uniformly:

```yaml
layer: data
decides: [data model, storage engine, schema and migration approach, consistency model]
reads: [quality scenarios, constraints, futures, settled contracts]
constrains: [runtime, interface, platform]      # neighbors its choice can limit
questions:                                       # what to establish before candidates
  - access patterns and volumes per entity
  - consistency and durability needs per scenario
  - existing stores and their owners
criteria: [fit to scenarios, operational burden, team familiarity, maturity, license, cost]
evidence: [current release and maintenance activity, license text, documented limits]
```

The module body holds the method for that layer: what to ask, common traps (for example a cache gaining authority, schema migrations without rollback), and what counts as evidence. It does not rank products.

## Decision record

Each layer produces one record in ADR form (Nygard; MADR-compatible):

- **Context**: brief fields this decision depends on.
- **Candidates**: two or three, each with evidence (version and date checked, license, known limits).
- **Scores**: criteria against quality scenarios, plus cost (CBAM-style, ordinal is fine).
- **Regret**: for each future, how far each candidate falls short of the best candidate in that future; the minimax-regret candidate is noted.
- **Decision and status**: proposed, conditional (awaits evidence or authorization), or accepted.
- **Neighbor assumptions**: what this choice requires from each neighbor (for example "runtime has a maintained async driver for the store").
- **Consequences and revisit conditions**: what becomes easy or hard, and which observation would reopen the decision.
- **Novelty**: whether it spends the innovation budget.

## Orchestration

1. **Frame and ground** as in 0.3.0. Write the stack brief. Mark unaffected layers "keep current".
2. **Pass 1, candidate sets.** For each affected layer, load its module and produce candidates with neighbor assumptions. Research for independent layers may run in parallel subagents where the host allows. Subagents return evidence; they do not decide.
3. **Intersect.** Run `check_stack.py` over the candidate sets to remove combinations that break rules or neighbor assumptions. The orchestrator then chooses the joint profile: the combination that best meets the scenarios, with minimax regret as a tie-breaker and the innovation budget respected. Layers do not choose independently.
4. **Authorize.** Costly-to-reverse commitments in the profile go to the user (D-015). Declined commitments make dependent layers conditional.
5. **Pass 2, finalize.** Each affected layer records its decision against the committed profile and settled contracts.
6. **Check.** `check_stack.py` must exit 0: every neighbor assumption is met by a recorded decision or listed as a blocker. Then produce the 0.3.0 design package (scope, ownership and contracts, choices, increments, blockers). The layer records fill "choices".
7. **Implement** (only when asked) follows the 0.3.0 implement flow and guard unchanged.

For a change with no new technology, steps 2–5 collapse to "keep current" and the run costs about what the brief does.

## Compatibility rules

Each layer choice declares `provides` tags (guarantees it gives neighbors) and `assumes` tags per neighbor (what it needs). The terms reuse the `provides` relation from the terminology reference. `rules/compatibility.json` holds twelve seed rules over those tags:

```json
{"id": "R-002",
 "when": {"platform": ["horizontally-scaled-instances"]},
 "excludes": {"data": ["embedded-single-writer"]},
 "why": "Several instances cannot safely share one embedded single-writer database file."}
```

A rule fires when every layer in `when` provides all the listed tags; `brief` refers to `brief.tags`. `requires` then demands tags from a layer, and `excludes` forbids them. The rules are deliberately few and generic, covering structural compatibility rather than products. A run may add a project-local rule in the stack block only with cited evidence.

`check_stack.py` (standard library only) reads a `.json` file or a Markdown design containing one ` ```json stack ` block:

- `check` validates committed choices. It flags unmet neighbor assumptions (downgraded to warnings when the assuming layer is conditional or blocked), fired rules, an exceeded innovation budget, affected layers without a decision, and records missing a choice or alternatives.
- `profiles` enumerates combinations of candidate sets (capped at 20,000). It lists the surviving profiles, fewest novel choices first, and counts what eliminated the rest.

Exit codes: 0 consistent or at least one survivor; 1 violations or no survivor; 2 unreadable input. The script cannot judge quality; it catches mismatches. Tags only work if runs use the same spelling, which is why each layer module lists its common tags.

## Evaluation

- **Greenfield stack cases** (FS-016): briefs with known-sensible answer ranges (offline-first notes app, high-write telemetry service, internal CRUD tool for a small team, CLI data pipeline). Graded blind on stack coherence, justification against scenarios, regret awareness, unnecessary novelty, and scope honesty. Compared with plain, brief, and 0.3.0 at matched budgets.
- **Existing-repo cases**: confirm "keep current" holds and that no migration is proposed without a requirement.
- **Module attribution** (FS-017): sampled Shapley values over layer modules, measuring which modules raise grades.
- **Check accuracy**: seeded inconsistent profiles to measure `check_stack.py` recall and false positives.

## Increments

See [ROADMAP.md](../../ROADMAP.md) FS-011 to FS-018. The first slice is FS-011, FS-012, FS-013, and FS-014: brief and record templates, a brief-sized core with flows split out, the `data` and `runtime` modules, and `check_stack.py` with tests. That slice is then evaluated on one greenfield case before more layers are written.

## Blockers and open questions

- FS-009 has one session per cell; the core-size decision rests on thin evidence until it is repeated.
- Whether two passes beat one at equal tokens is unknown (research report, open question 2).
- Host subagent support differs (Claude Code supports subagents; Codex support was not checked). The design must work with no subagents.
- The SkillWren logic format (D-013) may not survive the split into core and flows. That will be decided at FS-012 from measured cost, not preference.
