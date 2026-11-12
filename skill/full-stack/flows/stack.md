# Stack flow

Load when a technology must be chosen or reopened for at least one layer:
a new system, a new component, or an outcome the current stack cannot meet.
One orchestrator (you) owns the brief, the cross-layer contracts, and the
final choice. Layer modules supply method; they never decide alone, because
layer choices are coupled and the best choice in isolation can break a
neighbor.

## 1. Write the stack brief

Fill [the stack brief](../templates/stack-brief.md) once; only the
orchestrator edits it. Quality scenarios must be observable ("p95 read under
200 ms at 50 requests/s", not "fast"). Mark a scenario target as proposed
when the user did not state it. List two to four futures: plausible changes
such as tenfold load, a team handover, a new client type, or an offline
requirement. Set the innovation budget (default one non-boring choice).

Mark each layer:

- **keep current**: an existing choice meets the outcome. In a repository
  this is the default. Record what it `provides` so neighbors can rely on it.
- **affected**: the outcome needs a new choice here, or the current choice
  cannot meet a required scenario (record the evidence; that finding is a
  prerequisite, not authorization to migrate).
- **out of scope**: the outcome does not touch it.

Read the modules for all affected layers, and only those, in one parallel
batch from `layers/`. Use [custom.md](../layers/custom.md) for a layer the
defaults do not fit. If every layer is keep current, skip to the design:
nothing here applies.

## 2. Pass 1: candidate sets

For each affected layer, follow its module's questions, then name two or
three candidates. For each candidate record:

- evidence checked now: current release and its date, maintenance activity,
  license, documented limits. Cite where it was found. A version or fact
  from memory is marked unverified, and the candidate stays conditional.
- `provides`: the guarantees it gives neighbors, as kebab-case tags. Reuse
  tags from `rules/compatibility.json` where they apply.
- `assumes`: per neighbor layer, the tags it needs from that neighbor.
- `novel`: true if the team or project has not run it in production.

Record evidence as one table row per candidate (version, date checked,
license, key limit, source URL), not page summaries. Research for
independent layers may run in parallel subagents where the host allows,
preferably on a smaller model (the Claude Code plugin ships one,
`stack-evidence`). Each returns only those rows, never a decision. Without
subagents, batch the lookups.

## 3. Intersect

Write the candidates into a ` ```json stack ` block (shape below) and run:

```
python scripts/check_stack.py profiles <file>
```

It lists the combinations that satisfy the rules, every neighbor
assumption, and the innovation budget, along with what eliminated the rest.
If none survive, revise a candidate set or the brief, never the evidence.
Without Python, apply the same three checks by hand and say so.

Choose one joint profile from the survivors:

1. best fit to the quality scenarios, weighed against cost, operational
   burden, and team familiarity;
2. then lowest maximum regret across the futures: for each future, how far
   the profile falls short of the best surviving profile in that future;
3. then fewer novel choices.

Layers never pick their own optimum independently of this step.

## 4. Authorize

A new datastore, language, hosting platform, paid service, or public
contract is usually costly to reverse. Show the profile and ask the user to
authorize each such commitment. Declined commitments mark the dependent
layers conditional; continue with independent ones. Dismissed means stop
and show the profile in chat with nothing written.

## 5. Pass 2: decision records

For each affected layer, write a record from
[the decision record template](../templates/decision-record.md) against the
committed profile: context, candidates with evidence, scores, regret,
decision and status, neighbor assumptions, consequences, revisit
conditions, novelty. Keep-current layers get one line: the choice and what
it provides.

## 6. Check

Update the ` ```json stack ` block with the final choices and run:

```
python scripts/check_stack.py check <file>
```

Exit 0 is required before the design is ready. An unmet assumption is fixed
by changing a choice, or by marking the assuming layer `conditional` or
`blocked` with the gap listed as a blocker. Report the command and its
output; a check that did not run is reported as not run.

## Stack block shape

```json
{
  "brief": {
    "outcome": "Shared shopping list usable offline on phones",
    "tags": ["offline-operation", "user-accounts"],
    "innovation_budget": 1,
    "futures": ["10x users", "web client added"]
  },
  "layers": {
    "data": {
      "status": "accepted",
      "choice": "SQLite on device + PostgreSQL server",
      "provides": ["transactional-writes", "local-replica", "conflict-resolution"],
      "assumes": {"interface": ["sync-capable"]},
      "novel": false,
      "candidates": [
        {"name": "SQLite on device + PostgreSQL server",
         "provides": ["transactional-writes", "local-replica", "conflict-resolution"],
         "assumes": {"interface": ["sync-capable"]}, "novel": false},
        {"name": "Hosted document store with offline SDK",
         "provides": ["local-replica", "conflict-resolution"], "assumes": {}, "novel": true}
      ]
    },
    "interface": {"status": "accepted", "choice": "HTTP sync API with per-item versions",
                  "provides": ["http-request-response", "sync-capable", "idempotent-writes"],
                  "candidates": [{"name": "HTTP sync API with per-item versions"}, {"name": "Change feed over WebSocket"}]},
    "client": {"status": "accepted", "choice": "Native mobile app", "provides": ["native-mobile", "offline-first"],
               "candidates": [{"name": "Native mobile app"}, {"name": "Installable web app"}]},
    "runtime": {"status": "keep-current", "choice": "Existing Python service", "provides": ["python"]},
    "platform": {"status": "keep-current", "choice": "Existing VM", "provides": ["long-lived-connections", "single-instance"]},
    "crosscut": {"status": "keep-current", "choice": "Existing OAuth provider", "provides": ["authentication"]}
  },
  "rules": []
}
```

Statuses: `keep-current`, `proposed`, `accepted`, `conditional`,
`blocked`, `out-of-scope`. `brief.tags` lets rules key on the brief.
`rules` holds project-local rules, each with cited evidence in `why`.
