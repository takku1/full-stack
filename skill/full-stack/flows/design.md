# Design flow

Load for any request beyond an isolated routine edit. The fenced block is
ordered instructions, not a program; the sections below it define each step.

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

  if any layer needs a technology chosen or reopened:
    read stack flow from flows/stack.md as stack
    apply stack orchestration with stack as scope

  generate design from scope as design

  if reuse choices outside the stack flow could change the design:
    read research guide from references/research.md as guide
    apply choice with guide as design

  read artifact patterns from references/artifacts.md as patterns
  apply shape with patterns as design

  if subject has existing contracts, providers, or registries:
    apply delta with integration as design

  verify design has scope, ownership and contracts, choices, increments, and blockers sections matching the selected scope
    otherwise:
      apply readiness repair with design as design
      retry

  if design contains a costly-to-reverse commitment not already authorized:
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

## Resources

- **design_docs**: the subject's existing design note for the affected
  component, else its documented design location, else
  `docs/design/<outcome-slug>.md`.
- **registry**: the subject's declared work registry (Recurspec
  `ROADMAP.md` first), else the tracker nearest the changed component; none
  means skip. Never create a registry file without authorization.

## Step meanings

- **update**: fold the user's answer into the request.
- **registry resolution**: pick the registry the resource line names.
- **grounding**: separate current state, target state, and migration.
- **registry entries**: link existing work IDs; never renumber.
- **term fixes / boundary method / choice / shape / delta**: apply the
  named reference or the subject's contracts.
- **split**: shrink scope to the smallest increment that delivers the
  outcome; record the rest as deferred.
- **default**: take the reversible ordinary option and record it.
- **stack orchestration**: run [stack.md](stack.md); its decision records
  become the design's choices, and its blockers join the design's blockers.
- **readiness repair**: fill a gap from evidence, or move it to blockers
  and mark the affected work blocked.
- **conditional mark**: mark work depending on the declined commitment
  conditional; independent work stays ready.
- **registry update**: update this work's entry, else add one.

`if`/`when` run their block when the condition holds. `require` stops
unless `otherwise:` repairs; `verify` checks evidence, `otherwise:` repairs,
`retry` rechecks. `ask` waits for the user. `read`/`write` touch only the
named resource; `generate` and `apply` change only the draft named after
`as`.

## Responses to the commitment question

**Authorized** makes dependent work ready. **Declined** applies the
conditional mark and files the design. **Dismissed or unanswered** stops
with nothing written and shows the design in chat. A commitment the user
already authorized in the stack flow is not asked again.

## Filing

A design stays in chat when the request says so, no repository is known,
or the subject forbids new design files and has no note to extend.
Otherwise update the component's existing design note, else write one file
at the documented design location, else `docs/design/<outcome-slug>.md`;
reruns update that file. A stack decision set goes in the same file as a
` ```json stack ` block so `scripts/check_stack.py` can read it.

## Design package shape

A substantial design returns, in order: scope (outcome, work IDs,
constraints, exclusions, dispositions), ownership and contracts, choices
(stack decision records when the stack flow ran; otherwise alternatives,
evidence, fit gaps, revisit conditions), increments (requirements, write
set, prerequisites, checks, ready / conditional / blocked), and blockers;
an empty section reads "none".

## Generate guidance

Classify every discovery as required now, existing dependency, unresolved
prerequisite, or deferred enhancement. State consequential assumptions with
their cost if false. A cache never gains authority by copying. Match every
consumer assumption to a provider guarantee or an explicit unresolved
condition. Missing compatibility evidence makes the affected selection
conditional; never invent it.

Output: a routine edit returns at most five lines (what changes, what
verifies it). Sections that do not apply read "none". Link to the brief and
the code instead of restating them.
