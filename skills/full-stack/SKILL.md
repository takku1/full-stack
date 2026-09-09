---
name: full-stack
description: Elaborate a software prompt, roadmap slice, or prototype into a scoped design across the relevant stack, with domain vocabulary, ownership, interaction contracts, targeted research, and ordered implementation work. Use for new systems or changes spanning meaningful component boundaries; skip isolated routine edits.
metadata:
  version: "0.1.0"
---

# Full Stack

Turn the requested outcome into a connected design that an implementer can follow without inventing product behavior or foundational architecture. Full stack means the layers needed to deliver the outcome, including native/platform systems when relevant. Do not assume a browser, HTTP service, or database.

## Establish scope and reality

Identify the subject repository, requested outcome, selected roadmap items, constraints, and exclusions. Read applicable project instructions and the relevant architecture, code paths, manifests, tests, and prototypes. Follow a representative flow far enough to distinguish implementation from proposal. Mark unexecuted checks as unexecuted; names and documentation alone do not establish working behavior.

Keep **current state**, **target state**, and **migration** distinct. Preserve existing authoritative documents and IDs. For established projects or Recurspec integration, read [existing-projects.md](references/existing-projects.md). Prefer a focused design delta over rewriting the architecture.

Classify discoveries as **required now**, **existing dependency**, **unresolved prerequisite**, or **deferred enhancement**. These are scope dispositions, not evidence or completion statuses. Explain why each prerequisite is necessary. An optional feature found in research does not enter the milestone automatically.

If a product ambiguity would change the outcome, first seek evidence in the supplied context; ask a focused question only if necessary. Use explicit, reversible assumptions for ordinary choices and continue independent work. Do not reopen decisions the user already made.

## Elaborate and synthesize iteratively

Use [terminology.md](references/terminology.md) for overloaded concepts and relationship meanings. For substantial decomposition, follow [design-method.md](references/design-method.md). The activities below are iterative, not a requirement to freeze one phase before starting another.

1. **Ground concepts.** Define terms whose ambiguity changes the design, with examples and distinctions. Preserve the project's language. Separate product capabilities, requirements, domain entities, components, and work packages.
2. **Trace behavior.** Describe representative tasks from trigger through state transition to observable outcome. Cover relevant failure, cancellation, retry, startup, and recovery paths. Extract visual and interaction requirements from prototypes; do not infer working backends from mock data.
3. **Allocate responsibilities.** Identify authoritative state, policy, invariants, readers/writers, and derived views. Assign one authority per state set or specify the actual coordination protocol. Architectural authority, resource ownership, and team responsibility are different questions.
4. **Resolve uncertain choices.** Research alternatives capable of changing the design using [research.md](references/research.md). Keep existing valid choices unless contrary evidence matters. Resolve consequential reuse decisions before detailing custom internals; revisit decomposition when fit gaps emerge.
5. **Specify and connect.** Use the relevant sections of [artifacts.md](references/artifacts.md). Give each important component a cohesive responsibility, boundary, consumers, interface semantics, lifecycle, and acceptance criteria. Link shared providers once; do not clone them beneath every consumer.
6. **Sequence delivery.** Derive bounded work packages from the design. Prefer a small end-to-end increment that exercises real integration. Identify prerequisite decisions and shared interface work before claiming tasks are independent. Document tests/doubles as such; never report a mocked path as operational integration.

## Control granularity and coverage

Split when responsibilities hide different decisions, authoritative state changes hands, protection/lifecycle constraints differ, or unresolved coupling prevents a coherent implementation increment. A screen region, noun, workflow step, or directory is not automatically a component. A component is not automatically a crate, service, process, or team.

Stop when the next increment has a clear outcome, usable contract, available or scheduled prerequisites, and meaningful checks; private implementation choices may remain. Stop at an adopted provider's public boundary. Keep an unresolved prerequisite explicit rather than fabricate its implementation. There is no fixed target depth, document count, or session duration.

Before calling the design ready, inspect three kinds of gaps:

- **Within a responsibility:** required states, errors, resources, lifecycle, and checks.
- **Across interactions:** producer guarantees versus consumer assumptions, identity, authority, ordering, and failure propagation.
- **Across the selected outcome:** can the complete task succeed and make its outcome observable?

Apply cross-cutting concerns only where relevant: presentation/accessibility, business rules, data/persistence, authorization, concurrency, platform compatibility, operations, migration, and performance. Record a reason for excluding a material concern. Do not inflate scope to populate a universal checklist.

## Evidence and close-out

Keep proposed behavior and assumptions distinguishable from source inspection, executed tests, measurements, and formal proof. A requirement is an obligation; an invariant is a particular property; a passing test is bounded evidence. Prose contracts do not enforce themselves.

Maintain one authoritative work registry in the subject project. Specifications define behavior; they refer to work IDs instead of maintaining duplicate status lists. Record unresolved decisions with the evidence needed and affected work.

Deliver the scope, linked design artifacts, ownership and interface decisions, research-backed choices, implementation order, and unresolved blockers. State which next increment is ready and which is conditional. Planning does not imply permission to implement, deploy, publish, install tools, or delegate work; follow the user's actual task authorization.
