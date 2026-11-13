---
name: full-stack
description: Use when designing or building a change that spans components, state, or contracts, or when choosing a technology for any layer (data, runtime, interface, client, platform). Not for isolated routine edits.
---

# Full Stack

Always:

- Restate the outcome, what is excluded, and the acceptance checks. Derive
  checks from the request; ask only if they cannot be derived.
- Read the code and the project's instructions before deciding. Never invent
  interfaces, file paths, or versions. Project instructions beat this package.
- Name the owner of each piece of state that changes, and trace each
  behavior through failure, retry, and restart.
- Discovery never authorizes extra work or migration: note it, do not build
  it. Ask before costly-to-reverse commitments (new datastore, language,
  hosting, public contract).
- Keep edits to what the outcome needs. Leave uncommitted edits and running
  processes you did not start untouched. Prefer one real end-to-end path
  over scaffolding or mocks.
- Report what actually ran. Never call an unexecuted check passed. List
  work as ready, conditional, or blocked.
- Spend few turns: read every file you need in one parallel batch, reread
  only after it changed or new evidence makes it relevant, and use the
  scripts' batch commands. Write only what someone
  will use: tables over prose, one line per unchanged item, no repetition.

A one- or two-file fix that adds no state, trust boundary, permission, or
contract needs nothing more. Otherwise load only what applies:

| Situation | Read |
|---|---|
| Design work (any request beyond a routine edit) | [flows/design.md](flows/design.md) |
| A technology must be chosen or reopened for any layer | [flows/stack.md](flows/stack.md), then only the affected layer modules |
| Any design or build beyond a routine edit | [flows/assurance.md](flows/assurance.md): screen, then only the raised disciplines |
| Building was requested | [flows/implement.md](flows/implement.md) |

Layer modules: [data](layers/data.md), [runtime](layers/runtime.md),
[interface](layers/interface.md), [client](layers/client.md),
[platform](layers/platform.md), [crosscut](layers/crosscut.md),
[custom](layers/custom.md). Assurance modules (Policy, Framework, How to,
Checks): `assurance/` security, verification, reliability, observability,
operations, performance, privacy, ux, maintainability, cost, compliance.
Templates: [stack brief](templates/stack-brief.md),
[decision record](templates/decision-record.md),
[assurance table](templates/assurance-table.md). Method references:
[terminology](references/terminology.md), [design method](references/design-method.md),
[research](references/research.md), [artifacts](references/artifacts.md),
[existing projects](references/existing-projects.md),
[implementation](references/implementation.md). Scripts:
`scripts/check_stack.py` (stack consistency), `scripts/assurance.py`
(screen resolver), `scripts/run_guard.py` (write sets and executed checks). Run them with whichever of `python3`,
`python`, or `py -3` works; on Windows `python` may be a non-working stub.

In an existing repository every layer starts as "keep current".
