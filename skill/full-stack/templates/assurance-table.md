# Assurance table template

One row per claim about a raised discipline. Claims are specific and
falsifiable ("a user cannot read another user's lists"), not qualities
("secure"). This is a lightweight claims-arguments-evidence case: the
"could fail by" column is where you look for reasons the claim is false.

```markdown
## Assurance

Screen: security T1 (boundary, tenants); verification T1 (build, tenants); reliability T1 (external); observability T1 (boundary); others T0

| ID | Discipline | Claim | Could fail by | Control (owner) | Check | Evidence |
|---|---|---|---|---|---|---|
| A-1 | security | A user cannot read another user's lists | ID guessing on GET /lists/{id} | Ownership check in ListService (runtime) | test_other_users_list_is_404 | tested |
| A-2 | reliability | A retried payment never charges twice | Lost response, client retries | Idempotency key stored with the charge (data) | test_replayed_charge_is_single | unknown |
```

Evidence status: **documented** (the provider's docs say so, linked),
**tested** (a check ran and passed in this run), **inferred** (reasoned,
not checked), **unknown**. Only **tested** satisfies a tier 2 claim. A row
without a check is listed under blockers. Paste the Screen line from
`scripts/assurance.py screen`; `scripts/assurance.py check` finds gaps, and
each row's ID goes in its check's criterion so the run guard can match them.
