# Status

**Last Updated**: 2026-11-12

## Current Phase

Package 0.5.1: the 0.4.0 modular layer redesign plus a risk-tiered assurance dimension (D-020); 0.5.1 fixes run-guard defects from field report 3. It passes packaging and unit checks, and the plugin plumbing passed a live smoke test on Windows (FS-023). It has not yet been used on a real design task (FS-015) or compared against 0.4.0, 0.3.0, the brief, or plain prompting (FS-016).

## Active Focus

Feature freeze: evidence before features. FS-023 is done on Windows ([results](../evals/results/plugin-smoke-2026-11-12.md)): the plugin plumbing works, and five guard defects were reproduced and fixed. FS-015 first run ([results](../evals/results/fs015-2026-11-12.md), $0.24): 7/7 hidden checks passed, but the model skipped the stack records, the assurance table, and the guard (the guard was blocked by harness permissions). Next: one FS-015 rerun with harness fixes, then FS-016. The assurance dimension (FS-026) was built at the owner's request and is unevaluated; FS-016 gains planted-failure cases for it. An [external review](research/review-2026-11-12-external.md) (2026-11-12) rated direction strong and empirical validation weak (3/10); its fixable defect, an absolute no-reread rule, is corrected. [Field report 3](research/field-report-2026-11-12-mochios-3.md) (0.5.0 building a MochiOS kernel slice, plus 60 guarded runs) found three guard defects, now reproduced in tests and fixed (D1, D3, D4), and the assurance screen skipped again on a live build (G1, recorded under frozen FS-027). A [second review](research/review-2026-11-12-external-2.md) of 0.5.0 found assurance effectiveness unproven; its measures (check meaningfulness, screen recall on implicit risk, planted multi-tenant flaws) are added to FS-016.


- FS-015: first greenfield trial of 0.5.0 end to end: stack brief → candidate sets → `check_stack.py profiles` → decision records → `check_stack.py check` → assurance screen and table → checks through `run_guard.py`.
- FS-005: Claude Code plugin discovery and invocation verified live (FS-023 T1, 2026-11-12); Codex discovery and invocation still unverified.
- FS-016: design the greenfield stack-selection evaluation; the FS-009 harness is the starting point.
- FS-019: cost optimization. [Research](research/optimization.md) found that FS-009's extra skill cost tracks extra turns more than instruction length. A turn budget, output caps, and batch guard commands are now applied (D-018). They stand only if they pass a pre-registered non-inferiority test.

## Architecture Summary

Full Stack is a portable agent skill, shipped for Claude Code as a plugin rooted at `skill/` that adds an automatic guard hook and a haiku `stack-evidence` subagent (D-019). Its small core, `SKILL.md` at about 640 tokens, is always loaded and routes to on-demand flows (`design`, `stack`, `implement`) and to one module per layer (data, runtime, interface, client, platform, crosscut, custom). An assurance screen raises only the relevant disciplines (security, verification, reliability, and eight more), each with Policy, Framework, How to, and Checks, and its checks feed the run guard. When a technology must be chosen, the orchestrator writes a stack brief. Layers propose candidate sets with `provides` and `assumes` tags; `scripts/check_stack.py` intersects them against `rules/compatibility.json`, and the orchestrator commits one joint profile with ADR-shaped decision records. Implementation follows the 0.3.0 flow, guarded by `scripts/run_guard.py` in three calls (start, checks, close).

## Key Decisions

- [D-017](design-decisions.md#d-017-modular-layer-orchestration-package-040): modular layers, a tiered core, central orchestration of coupled choices, methods instead of catalogs, mechanical compatibility checks, and existing stacks kept by default. Research: [modular-redesign.md](research/modular-redesign.md).
- [D-018](design-decisions.md#d-018-optimize-turns-and-output-before-instruction-length): optimize turns and output first. The guard now has batch `checks` and `close` commands; the core sets a turn budget; templates cap output. Unevaluated.
- [D-020](design-decisions.md#d-020-build-the-assurance-dimension-package-050): assurance dimension built (owner exception to the freeze); unevaluated.
- [D-019](design-decisions.md#d-019-ship-as-a-claude-code-plugin-around-the-portable-skill): plugin around the portable skill; strict validation passes and the plugin loaded and worked live on Windows (FS-023). No license chosen yet.
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
