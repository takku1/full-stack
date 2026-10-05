# Context-dose comparison, 2026-10-05

First run of `evals/ab/run_ab.py` (FS-009). The question is not "skill or no skill" but how much added context pays for itself: **plain** (no skill, direct coding), **brief** (a 312-token reminder skill with the same name and description, `evals/ab/arms/brief/SKILL.md`), and **skill** (full-stack 0.3.0, about 3,400 tokens of entrypoint plus references on demand).

## Setup

- Subject model Claude Sonnet 5.5, Claude Code 2.1.289 headless, $1 cap per session, one session per case and arm, each in an empty throwaway profile.
- Six cases: three implementation tasks with hidden acceptance checks (`bugfix`, `feature`, `crosscut`: archiving across storage, CLI, and legacy data) and three design cases (E02 neutralized, E04 with a declining follow-up, E06).
- Two runs. **Neutral**: identical prompts, so the skill arms only help if the host picks the skill. **Explicit**: the skill arms' prompts start with `/full-stack`, which tests content rather than discovery.
- Grading: one fresh Claude Opus 5.5 session per case. It saw only the shuffled X/Y/Z packets (answers, diffs, hidden-check output) and the rubric, and scored 0 to 10 with high-impact failures listed.
- Records: `evals/ab/results/2026-10-05-neutral/` and `2026-10-05-invoked/` (`results.md`, `grades.json`, transcripts, workspaces).

## Results

| Arm | Mean grade, neutral | Mean grade, explicit | Cost vs plain, neutral / explicit | High-impact failures | Hidden checks |
|---|---|---|---|---|---|
| plain | 7.3 | 7.3 | baseline ($0.72 / $0.69 for 6 cases) | 3 | 6/6 |
| brief | 8.2 | 8.8 | +8% / +12% | 0 | 6/6 |
| skill | 8.0 | 7.7 | +20% / +55% | 0 | 6/6 |

- **Brief ranked first in all six explicit cases**, and first or second in five of six neutral ones.
- **Plain's high-impact failures** were the kind the skill targets. `feature`: it rewrote whole files (line endings) while claiming nothing else changed. E04: it labeled library-dependent work unconditional until the follow-up. E06: it reported a search result its evidence contradicted.
- **Every arm passed every hidden check.** These implementation tasks do not separate the arms on correctness; the differences are in scope honesty, evidence, and design quality.
- **Discovery.** With neutral prompts the hosts picked a skill only for design cases (E02n full skill, E04 brief and full skill), never for implementation tasks, including `crosscut`.
- **Guard in live use.** In explicit `crosscut`, the full skill ran `run_guard.py`. It caught a stray `tasks.json` that the model's smoke test left behind (true positive). It also exposed a bug: a write set given as `tasks`, without a trailing slash, did not cover `tasks/*.py`. Fixed, with a regression test. The model reported the violations instead of claiming a clean run.

## Limits

One session per cell, one subject model, small tasks, and grading by a model. The grader sometimes inferred which responses had a skill loaded, because answers mentioned skill files, so blinding was partial. The brief arm differs from the full skill in both length and format (prose versus SkillWren structure), so this run cannot say which mattered. Nothing here tests large or multi-worker tasks, where the full method's distinctive parts (registry, design files, guard, parallel write sets) are meant to pay off.

## Reading

On small and medium tasks, a few hundred tokens of the right reminders captured all of the measured benefit over direct coding, at about a tenth of the full skill's extra cost. The full method added process (filing, write-set and ready/conditional/blocked headings on a bug fix) that the grader scored slightly lower. That points to a tiered design: a short core that every run loads, with the full method loaded only for cross-component, multi-worker, or design-heavy work. That is a proposal, not a result. Confirming it needs repeated sessions and at least one large task.
