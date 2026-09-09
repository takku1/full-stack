# Project framing

## Purpose

Translate incomplete software intent into a scoped design that an implementer can follow without inventing unresolved product behavior or foundational architecture. Cover the layers actually needed to deliver the outcome: interaction, domain behavior, state, application coordination, infrastructure, platform integration, and verification.

The public name is **Full Stack**. The technical description is **requirements elaboration and architectural synthesis with traceability**. Elaboration makes intent explicit; synthesis selects a coherent arrangement of responsibilities and mechanisms; traceability preserves the reasons and relationships behind the result.

## Problem

A prompt often mixes outcomes, widgets, technologies, and tasks. A flat roadmap can give a complete subsystem and a small visual change equal apparent weight. A visual prototype can show an application as running without defining the application identity, launch outcome, or observation protocol behind that indicator. Existing documents may mix the current implementation with a future target.

The skill must resolve these category errors before producing implementation packets. The desired output is a connected explanation of what must happen, what owns each part, what already exists, what remains uncertain, and what should be built next.

## Scope

Inputs may include a new-product prompt, an explicitly selected roadmap outcome, design images or HTML, architecture contracts, source code, tests, build configuration, and platform constraints. Analysis scales from a small change crossing two components to a system design explicitly requested by the user.

Research follows the decisions that could change the design. Broad literature exploration belongs to an explicit research assignment, such as this project's initial foundations. Ordinary invocation should not reproduce the entire research program.

Planning is the default deliverable. A request to build or implement activates the conditional [implementation workflow](../skills/full-stack/references/implementation.md) within the selected scope; already authorized work needs no repeated approval. Dependency/tool installation, deployment, publication, and delegation follow applicable task and host permissions. The skill supplies instructions; the host supplies repository access, execution tools, and runtime capabilities.

## Output contract

The deliverable must make the following questions answerable, using as few artifacts as the scope permits:

| Question | Representation |
|---|---|
| Which outcome is being delivered now? | Scope statement and selected requirement IDs |
| What do the important words mean? | Domain vocabulary with examples and distinctions |
| How will a user or external actor complete the task? | Scenario and interaction flow |
| Who controls state and enforces rules? | Responsibility allocation and component specifications |
| Which existing facilities can satisfy the design? | Current-state evidence and technology decisions |
| What happens across a boundary? | Interface semantics, including failure and lifecycle behavior |
| Why does each piece exist? | Links to requirements, constraints, or justified prerequisites |
| How will it be delivered and checked? | Ordered work packages and observable acceptance criteria |

Scope disposition, evidence status, and delivery status are separate fields. A future requirement may have excellent evidence; a current requirement may be unimplemented; a completed task may still lack runtime verification.

## Meaning of completeness

Completeness is relative to the selected outcomes, explicit constraints, considered scenarios, and known environment. It is not an assurance that every possible feature or failure has been discovered.

The design is ready for the next implementation increment when its required behavior has an owner, its critical interactions have defined outcomes, prerequisites are available or explicitly scheduled, and no unresolved decision would force the implementer to choose a different product or architecture. Remaining private implementation choices are expected.

For an implementation request, readiness starts delivery. Completion requires the selected acceptance criteria to be exercised through real integration, with remaining requirements or unavailable checks recorded honestly. A first increment, a successful build, and a mock-backed demonstration do not establish milestone completion.

## Initial non-goals

This project does not build a new agent runtime, compiler, graph database, task runner, formal verifier, or universal technology catalog. It does not convert every component into a service, prescribe a fixed stack, or replace a subject repository's architecture with its own terminology. It does not promise that a carefully worded skill guarantees model understanding.

## Success criteria

The evaluation should measure retained scope, omitted prerequisites, contradictory ownership, unsupported claims, traceability, and implementation handoff usability. Document count, tree depth, vocabulary size, and confident prose are not success metrics. [The evaluation protocol](../evals/README.md) specifies the initial cases and the limits of the evidence.
