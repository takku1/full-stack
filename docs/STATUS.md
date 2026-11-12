# Status

**Last Updated**: 2026-11-12

## Current Phase

Package 0.4.0, the modular layer redesign, is built and passes its packaging and unit checks. It has not been trialled live or compared against 0.3.0, the brief, or plain prompting.

## Active Focus

Feature freeze: evidence before features. FS-023 is done on Windows ([results](../evals/results/plugin-smoke-2026-11-12.md)): the plugin plumbing works, and five guard defects were reproduced and fixed. Next: FS-015, then FS-016. An [external review](research/review-2026-11-12-external.md) (2026-11-12) rated direction strong and empirical validation weak (3/10); its fixable defect, an absolute no-reread rule, is corrected.


- FS-015: first greenfield trial of 0.4.0 end to end (stack brief → candidate sets → `check_stack.py profiles` → decision records → `check_stack.py check`).
- FS-005: re-verify host discovery and invocation, since `SKILL.md` changed shape.
- FS-016: design the greenfield stack-selection evaluation; the FS-009 harness is the starting point.
- FS-019: cost optimization. [Research](research/optimization.md) found that FS-009's extra skill cost tracks extra turns more than instruction length. A turn budget, output caps, and batch guard commands are now applied (D-018). They stand only if they pass a pre-registered non-inferiority test.

## Architecture Summary

Full Stack is a portable agent skill, shipped for Claude Code as a plugin rooted at `skill/` that adds an automatic guard hook and a haiku `stack-evidence` subagent (D-019). Its small core, `SKILL.md` at about 640 tokens, is always loaded and routes to on-demand flows (`design`, `stack`, `implement`) and to one module per layer (data, runtime, interface, client, platform, crosscut, custom). When a technology must be chosen, the orchestrator writes a stack brief. Layers propose candidate sets with `provides` and `assumes` tags; `scripts/check_stack.py` intersects them against `rules/compatibility.json`, and the orchestrator commits one joint profile with ADR-shaped decision records. Implementation follows the 0.3.0 flow, guarded by `scripts/run_guard.py` in three calls (start, checks, close).

## Key Decisions

- [D-017](design-decisions.md#d-017-modular-layer-orchestration-package-040): modular layers, a tiered core, central orchestration of coupled choices, methods instead of catalogs, mechanical compatibility checks, and existing stacks kept by default. Research: [modular-redesign.md](research/modular-redesign.md).
- [D-018](design-decisions.md#d-018-optimize-turns-and-output-before-instruction-length): optimize turns and output first. The guard now has batch `checks` and `close` commands; the core sets a turn budget; templates cap output. Unevaluated.
- [D-019](design-decisions.md#d-019-ship-as-a-claude-code-plugin-around-the-portable-skill): plugin around the portable skill; validated, not yet loaded live (FS-023). No license chosen yet.
- D-016: mechanical run guard and A/B harness (still in force).
- D-015: costly-to-reverse commitments need authorization; work is ready, conditional, or blocked (still in force).

## Deprecated/Legacy

- **SkillWren header in `SKILL.md`** (contract, authority, effects, budget): removed in 0.4.0. Hosts read only `name` and `description`, and the header cost about 400 tokens per run. The logic blocks now live in `flows/`.
- **D-016's rejection of a lighter profile**: superseded by D-017 on FS-009 evidence.
- **0.3.0 single-file entrypoint** (~3,400 tokens): replaced; recoverable at commit `2d96942`.
- Field reports and reviews in `docs/research/` that describe 0.3.0 behavior remain as history. They are not archived because they still motivate retained rules.

## Known Gaps

- Evidence for the core-size decision is one session per cell (FS-009).
- The compatibility rules are a 12-rule seed; tag spelling must match across runs.
- Codex discovery and invocation are unverified (FS-005), and `install.sh` is untested on macOS or Linux.
