# Design decisions

These decisions record the initial 0.1.0 design, the 0.2.0 extension in D-011/D-012, the logic entrypoint in D-013/D-014, package 0.3.0 in D-015/D-016, the modular layer redesign (package 0.4.0) in D-017, cost optimization in D-018, plugin packaging in D-019, and the assurance dimension (package 0.5.0) in D-020. They are project conventions motivated by the [research](research/foundations.md), not claims of experimentally demonstrated superiority.

## D-001: Create a standalone design skill

Full Stack owns bounded requirements elaboration, architectural synthesis, and delivery planning. Recurspec owns its contract/execution workflow. Architectural Reasoning supplies useful boundary and ownership discipline. Keeping the new skill independently usable avoids requiring a CLI, candidate branch, or merge process merely to prepare a design.

Alternative: rewrite Recurspec as the sole entry point. Rejected for this initial version because the new request concerns design semantics and scope control, while Recurspec also serves a distinct execution purpose. Revisit if usage shows that maintaining separate entry points causes more confusion than it removes.

## D-002: Prefer established vocabulary with explicit local definitions

Use requirements, scenarios, components, interfaces, authority, refinement, and traceability. Define overloaded terms and distinguish product, architecture, runtime, resource, and work views. Preserve a subject project's language through mappings rather than forced renaming.

