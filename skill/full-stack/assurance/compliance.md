---
discipline: compliance
triggers: [named regulation, contract, or license in scope]
tier2_when: [certification or audit expected, regulated data]
---

# Compliance and assurance

## Policy

- Tier 0 unless the request, the repository, or the brief names a
  regulation, contract, or license obligation; tier 2 when an audit or
  certification is expected.
- Default: map each named control to a claim in the assurance table; keep
  license identifiers in SPDX form.
- Never: claim conformance to a standard whose text was not checked; give
  legal advice; ship a dependency whose license conflicts with the
  project's.

## Framework

Claims, arguments, and evidence (assurance cases in GSN or CAE form): each
claim is supported by evidence through an argument, and the case actively
looks for defeaters. SPDX license identifiers. The control framework the
project names (do not choose one for it).

## How to

1. List each named obligation and its source.
2. For each control that applies to the outcome, add a claim to the
   assurance table with its check or document.
3. Check dependency licenses against the project's license.
4. Tier 2: record which controls were checked against the standard's text
   and which rest on summaries; list the rest as blockers.

## Checks

- Every applicable named control maps to a claim with a check or document.
- Dependency licenses compatible, or conflicts listed.
- Unmapped controls listed as blockers, not omitted.
