---
name: full-stack
description: Design, and build when asked, a change spanning components, state, or contracts. Not for isolated routine edits.
---

# Full Stack (brief)

Before changing code:

- Restate the outcome, what is excluded, and the acceptance checks. Derive
  checks from the request; ask only if they cannot be derived.
- Read the code involved. Do not invent interfaces or file paths.
- Name who owns each piece of state that changes, and trace each behavior
  through its failure, retry, and restart paths.
- Discovery never authorizes extra work: note optional improvements, do
  not build them. Ask before costly-to-reverse commitments.

While changing code:

- Keep edits to the files the outcome needs. Leave uncommitted edits you
  did not make untouched.
- Prefer the smallest real end-to-end change over scaffolding or mocks.

Before reporting:

- Run the existing checks and exercise the real path. Report what ran and
  its result; never call an unexecuted check passed.
- List anything left unfinished or blocked.

For a design-only request, return the outcome, ownership and contracts,
choices with evidence, ordered increments with checks, and open blockers;
mark work that depends on unverified facts as conditional.
