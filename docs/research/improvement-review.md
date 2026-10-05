# Review of the improvement proposals

Reviewed 2026-09-09 for version 0.2.0. The supplied `potential fixes- to be deleted.md` mixed critique, unsourced comparisons, usage prompts, and a repository improvement brief. This record replaces that scratch file. Its observations about another user's generated JSX and a Downloads checkout were not independently established here.

The concrete gap was documented: 0.1.0 ended with ordered implementation work. It did not provide an implementation procedure. This is evidence about instructions, not an observed application-generation failure. The revision preserves the design default and adds a conditional execution reference under D-011.

## Disposition of the proposals

| Proposal | Decision and implementation |
|---|---|
| Specify doubles alongside real contracts | Adopt: work packages and implementation guidance name simulated guarantees, limits, provider, replacement condition, and remaining integration work. |
| Make cross-cutting checks actionable | Adapt: scenario triggers in the entrypoint, with material exclusions explained. Reject evaluating performance only when benchmarks exist; requirements can precede measurements. |
| Classify irreversible/reversible decisions | Adapt: record costly reversal, migration options, and affected work without imposing branded decision classes or an approval gate. *Superseded in part by [D-015](../design-decisions.md#d-015-fresh-user-review-and-second-field-report-package-030): costly-to-reverse commitments now ask the user.* A database or format choice is not inherently irreversible. Consequential assumptions remain visible even when reversible. |
| Claim production readiness or superiority over official skills | Reject: no supporting outcome comparison was supplied. Official skill guidance describes packaging and loading, not a universal architecture ranking. The unnamed `skill-design-sync` comparison lacks a resolvable source. |
| Use progressive disclosure and concise wording | Adopt: shared rules stay in the entrypoint; detailed method and build workflow load conditionally. Report total reference cost as well as entrypoint cost. |
| Add deterministic execution commands | Adapt: use the subject project's actual tools and checks; no universal package manager, runtime, or install procedure. |
| Produce complete software when asked | Adopt: the same scoped requirements and registry drive design, implementation, integration, and evidence. A first slice does not close the milestone. |
| Fix modularity by generating more files | Reject as a criterion: preserve information hiding, state ownership, and consumers; packages/services require justification. The NPC example remains illustrative, not a mandatory framework. |
| Add usage examples and clarify host capabilities | Adopt in README, project framing, and implementation reference; retain portable notices and existing-project authority. |
| Test a CLI, existing feature, stateful user-facing app, restart, later change, trivial edit | Run isolated forward trials with exact inputs and retained outputs. Separate author assessment, executable checks, and independent generation; see the revision evidence. |
| Compare equivalent budgets and test a real project | Retain as future evaluation in ROADMAP.md; local samples cannot establish comparative or universal reliability. |

## Sources and applicability

All sources below were opened on 2026-09-09. These support specific decisions, not validation of Full Stack.

- **Agent Skills, Specification**, undated live specification, sections “Body content,” “Progressive disclosure,” and “File references”: recommends a compact entrypoint and conditional references. It does not require a purely procedural body or prove a performance benefit for this skill. [Specification](https://agentskills.io/specification)
- **Anthropic, Equipping agents for the real world with Agent Skills**, 2025-10-16, “The anatomy of a skill”: describes staged loading of metadata, instructions, and resources. Vendor engineering guidance, not a comparative architecture study. [Article](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- **David L. Parnas, On the Criteria To Be Used in Decomposing Systems into Modules**, 1972, “Changeability” and “The Criteria”: examines information hiding and change effects through a worked comparison. This motivates the later-change diagnostic; it establishes no file-count rule or LLM outcome. [Original paper transcription](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html)
- **Felix Bachmann, Len Bass, Mark Klein, Deriving Architectural Tactics**, CMU/SEI-2003-TR-004, 2003, section 2.1 and Appendix A: expresses quality requirements through concrete scenarios and response measures. Our trigger wording is an adaptation, not the report's checklist or a conformance claim. [Technical report](https://www.sei.cmu.edu/documents/704/2003_005_001_14213.pdf)
- **Martin Fowler, Mocks Aren't Stubs**, 2007-01-02, “The Difference Between Mocks and Stubs” and “Classical and Mockist Testing”: distinguishes test doubles and verification styles. Requiring real integration evidence is our project convention, not a claim that the article validates this workflow. [Author article](https://martinfowler.com/articles/mocksArentStubs.html)
- **Jeff Bezos, 2015 Letter to Shareholders**, section “Invention Machine,” decision-type discussion: practitioner rationale for proportional treatment of reversible decisions. We use reversal cost directly rather than a mandatory Type 1/Type 2 taxonomy. The initially attempted About Amazon article URL failed; the official investor-relations PDF was accessible. [Letter](https://ir.aboutamazon.com/files/doc_financials/annual/2015-Letter-to-Shareholders.PDF)

The existing [source register](sources.md) remains the provenance for the broader foundations. This revision rechecked sources material to these proposals, not every historical citation. No new academic effectiveness claim is made.

## Acceptance and evidence

The revision must preserve semantic distinctions and design-only scope, reduce entrypoint cost, make authorized implementation actionable, retain self-contained packaging/notices, update usage consistently, and exercise the requested samples. [Revision evidence](../../evals/results/revision-review.md) records measurements, checks, outcomes, and limits. Incomplete evaluation work belongs only in [ROADMAP.md](../../ROADMAP.md).
