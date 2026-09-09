# Design method

Use for substantial prompt elaboration, a roadmap slice, or a change crossing meaningful boundaries. Scale artifact depth to uncertainty and risk. This is a reasoning method, not a mandatory sequence of approval gates.

## Frame and ground

Write the requested outcome and exclusions before expanding the design. Identify the actual subject system and context: actors, external systems, platform, budget constraints, compatibility, and available evidence. If the roadmap has several unrelated outcomes, identify the selected ones rather than treating the file as authorization to implement everything.

Inspect enough repository reality to locate relevant owners and execution paths. Record conflicting current/target claims and investigate those that could change the next increment. Existing architecture is a constraint and source of evidence, not proof that every described feature works.

Extract terms from the request and actual artifacts. Define only ambiguities that affect behavior: identity, lifetime, state transitions, cardinality, authority, or observable completion. Map aliases; do not silently merge distinct entities. A process, application instance, and window may have different lifetimes.

## Elaborate representative tasks

Trace a requested task from its trigger to its observable result. Identify who acts, what information is needed, what state changes, who may authorize the change, and who observes completion. Add failure and alternate paths according to their relevance: absent data, stale state, duplicate action, cancellation, partial success, crash, or restart.

For a visual prototype, identify layout/appearance, demonstrated interactions, and mock behavior separately. Preserve salient visual requirements by linking the reference. Include accessibility and keyboard behavior needed for the selected task. A mock array is not evidence of a registry, persistence layer, or lifecycle service.

For a nonvisual task, use equivalent observable outputs: returned values, stored records, emitted events, device actions, or operational signals. Do not introduce a UI merely because the skill is called full-stack.

## Allocate and challenge boundaries

For each candidate responsibility ask:

1. What requirement or necessary dependency justifies it?
2. What state, policy, resource, or private design choice does it own?
3. What do consumers need, and what should remain private?
4. Does its lifetime, authority, change pressure, or failure behavior justify a separate boundary?
5. What cost does the split introduce, and could the responsibility remain cohesive inside an existing component?

Choose a primary reason for a consequential boundary and a meaningful challenge. For example, information hiding may favor separation while latency or coordinated transaction semantics favor colocation. Record the tradeoff only if it affects the recommendation.

Identify source/build, runtime, protection, and deployment mappings independently. A new source module need not become a process. Fault containment only exists when the actual isolation and recovery design supports it. Resource lifetime and Rust borrowing constraints belong in the implementation mapping without replacing architectural authority.

## Resolve and revise

Investigate choices that could invalidate a boundary or large amount of custom work. Compare feasible reuse/adaptation/build approaches under actual constraints. A selected provider bounds the custom design at its interface; remaining fit gaps become owned work only when required.

Revisit both requirement interpretation and architecture when new evidence matters. Do not weaken an explicit requirement merely because a candidate dependency lacks a feature. Present the incompatibility and alternatives. Conversely, do not preserve an invented subcomponent after research shows that an existing owner already provides the needed behavior.

## Compose the design

Match each consumer assumption to a provider guarantee or an explicit unresolved condition. Check identity, schema, versioning, error outcomes, ordering, delivery, authorization, cancellation, backpressure, and recovery where relevant. Avoid promising exactly-once effects or lossless streams without a mechanism that supports them.

Trace each selected task across the resulting contracts. Confirm both semantic completion and user/actor feedback. A successful transport acknowledgment may not mean that a launch, save, payment, or device operation completed.

Inspect lifecycle transitions, especially bootstrap, shutdown, reconnection, and stale derived state. A consumer that disconnects must know how to resume, resynchronize, or report that its view is unknown. Polling or event subscriptions can each be valid; choose based on the requirements and provider behavior.

## Sequence the next increment

Derive implementation work from the design rather than using implementation tasks as the architecture. Each package needs an outcome, affected code/contract locations, prerequisites, checks, and unresolved blockers. Mark proposed code paths explicitly.

Order required interface agreements and prerequisites before dependent integration. Runtime graphs may contain cycles; the implementation dependency graph needs a workable order. Resolve delivery cycles through a stable interface, coordinated increment, or explicit investigation. Do not declare parallel independence merely because file paths differ.

Prefer a small vertical slice that exercises real boundaries. An early test double can establish a contract but must not be reported as a working platform facility. Preserve a path to real integration and retirement of temporary adapters.

## Readiness review

For the next increment, establish:

- Selected requirements have origins, owners, and observable acceptance conditions.
- Necessary dependencies are verified available, scheduled, or explicitly blocking.
- Shared state authority and interface assumptions do not contradict each other.
- Important task and failure paths reach an observable outcome.
- Material product/architecture decisions are resolved; private implementation choices may remain.
- New work is linked from the existing registry and scope exclusions remain intact.

If this is not satisfied, deliver the supported design and identify exactly what remains conditional. Do not label the whole system complete based on sampled scenarios or documentation structure.
