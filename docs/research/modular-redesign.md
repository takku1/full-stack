# Research for a modular, layer-orchestrated Full Stack

Research date: 2026-11-12. This report supports the proposed redesign in [docs/design/modular-layers.md](../design/modular-layers.md) and decision [D-017](../design-decisions.md#d-017-modular-layer-orchestration-package-040). It extends [foundations.md](foundations.md), which covers requirements semantics, architecture description, decomposition, composition, and traceability, but not technology selection, multi-agent coordination, or decision economics. Numbers in brackets refer to the [source register](sources.md#sources-for-the-modular-redesign-2026-11-12). Where only an abstract or landing page was read, the register says so; no claim here relies on full text that was not accessed.

Evidence labels used below: **measured** (a published experiment reports it), **internal** (this repository's own runs, self-administered), **precedent** (an established method from another field or era, not tested on LLM agents), and **proposal** (this project's inference).

## Question

The request is to break Full Stack into layer-specific parts (data, language and runtime, interface, client, platform), each able to find the best option for its layer, with an orchestrator holding them together. Three questions follow:

1. How much instruction should a run load, and how should it be split? (Sections 1–2.)
2. How should specialists for coupled decisions coordinate? (Sections 3–4.)
3. How should each specialist choose, and does game theory add anything? (Sections 5–7.)

## 1. More instruction is not reliably better

**Measured.** Repository context files rarely improve task success. Gloaguen and colleagues report that context files "do not generally improve task success rates" while raising inference cost by over 20%, across agents, models, and both generated and developer-written files; instructions in them were followed, but repository overviews did not help [30]. A two-agent ablation on 17 real tasks (288 runs) bounds the correctness effect of context strategy to at most 10–15 percentage points and attributes failures to "implementation skill—feature design, pattern selection, exact wiring", not missing repository knowledge [32]. A factorial study of 1,650 Claude Code sessions found no detectable effect of file size, instruction position, architecture, or conflicts on compliance; compliance fell with the number of functions generated in a session [33]. One study does find an efficiency benefit: with an AGENTS.md file, median runtime fell 28.64% and output tokens 16.58% over 10 repositories and 124 pull requests, with comparable completion [31]. IFScale finds the best frontier models reach 68% accuracy when given 500 simultaneous instructions [34].

**Internal.** This project's first context-dose run ([FS-009](../../evals/results/context-dose-2026-10-05.md)) found a 312-token brief scored higher than both plain Claude Code and the full ~3,400-token skill on six small and medium cases, at roughly a tenth of the skill's added cost. One session per cell and model grading limit it.

**Reading.** Instruction volume buys little on its own; what helps is guidance on procedure, pattern choice, and verification, delivered when relevant. That argues against loading every layer's guidance on every run, and for a small always-loaded core.

## 2. Progressive disclosure is the platform's intended modularity

**Precedent (vendor guidance, unmeasured).** Agent Skills load only `name` and `description` at startup, the body on trigger, and bundled files only when read [28]. Anthropic's authoring guidance recommends a `SKILL.md` body under 500 lines, references one level deep, tables of contents for long references, scripts for fragile deterministic operations ("solve, don't defer"), and at least three evaluations across model sizes [27]. A 2026 survey frames skills by a nine-stage lifecycle (discovery, representation, storage, retrieval and routing, composition, execution and repair, adaptation, evaluation, security governance) and reports no experiments [35].

**Reading.** Layer modules map naturally onto on-demand reference files. Mechanical checks (compatibility, write sets) belong in scripts, not prose. None of this is measured; it is the host's design.

## 3. Multi-agent orchestration helps parallel work, not coupled work

**Measured (vendor, internal eval).** Anthropic's research system, a Claude Opus 4 lead with Claude Sonnet 4 subagents, outperformed single-agent Opus 4 by 90.2% on Anthropic's internal research evaluation. Token usage alone explained 80% of performance variance, with tool-call count and model choice the other two factors. Multi-agent runs used about 15× the tokens of a chat. The authors state that domains requiring shared context or "many dependencies between agents are not a good fit for multi-agent systems today" [29].

**Measured.** MAST classifies 14 multi-agent failure modes into system design issues, inter-agent misalignment, and task verification, from 150 traces (κ = 0.88) and a dataset of 1,600+ traces over 7 frameworks [36]. The current abstract claims "improvement headrooms from better MAS design" without a figure; an earlier version's intervention number is not relied on here.

**Measured.** Multi-agent debate rarely beats simpler sampling at equal budget. Zhang and colleagues tested 5 debate methods on 9 benchmarks with 4 models and found they "often fail to outperform" chain-of-thought and self-consistency, while arguing that model heterogeneity helps [37]. Yang and colleagues find limited advantage over single-agent scaling on math, more benefit on harder problems and weaker models, little benefit from agent diversity, and increased vulnerability on safety tasks [38]. The two disagree on diversity.

**Reading.** Stack layers are tightly coupled: the data model constrains the runtime, the interface style shapes the client, the platform limits everything. That is the dependency-heavy case Anthropic flags and the misalignment class MAST names. Independent per-layer agents choosing their own optimum is the wrong default. Parallelism fits the *research* inside a decision (surveying database candidates and client frameworks are independent), not the decision itself. Adding debating or negotiating agents is not supported by the evidence.

## 4. Coordinating coupled specialists: prior art outside LLMs

**Precedent: set-based concurrent engineering.** Sobek, Ward, and Liker describe Toyota engineering teams that map the design space in parallel by functional expertise, keep *sets* of feasible designs, integrate subsystems "by finding the intersection of mutually acceptable sets", and narrow gradually [40]. (Only the article's opening was accessible; the third principle is not reported here.) This matches the layer problem closely: each layer proposes a set and the constraints it imposes; integration intersects; commitment comes late.

**Precedent: blackboard architecture.** HEARSAY-II coordinated independent knowledge sources through a shared structured state under a scheduling controller [47]. An orchestrator with a shared stack brief and per-layer records is the same pattern.

**Precedent: contract net.** Smith's Contract Net Protocol allocates tasks by announcement and bidding among agents with private capabilities [51]. Layer modules have no private information or competing interests, so bidding adds messages without solving a real problem. It is cited as a pattern *not* to adopt.

**Measured.** In LLM-Coordination's pure coordination games, agents did well when decisions depended mainly on the environment, and poorly when they had to reason about partners' beliefs and intentions [39]. Implicit coordination between layer agents is therefore unreliable; contracts between layers should be written down.

**Proposal.** One orchestrator owns the stack brief and the cross-layer contracts; layer modules propose candidate sets with their neighbor assumptions; the orchestrator intersects and commits; a script checks that every recorded assumption is met.

## 5. Choosing within a layer

**Precedent: CBAM.** The SEI's Cost Benefit Analysis Method starts from quality-attribute scenarios (ATAM's output) and ranks architectural strategies by benefit relative to cost, explicitly as decision support rather than decision-making [41].

**Precedent: architecture decision records.** Nygard's ADRs record Title, Context, Decision, Status (proposed, accepted, deprecated, superseded), and Consequences [45]. Agents and maintainers already recognize the form.

**Precedent: boring technology.** McKinley proposes that "every company gets about three innovation tokens" and should spend them deliberately; familiar technology has known failure modes [46].

**Precedent: feature models.** FODA introduced feature models for a domain's commonality and variability [44]; product-line work since expresses compatibility as requires/excludes constraints that a solver can check. Technology compatibility (a framework requires a runtime; an ORM excludes a store) has the same shape.

**Precedent: modularity as option value.** Baldwin and Clark value modular designs as bundles of options [43]; Sullivan, Griswold, Cai, and Hallen apply design structure matrices and real options to software and reproduce Parnas's conclusions on KWIC [42]. A DSM indicates where to draw module boundaries (low cross-dependency), and option value explains why costly-to-reverse commitments deserve delay and evidence.

**Reading.** A layer module should not hold a ranking of "best" tools. It should hold the questions, criteria, and evidence requirements that let a run choose against *this* project's brief, record the choice as an ADR, and spend novelty deliberately. This keeps the [project framing](../project-framing.md)'s non-goal of no universal technology catalog and no fixed stack.

## 6. Game theory: where it helps and where it does not

**Useful.**

- **Coordination games explain why choice must be joint.** A stack is a coordination game with several equilibria: different database and runtime pairings can each be internally coherent. Layers that each best-respond independently can land on a mismatch or a poor equilibrium. A single chooser selecting the joint profile avoids that; the measured coordination weakness [39] reinforces it. (Proposal, grounded in standard theory.)
- **Minimax regret for uncertain futures.** Savage's minimax-regret criterion [50] picks the option whose worst-case shortfall, against the best option in each scenario, is smallest. For technology choice, scenarios are plausible futures (tenfold load, team turnover, offline requirement). It is cheap, legible, and fits decisions under unknown requirements better than a single weighted score. (Precedent, decision theory rather than strategic game theory.)
- **Shapley values for evaluating modules.** Shapley's value [49] assigns each player its average marginal contribution across coalitions. Treating modules as players answers which layer modules earn their tokens, extending FS-009. Exact computation over six modules is 64 configurations per case, so sampling is required; llmSHAP analyzes when Shapley principles hold under stochastic inference [48]. (Proposal for evaluation.)
- **Principal–agent framing of self-reports.** A model that reports its own success has an incentive-like bias toward claiming completion; the remedy is executed evidence. `run_guard.py` already does this; the framing explains why it should stay mechanical. (Proposal.)

**Not useful.**

- **Mechanism design, auctions, and negotiation between layer agents.** These solve problems of self-interest and private information. Layer modules share one model, one principal, and full information. Negotiation benchmarks (TERMS-Bench, PACT) and cooperation benchmarks (CoopEval) measure behaviors this design does not need; they are listed as leads only.
- **Debate as a quality mechanism.** See section 3: equal-budget evidence does not favor it, and the diversity claim is contested [37], [38].

## 7. Implications for the redesign

| Finding | Design response | Label |
|---|---|---|
| Volume of instruction does not buy success [30]–[34]; brief beat full skill (FS-009) | Small always-loaded core; layer modules loaded only for affected layers | Measured + internal |
| Skills disclose progressively; scripts for deterministic checks [27], [28] | Modules as reference files; compatibility check as a script | Precedent |
| Multi-agent fits parallel, not coupled, work [29]; failures are spec and misalignment [36] | Central orchestrator owns brief and contracts; subagents only for independent research | Measured |
| Coordinate coupled subsystems by intersecting sets [40] | Two passes: candidate sets with neighbor assumptions, then joint commitment | Precedent |
| Choose by quality scenarios and cost [41]; record as ADRs [45] | Per-layer decision record with criteria, evidence, consequences, revisit conditions | Precedent |
| Novelty has a cost [46]; modularity has option value [42], [43] | Mature default; innovation budget; defer costly commitments (already D-015) | Precedent |
| Compatibility is a constraint problem [44] | Rules file of requires/excludes/assumes plus checker | Precedent + proposal |
| Joint choice in a coordination game; minimax regret under uncertainty [50] | Orchestrator commits the profile; regret column in decision record | Proposal |
| Module value is measurable by attribution [48], [49] | Sampled Shapley ablations in evaluation | Proposal |

## Boundaries

This is a targeted search with citation following, not a systematic review. Several LLM sources are 2026 preprints read at abstract level; their designs (one or two repositories, 17 tasks, a single vendor's internal eval) limit generalization. The engineering precedents come from manufacturing, defense software, and 1980s AI; none was tested with LLM agents. No source evaluates per-layer technology selection by an LLM; that question is open and is what [FS-016](../../ROADMAP.md) tests.

The redesign is a proposal. Nothing here shows that a modular Full Stack outperforms the 0.3.0 package, the 312-token brief, or plain prompting.

## Open questions

1. Does a brief-sized core plus on-demand layer modules match the brief's FS-009 result on small tasks while helping on greenfield stack selection?
2. Does two-pass set narrowing produce more coherent stacks than a single pass by the same model at equal tokens?
3. Does a mechanical compatibility check catch real inconsistencies, and at what false-positive rate?
4. Which layer modules have positive marginal value under sampled Shapley attribution?
5. Does research fan-out to subagents improve candidate evidence enough to justify its token multiple [29]?
