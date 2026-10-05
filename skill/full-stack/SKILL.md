---
skill: full-stack
name: full-stack
description: Design, and build when asked, a change spanning components, state, or contracts. Not for isolated routine edits.
version: 0.4.1
purpose: Scope a cross-component change into owners, contracts, and ordered work.
accepts:
  request: { type: Text, required: true }
  subject: { type: Path, required: false }
  criteria: { type: Text, required: false }
  design: { type: Text, required: false }
  filing: { type: "Enum[files, chat]", required: false }
produces:
  design: { type: Text }
  report: { type: Text, when: implementing }
owns-when:
  - user wants a design for a cross-component change
  - user wants to design and implement a feature across components
  - user wants a roadmap slice turned into ordered work
requires:
  design: [request exists]
  implement: [request exists]
flows: [design, implement]
authority:
  user-decides: [outcome or authority to pursue, authorize a costly-to-reverse commitment, build acceptance criteria]
  system-decides: [whether scope is unambiguous, whether contracts are compatible, whether design is ready, whether checks pass]
  system-may: [choose reversible ordinary defaults, suggest scope splits]
  system-must-not: [expand scope without authorization, invent existing interfaces or source paths, treat mock data as working behavior, mark unexecuted checks as passed, build conditional work]
effects:
  reads: [subject, references, registry, design_docs, run_log]
  creates: [design_docs]
  mutates: [subject, registry, design_docs, run_log]
risk: medium
cost: expensive
budget: { header: 400, body: 3000 }
---

# Full Stack

Structured entrypoint: the fenced blocks are instructions, not a program.
The appendix defines every step in plain language.

```contract
resources:
  subject:
    path: subject repository
    access: read+create
  design_docs:
    path: the subject's existing design note for the affected component, else its documented design location, else docs/design/<outcome-slug>.md
    access: read+create
  registry:
    path: the subject's declared work registry (Recurspec ROADMAP.md), else the tracker nearest the changed component; none means skip
    access: read+create
  references:
    path: references/*.md
    access: read
    immutable: true
  run_log:
    path: run records kept by scripts/run_guard.py under the subject's git directory
    access: read+create
always:
  follow subject instructions over this package's defaults
  preserve authoritative documents, identifiers, and project vocabulary
  preserve settled user decisions
  keep current state, target state, and migration distinct
  link requirements, decisions, realization, and checks
  read target files and registry entries before changing them
  leave uncommitted edits made outside this run, and build or run resources held by another process, untouched
  mark unexecuted checks as unexecuted
never:
  expand scope without authorization
  invent existing interfaces or source paths
  treat mock data as working behavior
  implement without a build request
  build conditional or blocked work
  deploy, publish, or install tools beyond task authorization
  mark unexecuted checks as passed
  create a registry file, or a design file the subject's instructions forbid, without authorization
```

```logic
design:
  require request exists
    otherwise:
      abort with "A request is required."

  if request is ambiguous on outcome or authority:
    ask user to clarify the outcome or authority as clarification
    apply update with clarification as request

  generate initial scope from request as scope

  if subject is known:
    read instructions from subject as context
    if subject has existing contracts, providers, or registries:
      read integration guide from references/existing-projects.md as integration
      apply registry resolution with integration as context
    apply grounding with context as scope
    if subject has a work tracker:
      read existing entries from registry as entries
      apply registry entries with entries as scope

  if request is an isolated routine edit:
    generate minimal edit note from scope as design
    if subject has a work tracker:
      apply registry update with design as entry
      write entry with registry
    return design as design

  when terms are ambiguous:
    read terminology from references/terminology.md as terms
    apply term fixes with terms as scope

  when decomposition is substantial:
    read design method from references/design-method.md as method
    apply boundary method with method as scope

  if scope splits suggest a smaller increment:
    apply split with scope as scope

  when a reversible ordinary choice applies:
    apply default with scope as scope

  generate design from scope as design

  if reuse choices could change the design:
    read research guide from references/research.md as guide
    generate resolution options from guide as options
    apply choice with options as design

  read artifact patterns from references/artifacts.md as patterns
  apply shape with patterns as design

  if subject has existing contracts, providers, or registries:
    read integration guide from references/existing-projects.md as integration
    apply delta with integration as design

  verify design has scope, ownership and contracts, choices, increments, and blockers sections matching the selected scope
    otherwise:
      apply readiness repair with design as design
      retry

  if design contains a costly-to-reverse commitment:
    show design
    ask user to authorize the costly-to-reverse commitment
    require user authorizes the costly-to-reverse commitment
      otherwise:
        apply conditional mark with design as design
        return to finish design

  label finish design:

  if design should stay in chat:
    return design as design

  write design with design_docs
  if subject has a work tracker:
    apply registry update with design as entry
    write entry with registry

  return design as design
```

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
    run design with:
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

