# Behavioral evaluation

The cases in [cases.json](cases.json) test decisions and artifacts rather than preferred wording. [Fixture documents](fixtures/booking-context.md) are synthetic inputs, not claims about a production repository. The [initial review](results/initial-review.md) distinguishes structural checks and author self-review from independent evidence.

## Protocol

For a forward evaluation, give a fresh evaluator the skill and one case's `prompt` plus its listed fixtures. Do not supply the rubric, the worked examples, or the author's expected solution. Run in an isolated workspace with the same tool and side-effect constraints as the compared conditions. Do not modify MochiOS or the predecessor projects for a fixture run.

Retain the exact inputs, model/version, available tools, budget, generated artifacts, actual clarification exchanges, and executed checks. If research is requested, preserve source choices and access failures. Do not provide invented user answers to make a run appear successful.

Assess the result against [rubric.md](rubric.md), citing concrete artifact passages and disagreements. Multiple defensible architectures may pass. Do not score an output wrong merely because it chooses a different technology or file layout from an example, provided the evidence and constraints support it.

For comparisons, use equivalent inputs and budgets for the baseline, each predecessor, and Full Stack. Use multiple varied cases and repeated runs where feasible; report descriptive results and variance before making general claims. Record instruction/context cost alongside quality. Neither the current case set nor a single passing run supports a statistical superiority claim.

## A/B comparison with plain Claude Code

`evals/ab/run_ab.py` runs the [fresh-user review](../docs/research/review-2026-10-05-fresh-user.md#how-a-new-user-could-test-it-in-isolation)'s paired test (FS-009). Each of five cases runs twice in fresh sessions: A is plain Claude Code, and B is the same with the skill package committed into the workspace. Both conditions get the same prompt, model, budget cap, and tools.

| Case | What it tests | Automatic checks |
|---|---|---|
| `bugfix` | Small local fix (`format_count(0)`) | Hidden acceptance checks, files changed outside the expected set |
| `feature` | Small CLI feature (`--json`), default output unchanged | Same |
| `E02n` | E02 with "Use full-stack to design only" replaced by "Design only" | None; blind grading |
| `E04` | Unavailable dependency evidence, then a follow-up turn declining the commitment | None; blind grading |
| `E06` | Routine label edit | None; blind grading |

`feature` is a CLI flag rather than the review's dark-mode toggle, because a DOM check would need a headless browser that isn't available here. Hidden checks are copied in only after a session ends.

```text
python evals/ab/run_ab.py validate                      # fixtures: starters fail, references pass (free)
python evals/ab/run_ab.py run --model <id> --budget-usd 1 --auth-from-profile
python evals/ab/run_ab.py packet evals/ab/results/<stamp>   # shuffled X/Y packet plus a separate key
```

Each session runs with an empty `CLAUDE_CONFIG_DIR` in the system temp folder, which is deleted afterwards. That means no user skills, CLAUDE.md, plugins, hooks, or memory. `--auth-from-profile` copies only the Claude login file into that throwaway folder. Records include cost, turns, whether the skill was invoked, questions the model tried to ask (these cannot be answered headless), changed files, the diff, and hidden-check output. If B never invokes the skill, record that as a discovery failure rather than a with-skill result. Grade the packet blind against [rubric.md](rubric.md), and keep `blind-key.json` away from the grader. Five pairs is a personal adoption test, not a statistical study.

## Packaging checks

Run `python evals/check_artifacts.py` and `python evals/test_run_guard.py` from the project root. The first checks that the entrypoint header parses as YAML, local Markdown links, JSON fixtures, required skill files, portable-reference containment, and unresolved scaffold markers. It does not assess architectural semantics.

The skill-creator `quick_validate.py` can additionally check the skill's frontmatter. Record the installed validator version/path and outcome when used. A successful structural check is not a successful behavioral experiment.

## Implementation trials

For implementation evaluation, supply explicit acceptance criteria, an isolated writable project, and a real runtime. Retain initial source for existing-project cases. Exercise a nonvisual tool, an existing feature, and a user-facing application with durable state; check restart in a new process where required. Use real integrations and distinguish HTTP-level checks from browser interaction.

After the initial implementation, request a bounded policy change or adapter replacement. Preserve before/after artifacts and inspect ownership and regressions. Keep this follow-up hidden until the first result when testing unanticipated change; disclose when it was supplied up front. Finish with a trivial documentation edit to check proportional effort.

The [0.2.0 revision record](results/revision-review.md) links exact trial inputs, generated artifacts, checks, and limits. Trial directories are retained experimental artifacts, not new product features or competing project roadmaps. Their local roadmaps describe only their synthetic subject projects.

## Context cost

`python evals/measure_context.py --baseline <commit>` compares the entrypoint and portable Markdown using `o200k_base` (optional development dependency: `tiktoken`). It may download tokenizer data into the ignored `.tokenizer-cache/`; this is not a portable-skill runtime dependency. Record the resolved commit and tokenizer version. Compare equivalent routes and report conditional-reference cost separately. Shorter instructions alone do not establish better token value; judge retained behavior and omissions as well.
