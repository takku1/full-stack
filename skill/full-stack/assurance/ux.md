---
discipline: ux
triggers: [human-facing interface]
tier2_when: [public audience, legal accessibility obligation, many users]
---

# User experience and accessibility

## Policy

- Tier 1 for any human-facing interface; tier 2 for public products or a
  legal accessibility obligation.
- Default: native controls over custom ones; every representative task
  works by keyboard; every async action has loading, empty, error, and
  success states.
- Never: color as the only signal; an error that does not say what to do
  next; a custom control without a name and role.

## Framework

Task-centered design (start from three to five representative tasks).
WCAG 2.2 level AA. Nielsen's heuristics for feedback, error prevention,
and recovery.

## How to

1. Name the representative tasks touched by the outcome.
2. For each, list its states: loading, empty, error, success, offline if
   relevant.
3. Check keyboard path, labels, focus order, and contrast.
4. Tier 2: full WCAG 2.2 AA pass on the affected screens and a screen
   reader walkthrough of each task.

## Checks

- Automated accessibility scan of affected screens passes or findings are
  listed.
- Keyboard-only walkthrough of each representative task succeeds.
- Each error state names the problem and the next step.
