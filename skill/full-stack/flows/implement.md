# Implement flow

Load only when building was requested. Without a build request, stop at the
design. The fenced block is ordered instructions; the sections below define
each step.

```logic
implement:
  require request exists
    otherwise:
      abort with "A request is required."

  unless criteria are known:
    generate criteria from request and prior conversation as criteria
    if criteria cannot be derived:
      ask user to state the acceptance criteria as criteria

  if request is ambiguous on outcome or authority:
    ask user to clarify the outcome or authority as clarification
    apply update with clarification as request

  unless design is known:
    run design from flows/design.md with:
      request = request

  apply recheck with design as design
  apply ready selection with design as selected

  read implementation guide from references/implementation.md as guide
  generate implementation from selected as implementation
  apply build method with guide as implementation
  apply acceptance criteria with criteria as implementation

  if subject is known:
    read contracts from subject as contracts
    apply fit with contracts as implementation

  apply write set with implementation as claim
  write claim with run_log
  verify run_log shows no collision with outside edits or open runs
    otherwise:
      apply collision resolution with implementation as implementation
      apply write set with implementation as claim
      write claim with run_log
      retry

  write implementation with subject
  apply check plan with criteria as checks
  write checks with run_log

  verify run_log shows every change inside the write set and each acceptance criterion met or blocked by an executed check
    otherwise:
      apply correction with implementation as implementation
      write implementation with subject
      write checks with run_log
      retry

  if subject has a work tracker:
    apply registry update with implementation as entry
    write entry with registry
  read run report from run_log as evidence
  generate completion report from evidence as completion
  apply run close with claim as claim
  write claim with run_log
  if subject uses Recurspec:
    apply node evidence proposal with implementation as completion

  return:
    design
    report = completion
```

## What is checked mechanically

`scripts/run_guard.py` (Python 3, git) enforces scope and evidence claims;
its log, not memory, is the record. A guarded run takes three calls:

1. **write set + write claim**: `run_guard.py start --write-set <paths>
   --label <work ID>`. Exit 3 is a collision. `--shared` claims files other
   workers also edit.
2. **check plan + write checks**: all acceptance checks in one call,
   `run_guard.py checks --each "<criterion> :: <command>" --each ...`
   (or `--plan checks.json`). Rerun it after a correction.
3. **verify gate + run report + run close**: `run_guard.py close` prints
   the report to paste into the completion report and finishes the run only
   if scope is clean and checks were recorded. If not, fix the problem, or
   report it as a blocker and rerun with `--accept-blockers`.

Without the guard, check with `git status` and `git diff` and say the run
was unguarded.

When the design contains a stack block, rerun
`scripts/check_stack.py check` after any change to a layer choice; a
dependency added during implementation that is not in the accepted profile
is a scope change and goes back to the user.

## Step meanings

- **recheck**: confirm a supplied design's facts still hold; revise only
  stale parts; settled decisions stay settled.
- **ready selection**: build only ready work; report conditional and
  blocked work.
- **build method / fit**: apply the implementation reference or the
  subject's contracts.
- **acceptance criteria**: tie each criterion to a check.
- **collision resolution**: narrow the write set around outside edits, or
  mark the colliding work blocked until the other run finishes.
- **correction**: repair the failing edit; the same failure twice with the
  same evidence becomes a blocked criterion, not another repair.
- **registry update**: update this work's entry, else add one.
- **node evidence proposal**: list Recurspec node evidence updates as
  proposed, not applied.

Control words read as in [design.md](design.md). Parallel workers and
shared files follow the implementation reference. A port or binary held by
another process means wait; never kill it. Never deploy, publish, or install
tools beyond the task's authorization.
