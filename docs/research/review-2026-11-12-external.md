# External review of package 0.4.0 (2026-11-12)

A summary of an external review of commit `4785b9c`, supplied by the owner. The ratings are the reviewer's subjective assessment from the documentation and core workflows, not benchmark results.

## Verdict

"0.4.0 looks architecturally stronger than 0.3.0. It hasn't yet demonstrated that it produces better software." Ratings: architectural direction 9/10, scope and safety design 8.5/10, practical packaging 8/10, empirical validation 3/10.

## Strengths noted

- Conditional loading: the always-loaded core fell by about 81% (about 3,400 to about 640 tokens), and simple edits no longer pay for the layer method.
- Joint decisions across layers rather than independently optimized choices.
- Mechanical checks (`check_stack.py`, `run_guard.py`) that can be inspected independently, while narrower than a correctness guarantee.
- Minimax regret and a default innovation budget of one as a check against unnecessary novelty.

## Challenges and dispositions

| Challenge | Disposition |
|---|---|
| The absolute "never reread a file" rule breaks after edits or new evidence | **Fixed** in the core: reread only after a change or when new evidence makes it relevant |
| Twelve seed rules and self-declared tags can give false confidence; the checker validates declared relationships, not the declarations (consistency is not correctness) | Recorded as FS-024: an evidence status (documented, tested, inferred, unknown) on important tags. Frozen until FS-016 |
| Two or three candidates per layer can yield hundreds of combinations; the enumeration cap does not bound reasoning quality | Noted; FS-016 transcripts will show whether profile choice degrades with many survivors |
| Without calibrated scoring the model can rationalize a preferred choice | Recorded as FS-025: write scores before reading `profiles` output. Frozen until FS-016 |

## Recommendations adopted

- Freeze features. Run FS-023 (live plugin smoke test), then FS-015 (first trial), then FS-016 (main evidence gate).
- FS-016 arms: plain Claude Code, the 312-token brief, 0.3.0, and 0.4.0, at matched budgets with blind grading. Measure architectural quality, missed requirements, task completion, unnecessary technology changes, tokens, turns, and cost per accepted task.
- Add an adversarial case whose declared tags look compatible but whose real operational limits make it a poor choice.
- If the brief still wins on ordinary tasks, narrow Full Stack to coupled, high-consequence decisions rather than tuning it to be universal.
