# Assurance flow

Load for any design or build beyond a routine edit. The layers decide where
the system is built; this flow decides which engineering disciplines must
show evidence that it is trustworthy, and how deeply. It is selective: a
local tool trips almost nothing, a payment system trips most of it.

## 1. Screen

Answer every question from the request, the stack brief, and the code;
unknown counts as yes until evidence says otherwise. Then resolve the
answers with `scripts/assurance.py screen --yes <ids> --no <ids>
[--unknown <ids>] [--high <disciplines>] [--build]`. It applies the
rules in `rules/assurance.json` (including dependencies such as privacy
requiring security) and prints the Screen line and the modules to load.
Without Python, apply the table by hand: a "yes" raises the listed
disciplines to at least tier 1.

| Question (ID) | Raises |
|---|---|
| `boundary` Reachable from the internet or another trust boundary? | security, observability |
| `tenants` More than one user or tenant whose data must stay separate? | security, verification |
| `personal_data` Stores personal data? | privacy, security |
| `money` Moves money or performs irreversible actions? | security, reliability, verification |
| `slo` States an availability or latency target? | reliability, performance, observability |
| `schema` Changes persistent schema or data? | operations, reliability |
| `external` Calls external services or networks? | reliability |
| `ui` Has a human-facing interface? | ux |
| `unattended` Deployed or operated by someone else, or runs unattended? | operations, observability |
| `regulation` A named regulation, contract, or license in scope? | compliance |
| `new_boundary` A new boundary or dependency the design must protect over time? | maintainability |
| `paid` Hosted or paid infrastructure, or paid APIs? | cost |
| `untrusted_code` Runs code, plugins, or content it does not control? | security, verification |
| `confidential` Reads, stores, or exposes secrets or confidential files? | security, observability |

**Tier 2** for a raised discipline when the consequence of failure is high:
money, health, safety, regulated data, many users, or an irreversible
action; name those disciplines with `--high`. Verification is never tier 0
for a build request (`--build`).

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

The table goes in the design's **assurance** section; `scripts/assurance.py
check DESIGN.md` reports raised disciplines with no row and rows with no
check. When building, declare the table with `run_guard.py start ...
--assurance DESIGN.md` and make every row's check an acceptance
criterion that names its ID: `run_guard.py checks --each "A-1 <claim> ::
<command>"`. `close` refuses while the table has gaps or a row's latest
check is missing or failing; documented evidence exempts only tier 1 rows.

## Red flags

| If you think | Instead | Seen in |
|---|---|---|
| "The design is small; I'll screen after building." | Screen and declare first; the guard hook blocks edits until you do. | Field report 3 (G1) |
| "I read the modules and applied the controls; the table is ceremony." | The table turns controls into claims with checks; `close` refuses a row without a passing check. | FS-015 (P2) |
| "This is routine." | Routine is one or two files with no new state, boundary, trust, or contract. Otherwise screen; a routine reason is reported. | Anticipated (external review 3) |

Output cap: the answer IDs and the Screen line; one table row per claim; no
restating module text.
