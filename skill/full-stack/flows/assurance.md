# Assurance flow

Load for any design or build beyond a routine edit. The layers decide where
the system is built; this flow decides which engineering disciplines must
show evidence that it is trustworthy, and how deeply. It is selective: a
local tool trips almost nothing, a payment system trips most of it.

## 1. Screen

Answer each question from the request, the stack brief, and the code. A
"yes" raises the listed disciplines to at least tier 1. Record the answers
in one line each; unknown counts as yes until evidence says otherwise.

| Question | Raises |
|---|---|
| Reachable from the internet or another trust boundary? | security, observability |
| More than one user or tenant whose data must stay separate? | security, verification |
| Stores personal data? | privacy, security |
| Moves money or performs irreversible actions? | security, reliability, verification |
| States an availability or latency target? | reliability, performance, observability |
| Changes persistent schema or data? | operations, reliability |
| Calls external services or networks? | reliability |
| Has a human-facing interface? | ux |
| Deployed or operated by someone else, or runs unattended? | operations, observability |
| A named regulation, contract, or license in scope? | compliance |
| A new boundary or dependency the design must protect over time? | maintainability |
| Hosted or paid infrastructure, or paid APIs? | cost |

**Tier 2** for a raised discipline when the consequence of failure is high:
money, health, safety, regulated data, many users, or an irreversible
action. Verification is never tier 0 for a build request.

## 2. Load and apply

Read the modules for every discipline at tier 1 or 2, and only those, in
one parallel batch from `assurance/`. Each has the same parts: **Policy**
(when, defaults, must and never), **Framework** (the established method),
**How to** (tier 1 steps, then what tier 2 adds), and **Checks**.

Modules: [security](../assurance/security.md),
[verification](../assurance/verification.md),
[reliability](../assurance/reliability.md),
[observability](../assurance/observability.md),
[operations](../assurance/operations.md),
[performance](../assurance/performance.md),
[privacy](../assurance/privacy.md), [ux](../assurance/ux.md),
[maintainability](../assurance/maintainability.md),
[cost](../assurance/cost.md), [compliance](../assurance/compliance.md).

## 3. Assurance table

Fill [the assurance table](../templates/assurance-table.md): one row per
claim the design makes about a raised discipline. Each row names what could
make the claim false, the control and its owning component, the check that
evidences it, and its evidence status (documented, tested, inferred,
unknown). A claim with no check is a blocker, not a pass. Controls that
change scope (a new service, store, or vendor) follow the core's
costly-commitment rule.

## 4. Hand off

The table goes in the design's **assurance** section. When building, every
row's check is an acceptance criterion: run them with
`run_guard.py checks --each "<claim> :: <command>"`. A failing assurance
check blocks `close` like any other criterion.

Output cap: screen in at most twelve lines; one table row per claim; no
restating module text.
