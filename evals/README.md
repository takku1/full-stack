# Behavioral evaluation

The cases in [cases.json](cases.json) test decisions and artifacts rather than preferred wording. [Fixture documents](fixtures/booking-context.md) are synthetic inputs, not claims about a production repository. The [initial review](results/initial-review.md) distinguishes structural checks and author self-review from independent evidence.

## Protocol

For a forward evaluation, give a fresh evaluator the skill and one case's `prompt` plus its listed fixtures. Do not supply the rubric, the worked examples, or the author's expected solution. Run in an isolated workspace with the same tool and side-effect constraints as the compared conditions. Do not modify MochiOS or the predecessor projects for a fixture run.

Retain the exact inputs, model/version, available tools, budget, generated artifacts, actual clarification exchanges, and executed checks. If research is requested, preserve source choices and access failures. Do not provide invented user answers to make a run appear successful.

Assess the result against [rubric.md](rubric.md), citing concrete artifact passages and disagreements. Multiple defensible architectures may pass. Do not score an output wrong merely because it chooses a different technology or file layout from an example, provided the evidence and constraints support it.

For comparisons, use equivalent inputs and budgets for the baseline, each predecessor, and Full Stack. Use multiple varied cases and repeated runs where feasible; report descriptive results and variance before making general claims. Record instruction/context cost alongside quality. Neither the current case set nor a single passing run supports a statistical superiority claim.

## Packaging checks

Run `python evals/check_artifacts.py` from the project root. This checks local Markdown links, JSON fixtures, required skill files, portable-reference containment, and unresolved scaffold markers. It does not assess architectural semantics.

The skill-creator `quick_validate.py` can additionally check the skill's frontmatter. Record the installed validator version/path and outcome when used. A successful structural check is not a successful behavioral experiment.
