---
skill: full-stack
name: full-stack
description: Turn a software request into a scoped design with ownership, contracts, and ordered work; implement when asked.
version: 0.4.1
purpose: Turn a software request into a scoped design with ownership, contracts, and ordered work; implement when asked.
accepts:
  request: { type: Text, required: true }
  subject: { type: Path, required: false }
  criteria: { type: Text, required: false }
produces:
  design: { type: Text }
  report: { type: Text, when: implementing }
owns-when:
  - user wants a scoped design for a software change
  - user wants to design and implement a feature across components
  - user wants a roadmap slice elaborated into ordered work
requires:
  design: [request exists]
  implement: [request exists]
flows: [design, implement]
authority:
  user-decides: [outcome or authority to pursue, authorize a costly-to-reverse commitment, acceptance criteria for the build]
  system-decides: [whether the scope is unambiguous, whether contracts are compatible, whether the design is ready, whether checks pass]
  system-may: [choose reversible ordinary defaults, suggest scope splits]
  system-must-not: [expand scope without authorization, invent existing interfaces or source paths, treat mock data as working behavior, mark unexecuted checks as passed]
effects:
  reads: [subject, references, registry]
  creates: [design_docs]
  mutates: [subject, registry]
risk: medium
cost: expensive
budget: { header: 400, body: 2500 }
---

# Full Stack

Logic-first entrypoint: control is structured; method meaning lives in this
package's references. Conversion evidence and cost accounting are recorded
in the project's logic-conversion pilot report.

```contract
resources:
  subject:
    path: subject repository
    access: read+create
  design_docs:
    path: design documents
    access: create
  registry:
    path: subject work tracker nearest the changed component, if any
    access: read+create
  references:
    path: references/*.md
    access: read
    immutable: true
always:
  preserve authoritative documents, identifiers, and project vocabulary
  preserve settled user decisions
  keep current state, target state, and migration distinct
  link requirements, decisions, realization, and checks
  mark unexecuted checks as unexecuted
  confirm target files have no concurrent uncommitted edits
never:
  expand scope without authorization
  invent existing interfaces or source paths
  treat mock data as working behavior
  implement without a build request
  deploy, publish, or install tools beyond task authorization
  mark unexecuted checks as passed
  create a new registry file without authorization
```

```logic
design:
  require request exists
    otherwise:
      abort with "A request is required."

  if request is an isolated routine edit:
    generate minimal edit note from request as design
    if subject has a work tracker:
      apply registry update with design as entry
      write entry with registry
    return design as design

  if request is ambiguous on outcome or authority:
    ask user to clarify the outcome or authority as clarification
    apply update with clarification as request

  generate initial scope from request as scope

  if subject is known:
    read instructions from subject as context
    apply grounding with context as scope
    if subject has a work tracker:
      read existing entries from registry as entries
      apply registry entries with entries as scope

  when terms are ambiguous:
    read terminology from references/terminology.md as terms
    apply term fixes with terms as scope

  when decomposition is substantial:
    read design method from references/design-method.md as method
    apply boundary method with method as scope

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

  if scope splits suggest a smaller increment:
    apply split with scope as scope

  verify design states outcome, contracts, prerequisites, and checks
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

  run design with:
    request = request

  read implementation guide from references/implementation.md as guide
  generate implementation from design as implementation
  apply build method with guide as implementation
  apply acceptance criteria with criteria as implementation

  if subject is known:
    read contracts from subject as contracts
    apply fit with contracts as implementation

  verify implementation meets the acceptance criteria
    otherwise:
      apply correction with implementation as implementation
      retry

  write implementation with subject
  if subject has a work tracker:
    apply registry update with implementation as entry
    write entry with registry
  generate completion report from implementation as completion

  return:
    design
    report = completion
```

## Appendix: design guidance

Guidance only; no control semantics. Terms follow this package's
terminology reference; upstream notices for adapted material live in this
package's NOTICE file. References load through the references resource
when a branch needs them.

### Design package shape

Every design returns the same sections in order: scope (outcome, work
IDs, constraints, exclusions, dispositions), ownership and contracts
(authoritative state, readers, writers, derived views), choices
(alternatives, evidence, fit gaps, revisit conditions), increments
(requirements, paths, prerequisites, checks, closure evidence), and
blockers (unresolved decisions with affected work). The readiness
verify gate enforces this shape; a design missing any section is
repaired, not returned.

### Generate guidance

Ground before designing: separate current state, target state, and
migration. Classify every discovery as required now, existing
dependency, unresolved prerequisite, or deferred enhancement; discovery
never authorizes expansion. State consequential assumptions with their
cost if false; prefer reversible ordinary choices and continue.

Trace each behavior from trigger through state transitions to the
observable result, including failure, retry, cancellation, and
recovery. Allocate one authority per state set or name the coordination
protocol; a cache or projection never gains authority by copying data.
Research only uncertainty that could change the design, from primary
sources with dates and applicability limits; preserve valid existing
choices and assign fit gaps to owned work. Match every consumer
assumption to a provider guarantee or an explicit unresolved condition.
Sequence bounded end-to-end increments; resolve shared interface work
before claiming independence. Label every double with its simulated
guarantees, limits, and replacement condition.

Split where different decisions need hiding, authority changes hands,
or lifecycle differs. Screens, nouns, directories, and workflow steps
do not dictate components. A next increment is ready when its outcome,
contracts, prerequisites, and checks are usable; private choices may
remain. Check gaps within responsibilities, across contracts, and
across the outcome. Apply quality concerns only when the scenario
triggers them, and explain excluding a material concern.

### Routine edits and blocked evidence

An isolated routine edit returns a minimal note: what changes, what
verifies it, nothing else. No architecture tree, no research. When
compatibility evidence is unavailable, mark the affected selection
conditional with the exact evidence needed, and continue the
independent design; never invent the missing facts and never abandon
the whole task.

### Requests without a repository

The request input carries pasted fixtures, prototypes, and quoted
contracts when no subject path is given; grounding reads the request
itself and skips repository inspection rather than failing.

### Retry discipline

A retry re-executes its gate after the repair is applied. If the same
gate fails twice with the same evidence, stop repairing and record the
blocker with the affected work instead of looping.

### Implementation notes

Implement consumes the design flow's output; it never re-derives
scope. Connect one real path through the required boundaries first,
then finish all selected transitions, failures, and lifecycle
obligations. Reuse existing facilities. Test doubles may exercise a
contract early but never substitute for required behavior. Run the
project's checks, exercise the real user or system path, and report
implemented behavior with actual evidence and limits. State the
acceptance criteria used, flagging any derived rather than user-stated,
so the user can correct them after the fact. Record unfinished
required work, blockers, and the next resumption step in the registry.
