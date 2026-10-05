# Full Stack roadmap

This file tracks incomplete project work. Package 0.3.0 ([D-015](docs/design-decisions.md#d-015-fresh-user-review-and-second-field-report-package-030)) applies the [fresh-user review](docs/research/review-2026-10-05-fresh-user.md); retained [trial evidence](evals/results/revision-review.md) predates it. No sample establishes comparative effectiveness.

| ID | Work | Status | Acceptance |
|---|---|---|---|
| FS-001 | Independent forward evaluation on the supplied behavioral cases | Partial | Seven raw-input responses retained, but they share one agent context and author scoring; finish isolated per-case runs and independent scoring with disagreements retained |
| FS-002 | Comparative evaluation against baseline, Recurspec, and Architectural Reasoning | Research | Comparable model/tool budgets; scope, ownership, omission, provenance, and handoff outcomes reported without unsupported significance claims |
| FS-003 | Real MochiOS roadmap-slice pilot | Ready when selected | Chosen outcome mapped to current code and contracts, provider seams verified, design deltas linked to existing work IDs |
| FS-004 | Nonvisual/native and transactional-web transfer trials | Partial | Python CLI and SQLite HTTP samples exercised; still test native/Rust execution and transactional-web concurrency/uncertain outcomes without scope expansion |
| FS-005 | Verify host discovery/invocation | Partial | Claude Code, 2026-10-05: discovery listed the 0.3.0 description; `/full-stack` invocation loaded the installed 0.3.0 body and ran a design-only flow on SkillWren through the costly-commitment ask and filing. The same run caught an unquoted `Enum[...]` that broke host YAML parsing (the host fell back to the H1 as description); fixed and now checked by `evals/check_artifacts.py`. Still to do: Codex discovery/invocation and `install.sh` on macOS/Linux |
| FS-006 | Refine terminology from observed semantic failures | Depends on FS-001/FS-003/FS-004 | Narrow changes tied to counterexamples; retest preserved behavior |
| FS-007 | Controlled implementation and change trials | Ready | Freeze all instruction bytes before reads; reveal follow-up only after first completion; compare equivalent budgets and retain external scoring. Current synthetic trials reveal follow-ups up front |
| FS-008 | Browser interaction for the stateful trial | Ready when browser tools available | Exercise rendered add/delete forms, visible validation, keyboard operation and restart; current evidence covers real HTTP only |
| FS-009 | Context-dose comparison against plain Claude Code | First run done 2026-10-05 | [Results](evals/results/context-dose-2026-10-05.md): a 312-token brief beat both plain and the full skill on six small and medium cases (one session per cell). Next: repeat sessions, add a large or multi-worker task, and separate length from SkillWren format |
| FS-010 | Guard the implement flow in live use | Ready | Use `run_guard.py` in a real multi-worker run (MochiOS or SkillWren BF-1..6); confirm collisions are caught and that the report replaces from-memory check claims; tune the overlap rule from observed false positives |

No CLI, graph database, or automated ontology reasoner is planned without demonstrated need.
