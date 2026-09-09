# Design decisions

These decisions record the initial 0.1.0 design and the 0.2.0 extension in D-011/D-012. They are project conventions motivated by the [research](research/foundations.md), not claims of experimentally demonstrated superiority.

## D-001: Create a standalone design skill

Full Stack owns bounded requirements elaboration, architectural synthesis, and delivery planning. Recurspec owns its contract/execution workflow. Architectural Reasoning supplies useful boundary and ownership discipline. Keeping the new skill independently usable avoids requiring a CLI, candidate branch, or merge process merely to prepare a design.

Alternative: rewrite Recurspec as the sole entry point. Rejected for this initial version because the new request concerns design semantics and scope control, while Recurspec also serves a distinct execution purpose. Revisit if usage shows that maintaining separate entry points causes more confusion than it removes.

## D-002: Prefer established vocabulary with explicit local definitions

Use requirements, scenarios, components, interfaces, authority, refinement, and traceability. Define overloaded terms and distinguish product, architecture, runtime, resource, and work views. Preserve a subject project's language through mappings rather than forced renaming.

Alternative: reuse all Recurspec domain terms as the sole vocabulary. Its [CONTEXT.md](../../recurspec/CONTEXT.md) reserves Contract Node and Atomic Leaf for specific workflow concepts; extending those names to every UI concept or work package would blur their meaning. Full Stack keeps them only when integrating with that workflow.

## D-003: Treat decomposition as an iterative design decision

Recurspec's [design reference](../../recurspec/src/recurspec/skill/references/design.md) already covers raw goals, technology research, vertical/horizontal coverage, and decomposition guards. This is an important existing capability, not an absent feature being invented here.

Full Stack changes the ordering: sketch responsibilities, investigate consequential reuse choices, and revise requirements and boundaries together. Resolve expensive custom commitments before detailed decomposition, while permitting preliminary decomposition needed to understand what to research. Reject both automatic build-first expansion and mandatory procurement research before any conceptual analysis.

## D-004: Keep multiple connected views

A component hierarchy is useful for responsibility allocation, but interaction flows, state authority, code mapping, and delivery precedence have different relations. Full Stack preserves these distinctions and links shared providers once. This extends the underlying insight of Recurspec's relationship index while keeping the design representation independent of its contract schema.

Alternative: make one canonical graph database. Unnecessary for a Markdown-first skill; revisit only after actual relation maintenance problems justify tooling.

## D-005: Make scope disposition explicit

The skill separates required behavior, existing dependencies, unresolved prerequisites, and deferred enhancements. It does not interpret “full stack” as “all possible features.” A necessary dependency can be understood without being rewritten. An unresolved prerequisite can block a specific increment while other design work continues.

The four labels are a local planning convention. They do not replace a project's evidence stages or task statuses. Preserve existing status systems and map these meanings when needed.

## D-006: Define readiness by usable boundaries

Do not prescribe one test-driven session per component, a fixed recursion depth, or a number of documents. Require a coherent next increment with defined behavior, dependencies, ownership, and meaningful checks. Leave private implementation choices to the implementer. Expose unresolved product or architectural choices.

Recurspec's bounded leaves and depth guards are useful within its workflow. Full Stack uses a different readiness criterion for design because a permanent architectural responsibility and a short-lived work package are not the same artifact. No study here determines a universally optimal granularity.

## D-007: Import ownership discipline selectively

Architectural Reasoning's [subsystem template](../../archetect/skills/architectural-reasoning/references/subsystem-specification.md) covers state authority, interfaces, resource/concurrency semantics, failure, observability, performance, and migration. Full Stack adapts this depth where the selected scope needs it.

Its primary-lens/counter-lens technique becomes a concise challenge to consequential boundary decisions. It does not require mechanically applying every lens or writing every template section. Logical, source, process, protection, and deployment boundaries remain distinct.

## D-008: Re-ground generated artifacts between stages

A generated glossary or decomposition is a proposal with provenance, not evidence of domain truth. Before deriving technical mappings, compare important concepts and assumptions against the original request, repository, and research. Record conflicts rather than allowing a plausible early inference to harden into an invented requirement.

This responds to the failure mode discussed in the research report. It does not require a user approval at every stage. Ordinary supported decisions proceed within the task's authority; material unresolved product questions are raised specifically.

## D-009: Research decisions rather than fill quotas

Use primary sources, preserve dates and applicability limits, and compare viable alternatives for consequential choices. Do not require two vendors or pinned versions for a stable conceptual responsibility. A technology decision still needs current compatibility evidence before adoption.

Academic depth is appropriate to this initial assignment. It is not a mandatory runtime cost for every use of the skill. The report and source register remain development rationale outside the portable package.

## D-010: Evaluate behavior and preserve evidence limits

Structural validation establishes packaging properties. A self-reviewed worked example checks consistency but does not establish effectiveness. Behavioral evaluation must exercise scope retention, ownership, missing prerequisites, unsupported claims, and handoff usability on realistic tasks. Comparative trials remain tracked in the roadmap.

## D-011: Continue into implementation when requested

Version 0.2.0 preserves D-001's standalone design default and adds a conditional [implementation reference](../skills/full-stack/references/implementation.md). A build request activates it using the same requirements, contracts, and work registry. It requires completion evidence for the selected outcome, not merely a first working slice. Existing subject-project execution rules retain authority.

A separate companion skill would add discovery and handoff cost without a distinct runtime or execution mechanism. A mandatory build mode would violate design-only requests. The conditional reference is the smallest extension supporting both intents; the host still supplies editing, execution, and runtime capabilities.

## D-012: Compress repetition, preserve decision criteria

Keep scope, authority, evidence limits, readiness, and mode selection in the entrypoint. Load detailed terminology, decomposition, artifact patterns, research, integration, and implementation only when needed. Retain distinctions that change a decision; remove duplicated explanation rather than replace precise terms with shorthand. Count entrypoint and selected-reference costs separately so moving text cannot masquerade as total savings.

The [proposal review](research/improvement-review.md) records accepted, modified, and rejected suggestions with sources. Compression is an instruction-cost measurement; behavior needs separate evaluation. Neither reduced tokens nor passing samples establishes superiority.

## Inspected predecessor baseline (0.1.0)

Inspection date: 2026-09-09. Recurspec HEAD: `8374c2bd1d373766ca7e66293dee44698d541612`. Architectural Reasoning frontmatter version: `1.3.0`; its repository had no resolvable HEAD during inspection. These identify inspected baselines, not a claim that either working tree was clean.

Relevant files: Recurspec `README.md`, `CONTEXT.md`, bundled `SKILL.md`, `references/design.md`, and `references/resolve.md`; Architectural Reasoning `SKILL.md`, `references/subsystem-specification.md`, and `references/architectural-philosophies.md`. Instructions are adapted selectively; the portable package retains [upstream notices](../skills/full-stack/NOTICE.md).