Alternative: reuse all Recurspec domain terms as the sole vocabulary. Its [CONTEXT.md](https://github.com/takku1/recurspec/blob/8374c2bd1d373766ca7e66293dee44698d541612/CONTEXT.md) reserves Contract Node and Atomic Leaf for specific workflow concepts; extending those names to every UI concept or work package would blur their meaning. Full Stack keeps them only when integrating with that workflow.

## D-003: Treat decomposition as an iterative design decision

Recurspec's [design reference](https://github.com/takku1/recurspec/blob/8374c2bd1d373766ca7e66293dee44698d541612/src/recurspec/skill/references/design.md) already covers raw goals, technology research, vertical/horizontal coverage, and decomposition guards. This is an important existing capability, not an absent feature being invented here.

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

Architectural Reasoning's [subsystem template](https://github.com/takku1/architectural-reasoning/blob/1e96a46360515db8774ba872d1d891e8209860ab/references/subsystem-specification.md) covers state authority, interfaces, resource/concurrency semantics, failure, observability, performance, and migration. Full Stack adapts this depth where the selected scope needs it.

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

Version 0.2.0 preserves D-001's standalone design default and adds a conditional [implementation reference](../skill/full-stack/references/implementation.md). A build request activates it using the same requirements, contracts, and work registry. It requires completion evidence for the selected outcome, not merely a first working slice. Existing subject-project execution rules retain authority.

A separate companion skill would add discovery and handoff cost without a distinct runtime or execution mechanism. A mandatory build mode would violate design-only requests. The conditional reference is the smallest extension supporting both intents; the host still supplies editing, execution, and runtime capabilities.

## D-012: Compress repetition, preserve decision criteria

Keep scope, authority, evidence limits, readiness, and mode selection in the entrypoint. Load detailed terminology, decomposition, artifact patterns, research, integration, and implementation only when needed. Retain distinctions that change a decision; remove duplicated explanation rather than replace precise terms with shorthand. Count entrypoint and selected-reference costs separately so moving text cannot masquerade as total savings.

The [proposal review](research/improvement-review.md) records accepted, modified, and rejected suggestions with sources. Compression is an instruction-cost measurement; behavior needs separate evaluation. Neither reduced tokens nor passing samples establishes superiority.

## D-013: Adopt a logic-first entrypoint

The prose entrypoint becomes a SkillWren contract-header plus logic-body file. Routing reads the ~400-token header instead of the full entrypoint; branches, gates, authority, and effects are mechanically checked; the six method references stay as the shared meaning corpus and load on demand. The `version` field now declares the SkillWren format version rather than the project revision.

Alternative: keep the prose entrypoint and the logic draft side by side. Rejected because two competing entrypoints split maintenance and router behavior; the [pilot report](../evals/trials/logic-conversion/pilot-report.md) records the conversion evidence and dogfood findings. Behavior still needs independent evaluation under FS-001; validator-clean is structure, not proof of effect.

## D-014: Live-fire flow refinements

First live use of the logic entrypoint (MochiOS performance fix, [field report](research/field-report-2026-10-03-mochios.md)) produced five refinements, all validator-clean with no header change. Derive acceptance criteria from the request and prior conversation before asking, and state derived criteria in the completion report for after-the-fact correction. Resolve the work registry to the subject's existing tracker nearest the changed component, skip registry steps when none exists, and never create a registry file without authorization. Routine edits record a registry entry in both flows when a tracker exists, keeping `design` and `implement` consistent. Confirm target files have no concurrent uncommitted edits, for repos with several agents active. Reword the entrypoint claim from "control is formal" to "control is structured": `apply` steps carry description, not checked effects.

Alternative: leave the flows as piloted and carry the friction as runner judgment. Rejected because each point forced a mid-run decision the skill should have made; the fixes are branch conditions and invariants, not new features. One observation (the `apply` verb carrying description rather than control) belongs to SkillWren rather than this skill and is recorded as a format-level finding, not applied here.

## D-015: Fresh-user review and second field report (package 0.3.0)

The [fresh-user review](research/review-2026-10-05-fresh-user.md) (verdict NOT-YET) and the [second field report](research/field-report-2026-10-03-mochios-2.md) found that the logic entrypoint left authorization, filing, ordering, and notation underspecified. The SkillWren format stays (D-013); the flows and appendix change:

- **Declined commitments.** Each answer to the costly-commitment question has a defined result: authorized work is ready; declined work is marked conditional and filed; dismissal writes nothing. Every design lists work as ready, conditional, or blocked, and `implement` builds only ready work (`never: build conditional or blocked work`). This supersedes the [0.2.0 review](research/improvement-review.md)'s rejection of an approval gate: the gate covers only costly-to-reverse commitments, and the review's concern (no branded decision classes, no approval for ordinary choices) still holds.
- **Plain-language step meanings.** The appendix defines every `apply` step, the control words, and which header fields hosts actually read. `version` remains the SkillWren format; the package release is stated in the README.
- **Filing.** Subject instructions take precedence over package defaults. A design extends the existing component note, else the documented location, else one `docs/design/<outcome-slug>.md`; it stays in chat when asked, when no repository is known, or when the subject forbids new design files. The standalone reference no longer suggests creating a roadmap.
- **Ordering.** Registry identity resolves during grounding (Recurspec `ROADMAP.md` first). Routine edits ground and read entries before updating, and registry updates are idempotent. Scope splits happen before the design is generated. Implementation writes edits before running checks, repairs, then records evidence.
- **Accepted designs.** `implement` accepts a `design` input and rechecks its facts instead of rerunning design and re-asking settled questions.
- **Readiness.** The gate checks the same five sections the appendix describes, matched to the selected scope; routine notes are a separate shape. A repeated identical failure becomes a recorded blocker instead of a loop.
- **Concurrency.** Uncommitted edits made outside the run and processes holding build/run resources are left alone, with a stated recovery: edit around, ask, or wait.
- **Recurspec evidence.** Owning-node evidence updates are proposed in the completion report, not applied.
- **Discovery.** The description excludes isolated routine edits and names cross-component changes.

- **Host-parseable header.** An unquoted `Enum[...]` in an inline map is valid in the SkillWren profile but not YAML; Claude Code then showed the H1 as the description. The value is quoted, and the artifact checker parses the header with PyYAML. Reported upstream as SkillWren BF-1.

The entrypoint grows from about 2,560 to about 3,500 approximate tokens, mostly for the step glossary. Alternative: convert back to numbered prose. Rejected for now because D-013's structure checks still catch binding, effect, and ask-before-write errors; revisit if the FS-009 comparison shows the notation costs more than it prevents.

Installers now preview, back up changed installs outside the skills folders, stage before replacing, and roll back on failure; `install.sh` covers macOS/Linux (exercised under Git Bash only). The artifact checker reports sibling-checkout links as optional workspace links rather than package errors.

## D-016: Mechanical run guard, parallel write sets, and an A/B harness

A follow-up critique of 0.3.0 raised four gaps: no enforcement story, effectiveness claims resting on non-comparative trials, a larger entrypoint with no measured payoff, and concurrency guidance too thin for parallel workers.

- **Enforcement.** `scripts/run_guard.py` makes the implement flow's scope and evidence claims checkable in git repositories. A worker claims a write set (refused if it overlaps uncommitted edits made outside the run, or another open run, including runs in other worktrees). Checks run through the guard so their exit codes are recorded. `check` flags changes outside the write set or to edits that predate the run. The completion report pastes the guard's report. The README states which guarantees are mechanical and which remain instructions. Alternative: rely on host hooks. Rejected as the default because hooks are per-user host configuration that a portable skill cannot install; a hook can still call the guard.
- **Parallel work.** Work packages carry a write set; parallel packages must be disjoint, and shared files (manifests, lockfiles, registries, generated code) have one owning package that integrates last and reruns the full checks.
- **Cost.** The appendix dropped text that repeats references the flows already load. The entrypoint is about 3,400 approximate tokens including the new enforcement section, down from about 3,500. A separate "lite" profile was rejected: each session starts fresh, so there is no "practiced runner" for whom the step glossary is redundant.
- **Evidence.** `evals/ab/run_ab.py` runs FS-009's five paired cases in isolated profiles with hidden acceptance checks and a blind grading packet. It closes no evidence gap until it has been run and graded.

## D-017: Modular layer orchestration (package 0.4.0)

Status: accepted for implementation on 2026-11-12 at the owner's request; effectiveness unmeasured. Design: [modular-layers.md](design/modular-layers.md). Research: [modular-redesign.md](research/modular-redesign.md).

The owner asked for Full Stack to break into layer-specific parts (data, runtime and scripting, interface, client, platform, cross-cutting), each able to find the best option for its layer, coordinated by an orchestrator.

- **Tiered loading.** A brief-sized core is always loaded; design and implement flows and layer modules load only when needed. This reverses D-016's rejection of a lighter profile. The reason is FS-009's evidence, not a new preference. In that run a 312-token brief beat the full skill, and external studies find instruction volume adds cost without reliable gains ([30]–[34]).
- **Central orchestration of coupled choices.** Layers are coupled, which is the case where multi-agent systems fail ([29], [36]). One orchestrator owns the stack brief and cross-layer contracts. Layer modules propose candidate sets with neighbor assumptions; the orchestrator intersects them and commits a joint profile, as in set-based concurrent engineering ([40]). Subagents may gather evidence for independent layers but do not decide.
- **Methods, not catalogs.** Modules hold questions, criteria, and evidence requirements, and each decision is an ADR with CBAM-style scoring, a minimax-regret column, and an innovation budget ([41], [45], [46], [50]). This keeps the framing's non-goals of no universal catalog and no fixed stack.
- **Mechanical compatibility.** `check_stack.py` checks decision records against a small rules file and against each other's neighbor assumptions, as feature-model constraints do ([44]).
- **Existing stacks stay.** In a repository each layer starts as "keep current" and reopens only when the outcome requires it (D-005).
- **Entrypoint format.** The SkillWren header (`contract`, `authority`, `effects`, `budget`) left `SKILL.md`. Hosts read only `name` and `description`, and the header cost about 400 tokens on every run. Its invariants now live in the core's rules, and its resources live in the flow that uses them. The `logic` blocks for design and implement moved unchanged in substance into `flows/`, with step meanings beside them. D-013's structure checks therefore still apply to the flows. Measured core: about 580 tokens (characters / 4), down from about 3,400.
- **Rejected:** independent per-layer agents (coupling, MAST); negotiation, bidding, or debate between layers ([37]–[39], [51]); a ranked tool catalog (goes stale, and conflicts with the framing).

Revisit if FS-016 shows the modular package does not beat the brief on greenfield selection, or if FS-017 attribution shows layer modules add no value.

## D-018: Optimize turns and output before instruction length

Status: applied 2026-11-12; non-inferiority unevaluated (FS-019). Research: [optimization.md](research/optimization.md).

FS-009's extra cost tracked extra turns (bugfix 14 vs 8, crosscut 24 vs 18) more than instruction size, and cached instruction prefixes cost 0.05–0.1× on later turns ([55]). Changes:

- **Guard batch commands.** `run_guard.py checks` runs every acceptance check in one call (`--each "criterion :: command"` or `--plan`). `close` combines check, report, and finish, and refuses to finish an unclean run without `--accept-blockers`. A guarded run drops from 4 + N calls to 3. `exec`, `check`, `report`, and `finish` remain for compatibility.
- **Turn budget in the core.** Read needed files in one batch, reread only after a file changed or new evidence makes it relevant, and use the batch commands. (First worded as "never reread"; an external review on 2026-11-12 pointed out that this breaks after edits or new check evidence, so it was corrected the same day.)
- **Output caps.** About 250 words per layer decision record; at most five lines for a routine edit; "none" for empty sections; reference brief IDs instead of restating them.
- **Evidence by row.** Stack research records one row per candidate (version, date, license, limit, URL), with subagents on a smaller model where the host allows it.
- **Deduplication.** The implement flow no longer repeats concurrency rules held by the core and the implementation reference, and the design flow drops guidance the core already states.

Instruction size is roughly flat: the core is about 640 tokens, up about 55 for the turn budget. That is deliberate, because the targets are turns and output. Rejected: LLMLingua-style compression of instructions, which defeats caching, is untested on agent instructions, and makes a maintained skill unreadable. Revisit any change that fails the non-inferiority margins in FS-019.

## D-019: Ship as a Claude Code plugin around the portable skill

Status: applied 2026-11-12; `claude plugin validate --strict` passes for the plugin and the marketplace; not yet loaded in a live session (FS-023).

The owner asked for whichever format is optimal. The answer is both: the portable skill folder stays the single source, and `skill/` becomes a Claude Code plugin root around it.

- **Why a plugin.** A bare skill cannot install hooks (D-016), so the guard enforced edits only after a manual settings change. The plugin ships `hooks/hooks.json`, which activates the guard automatically. A plugin can also define a subagent pinned to a cheaper model: `stack-evidence` on `haiku`, which returns cited evidence rows and never decides (D-018, FS-021). Marketplace install replaces the install scripts for Claude Code.
- **Why keep the skill.** Codex and other hosts read the plain folder, and the install scripts still copy `skill/full-stack` unchanged.
- **Plugin root is `skill/`, not the repo root.** Installs copy the plugin root into a cache, and a repo-root plugin would ship `docs/`, `evals/`, and tool directories. The manifest points at the skill with `"skills": ["./full-stack/"]`. The marketplace at the repo root uses `"source": "./skill"`.
- **Hook launcher.** `scripts/guard_hook.sh` picks a working Python (`python3`, `python`, or `py -3`, skipping the Windows Store stub) and passes the event through. With no Python it exits 0, so a missing interpreter never blocks edits.
- **Left to the owner:** a license. None exists in the repository, so none was declared. The plugin directory requires one for submission; local and marketplace installs do not.

Rejected: plugin-only distribution, which would drop Codex; and duplicating the skill inside a separate plugin folder, which would create two sources to keep in sync.

## D-020: Build the assurance dimension (package 0.5.0)

Status: built 2026-11-12 at the owner's explicit request, which lifts the feature freeze for FS-026 only; unevaluated. Research: [engineering-disciplines.md](research/engineering-disciplines.md).

- **Second dimension.** `flows/assurance.md` screens every design or build beyond a routine edit with twelve yes/no risk questions. Each raised discipline goes to tier 1 or tier 2, in the spirit of risk-proportional selection such as OWASP ASVS levels ([62]).
- **Eleven modules** in `assurance/`: security, verification, reliability, observability, operations, performance, privacy, ux, maintainability, cost, compliance. Each has the same four parts, which the owner asked for: Policy, Framework (a named established method), How to, and Checks. They are about 300–490 tokens each and load only when raised.
- **Assurance table.** One falsifiable claim per row, with what could make it false, the control and its owner, the check, and an evidence status (documented, tested, inferred, unknown; this pulls FS-024's statuses forward for assurance claims). Every check becomes an acceptance criterion in `run_guard.py checks`, so a failing assurance check blocks `close` (D3 fix).
- **`crosscut` narrowed** to choosing shared technology (identity provider, secrets store, telemetry, test tooling); the obligations moved to the assurance modules.
- **Cost.** The core grew from about 640 to about 745 tokens. A typical internet CRUD design adds the flow (~810), the table template (~305), and four modules (~1,600), about 2,700 tokens. A local tool adds the flow and verification only.
- **Why checks, not prose:** working AI-written backends were exploitable about half the time on BaxBench ([60]); coverage can hide weak tests ([63]); LLM threat modeling alone is not reliable ([64]).

Rejected: one technology-selection layer per discipline, which would recreate the context cost 0.4.0 removed; loading all disciplines on every run. Revisit if FS-016's planted-failure cases show no gain over 0.4.0, or if the screen raises disciplines on cases that should stay quiet.

## D-021: Enforce the assurance screen and resolve it by rules (package 0.6.0)

Status: built 2026-11-12 at the owner's explicit request, which lifts the freeze for FS-027 and FS-028; unevaluated. Evidence: [field report 3](research/field-report-2026-11-12-mochios-3.md) (G1, G3) and [FS-015](../evals/results/fs015-2026-11-12.md): the screen was skipped or applied after the code in both live builds.

- **Resolver.** `scripts/assurance.py screen` takes an answer for every screen question (unknown counts as yes) and resolves the disciplines and tiers by forward closure over Horn rules in `rules/assurance.json`: question → discipline, discipline → required discipline (privacy → security, performance → observability), raised and `--high` → tier 2, build → verification. Each discipline lists every answer that raised it. The shape comes from the owner's HITCH prototype (capabilities as rule modules over facts, load only what the goal needs); at fourteen questions a plain fixpoint suffices. A test keeps the flow's table and the rules file identical.
- **Two capability questions** join the screen: runs untrusted code or content, and reads secrets or confidential files. They target the implicit risks FS-016 case (3) measures; that case now tests whether the model answers them correctly rather than whether it infers them unprompted.
- **`assurance.py check`** reports raised disciplines without a row, rows without a check, duplicate IDs, and untested tier 2 rows.
- **Guard enforcement.** A run declares `--assurance DESIGN.md` or `--routine` (at `start`, or later with `declare`). `close` and the Stop hook refuse while nothing is declared or while an assurance row (other than documented evidence) has no executed check whose criterion names its ID. `--accept-blockers` still finishes with the gaps reported.
- **Handoff query.** `run_guard.py report --all` lists every recorded run (state, criteria passing and failing, last check), the use field report 3 found for the log.

Rejected: refusing `start` without a declaration, which would block routine edits before any work; deriving tiers from free-text `tier2_when` lists. Revisit if FS-016 shows `--routine` used to skip the screen on non-routine work, or the extra questions raise rigor where the screen should stay quiet.

## D-022: Tighten assurance enforcement and pressure-test the rules (package 0.7.0)

Status: built 2026-11-12 at the owner's request; unevaluated. Sources: [external review 3](research/review-2026-11-12-external-3.md) (six guard findings) and practices from obra/superpowers v7.0.2 (MIT), read 2026-11-12. No Superpowers text is copied; the conventions are restated in this package's terms.

- **Guard (review 3).** Each finding was reproduced as a failing test before its fix. `close` now runs the full table check (missing Screen line, raised discipline without a row, unraised row, row without a check, duplicate ID). The PreToolUse hook blocks edits until assurance is declared; a declaration made after files changed is recorded and blocks `close`, which covers shell writes the hook cannot see. `--routine` needs a reason, and replacing a table with it needs `--override`; both are reported. Checks store the assurance IDs they name, and the latest check per ID must pass. Tier 2 rows need a passing executed check whatever their declared evidence, and the report shows declared and executed evidence side by side. `finish` applies the same gates as `close`.
- **Seen failing first.** The report marks each criterion's history (`fail → pass`, `pass only`). A check seen failing before it passed has shown it can detect its failure, the property FS-016 measures as check meaningfulness. Adapted from Superpowers' red-green regression rule.
- **Pressure tests (skill TDD).** `evals/pressure.py` runs scenarios rebuilt from observed failures (field report 3 G1, FS-015 P1, and the anticipated misuse of `--routine`) with and without the skill, and keeps the model's own words where it skips a step. A rule change is kept only if its scenario's pass rate rises. Adapted from Superpowers' writing-skills ("no skill without a failing test first"). Two scenarios include a hidden outcome check, so ceremony is not scored alone.
- **Session audit.** `evals/process_audit.py` reads a transcript and reports the order of screen, declaration, code edits, checks, and close. The pressure tests and the FS-015 trial share it, and field reports can use it instead of hand counting. Adapted from Superpowers' diagnosing-superpowers.
- **Description as a trigger.** `SKILL.md`'s description now starts "Use when…" and names conditions, not the workflow, because a summary invites following the description instead of reading the skill (Superpowers' writing-skills). The artifact checker enforces the prefix. Discovery under the new description is unverified (FS-005).
- **Red flags.** `flows/assurance.md` lists three thoughts that lead to skipping the screen, each tied to its source. The stack-flow skip (FS-015 P1) got no rule because it was seen once; it is a pressure scenario instead.
- **Consumes and produces.** Work packages name the interfaces they consume and produce, so ordering between packages is explicit (from Superpowers' writing-plans task shape).
- **Independent review.** A design that raises a tier 2 discipline or holds a costly-to-reverse commitment gets one fresh-reviewer pass, reported apart from self-review (from Superpowers' brainstorming builder check).

**0.7.1 addendum (same day, from the [FS-029 smoke run](../evals/results/pressure-2026-11-12.md), $0.65).** Under "keep it quick", the skill arm skipped every process step, exactly like the control. Two defects explained it: the core called any one- or two-file fix routine (now: one that adds no state, trust boundary, permission, or contract), and the hooks enforced nothing until a run was open. Fixing the text alone changed nothing in one session. A session opt-in did: a `UserPromptSubmit` hook (or a model-invoked Skill call) marks a session that invokes Full Stack, and the PreToolUse hook then blocks code edits until a guarded run is open, leaving design notes free. In the next session the blocked edit led the model to screen, write the table, declare it, check A-1 to A-4, and close. Sessions that never invoke the skill are unaffected. One session per cell: an existence result, not a rate.

Rejected from Superpowers: the always-on bootstrap that requires a skill check at "even a 1% chance" (FS-009 found extra instructions and turns cost more without better results); per-task reviewer subagents and a model per role (team-ops and the `stack-evidence` agent already cover them). Revisit the red flags and the description if pressure tests or FS-016 show no gain.

## D-023: Adopt SkillWren's fragment workflow and run ledger (package 0.8.0)

Status: built 2026-11-12 at the owner's request ("update this system to match SkillWren's workflow"); unevaluated in live sessions. Source: SkillWren 0.6.0 to 0.7.0 at `Z:\skillwren` (SPEC Sections 6 and 20, `docs/current/fragment-template.md`, `design/fragments-and-ordering.md`, `src/skillwren/ledger.py`), which named two upstream findings for this package: an `order:` rule for the assurance screen (field report 3, G1) and a U1 on `integration` in `flows/design.md`.

- **Flows are SkillWren fragments.** Each of `design`, `implement`, `assurance`, and `stack` has a `contract` block with declared `inputs:` (strict definite binding) and `order:` rules, and a `logic` block. `assurance` and `stack` gained logic blocks (they were prose only, W14) and are called with cross-file `run`, so their order guarantees carry into `design`. All four pass `skillwren check --fragment` with no warnings.
- **Order rules rest on evidence.** Every rule's earlier step is an `exec` of one of this package's scripts (`assurance.py screen` and `check`, `check_stack.py profiles` and `check`, `run_guard.py start`, `checks`, `close`) whose result a `verify ... from` gate reads, so no rule is a self-report (W15). Rules: screen before the design is generated; complete table before code; guard started before code; code before acceptance checks; checks before close; profiles before decision records; stack check before the records are returned.
- **Defects the checker found.** U1: `integration` was unbound when the subject had contracts but was not otherwise known (fixed by reading the guide where it is used). M1, dismissal safety, in `design` and `stack`: the costly-commitment question came after files were written and scripts run, contradicting the stack flow's own "dismissed means nothing written". The stack flow now asks once candidates are named, before anything is written or run; the design flow asks about commitments known from the scope before any mutation, and a commitment found later is shown and marked conditional instead of asked mid-flow.
- **Mutants.** `evals/test_flows_skillwren.py` keeps every flow clean and proves the rules bite: five one-break mutants (assurance gate removed, code before the guard starts, screen made conditional as in G1, stack check dropped, table returned unchecked) fail with P1, and moving the authorization after a write fails with M1. `evals/check_artifacts.py` runs the fragment check too, and skips with a notice when SkillWren is absent.
- **Runtime form of the order rules.** The guard blocks code edits until the declared table passes `assurance.py check` (not merely until it is declared); a check run before any code edit is recorded as a reproduction, so reproduce-first never counts as an order violation; a write the hook did not see is recorded when the next check finds it, with file digests. With SkillWren installed, the guard writes a SkillWren 0.7 run ledger committed to `implement.md`'s order rules and required milestones, records checks and the table check as `exec` evidence, notes the close only when the run will finish, and `close` refuses a ledger with violations or missing milestones. Without SkillWren the gates still hold; only the ledger is skipped.

- **Cost.** The always-loaded core is unchanged (about 720 tokens). The on-demand routes grew: implementation from about 2,510 to 3,150 tokens and stack from about 4,290 to 5,030 (`evals/measure_context.py`), the price of logic blocks in `assurance` and `stack`. FS-019's non-inferiority test applies.

Not adopted: SkillWren's `guard` controller and `sandbox` (they need a trusted host and a container runtime; this package's hooks run as the user) and a SkillWren header on `SKILL.md` (still rejected per D-017; the fragment layout makes it unnecessary). Revisit the ledger gate if it blocks legitimate runs in FS-029 or FS-016.

## Inspected predecessor baseline (0.1.0)

Inspection date: 2026-09-09. Recurspec HEAD: `8374c2bd1d373766ca7e66293dee44698d541612`. Architectural Reasoning frontmatter version: `1.3.0`; its local checkout had no resolvable HEAD during inspection, and the public repository's only 1.3.0 state before that date is `1e96a46360515db8774ba872d1d891e8209860ab`, which the links above pin. These identify inspected baselines, not a claim that either working tree was clean.

Relevant files: Recurspec `README.md`, `CONTEXT.md`, bundled `SKILL.md`, `references/design.md`, and `references/resolve.md`; Architectural Reasoning `SKILL.md`, `references/subsystem-specification.md`, and `references/architectural-philosophies.md`. Instructions are adapted selectively; the portable package retains [upstream notices](../skill/full-stack/NOTICE.md).