## Appendix: reading the flows

No interpreter runs this file; the model reads the blocks as ordered
instructions. The SkillWren validator checks structure only (bindings,
declared effects, no write before a question). Hosts read `name` and
`description`; other header fields are SkillWren declarations. `version`
is the SkillWren format, not the package release. `read+create` means
readable and writable.

`if`/`when` run their block when the condition holds, `unless` when it
does not. `require` stops the flow unless its `otherwise:` repairs;
`verify` checks evidence, `otherwise:` repairs, `retry` rechecks. `ask`
waits for the user. `read`/`write` touch only the named resource;
`generate` and `apply` change only the draft named after `as`; a loaded
reference is not reread.

### What is checked mechanically

`scripts/run_guard.py` (Python 3, git) enforces the implement flow's
scope and evidence claims; its log, not memory, is the record.
**write set + write claim**: list the files and directories the
selected work may change, then `run_guard.py start --write-set ...
--label <work ID>`. Exit 3 is a collision. **check plan + write checks**:
run every acceptance check through `run_guard.py exec --criterion "<c>"
-- <command>`. The verify gate is `run_guard.py check` exiting 0 plus a
recorded passing (or blocked) check per criterion. **run report**:
`run_guard.py report`, pasted into the completion report. **run close**:
`run_guard.py finish`. `--shared` claims files other workers also
edit; an optional host hook (README) blocks out-of-scope edits.
Without the guard, check with `git status` and `git diff` and say the
run was unguarded. All else relies on the model.

### Step meanings

- **update**: fold the user's answer into the request.
- **registry resolution**: pick the registry the resource line names.
- **grounding**: separate current state, target state, and migration.
- **registry entries**: link existing work IDs; never renumber.
- **term fixes / boundary method / choice / shape / delta / build
  method / fit**: apply the named reference or the subject's contracts.
- **split**: shrink scope to the smallest increment that delivers the
  outcome; record the rest as deferred.
- **default**: take the reversible ordinary option and record it.
- **readiness repair**: fill a gap from evidence, or move it to blockers
  and mark the affected work blocked.
- **conditional mark**: mark work depending on the declined commitment
  conditional; independent work stays ready.
- **registry update**: update this work's entry, else add one.
- **recheck**: confirm a supplied design's facts still hold; revise only
  stale parts; settled decisions stay settled.
- **ready selection**: build only ready work; report the rest.
- **acceptance criteria**: tie each criterion to a check.
- **collision resolution**: narrow the write set around outside edits,
  or mark the colliding work blocked until the other run finishes.
- **correction**: repair the failing edit; the same failure twice with
  the same evidence becomes a blocked criterion, not another repair.
- **node evidence proposal**: list Recurspec node evidence updates as
  proposed, not applied.

### Response outcomes

For the costly-commitment question: **authorized** makes dependent work
ready; **declined** applies the conditional mark and files the design;
**dismissed or unanswered** stops with nothing written and shows the
design in chat. Every return lists work as ready, conditional, or
blocked.

### Filing

A design stays in chat when `filing` is chat, the request says so, no
repository is known, or the subject forbids new design files and has no
note to extend. Otherwise update the component's existing design note,
else write one file at the documented design location, else
`docs/design/<outcome-slug>.md`; reruns update that file.

### Design package shape

A substantial design returns, in order: scope (outcome, work IDs,
constraints, exclusions, dispositions), ownership and contracts,
choices (alternatives, evidence, fit gaps, revisit conditions),
increments (requirements, write set, prerequisites, checks, ready /
conditional / blocked), and blockers; an empty section reads "none". A
routine edit returns what changes and what verifies it.

### Generate guidance

Ground before designing. Classify every discovery as required now,
existing dependency, unresolved prerequisite, or deferred enhancement;
discovery never authorizes expansion. State consequential assumptions
with their cost if false. Trace each behavior from trigger to observable
result, including failure, retry, cancellation, and recovery. Give each
state set one authority; a cache never gains authority by copying.
Match every consumer assumption to a provider guarantee or an explicit
unresolved condition. Split where hidden decisions, authority, or
lifecycle differ, not by screens or directories. Missing compatibility
evidence makes the affected selection conditional; never invent it.
Without a repository, ground on what the request supplies.

### Concurrent work

Uncommitted changes this run did not make belong to someone else: never
revert, overwrite, or reformat them. Parallel workers each claim a
disjoint write set; files every package needs (manifests, lockfiles,
registries, generated code) get one owning package, and the others
sequence after it. A binary, emulator, or port held by another process
means wait; never kill it.
