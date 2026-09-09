# Foundations for Full Stack

## Framing and central conclusion

A planning skill must convert incomplete intent into a design whose parts retain their meaning as they are refined, allocated, implemented, and checked. The central activity is **requirements elaboration and architectural synthesis with traceability**. This framing names established activities without pretending their combination is an established method with demonstrated effectiveness.

The proposed skill should maintain a small domain vocabulary, a bounded set of outcomes, explicit responsibility allocation, selected architectural views, and links to evidence and implementation work. Recursive decomposition is one tool within this method. It cannot alone establish that the pieces are necessary, compatible, sufficient for an outcome, or appropriate implementation units.

This report combines foundational requirements and architecture research with empirical work, practitioner definitions, formal methods, and recent LLM studies. Their evidence types matter: a formal result applies within its mathematical model; a case study reports its studied setting; a terminology standard clarifies representation. None validates this new skill as a whole.

The recommendations are design proposals. Their operational form lives in the [skill](../../skills/full-stack/SKILL.md); effectiveness must be assessed through the [evaluation protocol](../../evals/README.md).

## 1. Ground words in observable distinctions

Zave and Jackson argue for explicit grounding of requirements terminology in the environment and distinguish domain knowledge, requirements, and specifications. Their discussion of designations is especially relevant: a word needs an explanation establishing what it refers to. They also warn against expanding a goal indefinitely beyond the engineering task's subject matter. [1](https://cse.msu.edu/~chengb/RE-491/Papers/dark-corners-re-zave-jackson.pdf)

The practical consequence here is to define terms where different interpretations would change behavior. In a desktop, an installed application, running process, application instance, window, and surface are different concepts. “Running” cannot alternate between “process exists,” “window is visible,” and “launch request was accepted.” An entry should include examples, counterexamples, identity, and lifecycle when those distinctions matter.

Terminology work should concentrate on consequential ambiguity. A useful definition changes a decision or prevents a misunderstanding. A large synonym list that leaves the underlying concepts unspecified does neither. The scope of a glossary is the selected design, not all software engineering.

## 2. Keep concepts and relationships explicit

Gruber's ontology work explains explicit conceptualizations and the vocabulary used to represent entities and relationships. Its focus is knowledge sharing and interoperability, not modern LLM prompting. It supports making relation meanings explicit, but does not establish that adding an ontology improves coding outcomes. [9](https://tomgruber.org/writing/ontolingua-kaj-1993.pdf)

The proposed artifact model distinguishes a requirement from a component and a component from a work package. Relationships need verbs: a component **owns** state, an operation **requires** authority, a scenario **exercises** a contract, and a work package **implements** a requirement. An unlabeled arrow leaves these meanings unresolved.

The initial project should use a controlled vocabulary and typed links in Markdown. Calling this a formal ontology would overstate the artifact: it has no inference engine or machine-enforced model semantics. A schema can be introduced later if realistic evaluations expose recurring relation errors that justify deterministic checking.

## 3. Preserve context-dependent domain language

Evans's DDD reference treats a common model language within an explicitly bounded context. This is useful when a word has different legitimate meanings in different parts of a system. A bounded context concerns a model's applicability and consistency; it should not automatically become a deployment unit. This is a practitioner method reference, not an outcome study. [10](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf)

Full Stack should preserve the subject project's language and explain mappings when terms cross contexts. In MochiOS, “capability” already has a protection meaning. The skill should say “product capability” for an ability offered to a user and “authority capability” for a protected authorization object. It should not rename existing concepts to fit its own preferred nouns.

“Component,” “subsystem,” and “module” remain useful when their view is identified. Their ambiguity should be resolved through definitions. A new branded noun for every purpose can conceal rather than solve the semantic problem.

## 4. Distinguish obligations from alternatives

Goal-oriented requirements work distinguishes refinements that collectively satisfy a goal from alternative ways of satisfying it. Van Lamsweerde discusses responsibility assignment, conflicts, and obstacles to goal satisfaction. This explains why expanding an outline is weaker than refining a requirement: the relationship to the parent needs justification. [2](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

For the proposed skill, application launch may require identity resolution, authorization, execution, and observable outcome handling. It does not require implementing every possible launch mechanism. A preferred provider and an alternative provider remain alternatives until both are actually required. Window previews are not prerequisites for launching merely because mature docks support them.

Refinement should stop at a stable external boundary, a cohesive implementation unit with defined acceptance, or a named unresolved decision. Session duration can estimate work, but is not a semantic definition of a component. Granularity should follow uncertainty, coupling, and the cost of choosing incorrectly.

## 5. Refine requirements and architecture together

Nuseibeh's Twin Peaks proposal argues for concurrent, iterative requirements and architecture work. This challenges rigid ordering in which requirements are frozen before architectural exploration or a platform is selected before its behavioral consequences are understood. Only its central proposal is relied on here because direct full-text retrieval failed. [3](https://oro.open.ac.uk/2213/)

Full Stack should frame the outcome and constraints, sketch responsibilities, research important options, and revise the decomposition as fit gaps appear. An existing facility may change a component boundary. A missing platform primitive may expose an unrecognized prerequisite. Neither finding automatically changes the user's desired outcome.

For example, a prototype may suggest that clicking a running application focuses its window. Inspection may reveal support for multiple windows per application. The design then needs a selection policy, while the milestone can still exclude previews and a full task switcher. The process revisits assumptions without surrendering scope control.

## 6. Decompose around coherent responsibility

Parnas compares decompositions and argues for information hiding around design decisions rather than grouping by processing sequence. This matters when a planning skill might otherwise turn every workflow step into a service. The paper recognizes implementation tradeoffs; it is not an instruction to maximize modularity. [4](https://www.cs.lafayette.edu/~gexia/cs301/resources/parnas.html)

The proposed split test asks what state or policy a candidate component controls, what decisions it keeps private, what consumers need to know, and whether the interface supports meaningful independent change. A separate component needs a reason beyond having a separate document heading. Shared use by several features is not a reason to duplicate a provider under each feature.

An application registry can serve a launcher, file associations, and application management. Consumers reference one registry responsibility. An apps bar can own presentation state while deriving lifecycle facts from another owner. The publication mechanism for those facts is a separate decision that must fit the actual environment.

## 7. Separate architectural views

Kruchten's 4+1 model distinguishes logical, process, development, and physical views, connected through scenarios. It addresses diagrams that mix code, runtime entities, and hardware in undifferentiated boxes. The public ISO 42010 overview concerns architecture descriptions and the conventions supporting them; it does not prescribe this project's workflow. [5](https://www.cs.ubc.ca/~gregor/teaching/papers/4%2B1view-architecture.pdf), [6](https://www.iso.org/standard/74393.html)

The skill should produce the views needed for consequential questions. A responsibility tree locates concerns. An interaction flow explains behavior over time. A state model identifies legal transitions. A code mapping identifies implementation locations. A delivery graph orders work. Authority crossing protection domains may require a trust-boundary view.

These representations overlap without being interchangeable. A runtime dependency cycle can be valid in an event-driven design; a cycle among mandatory implementation prerequisites prevents a simple execution order. An application can own several windows without owning composition. A Rust crate may contain several responsibilities without requiring several processes.

## 8. Start interaction design from tasks

Lewis and Rieman organize interaction design around representative tasks and use them to develop and evaluate the design. They explicitly distinguish prototype behavior from finished underlying functionality. This provides a practical bridge from visual references to behavioral analysis. [11](https://cspages.ucalgary.ca/~tam/2001/hci_topics/papers/LewisRiemanBook/chap-1.html)

A prototype supplies evidence about layout, hierarchy, feedback, and demonstrated interaction. It does not establish persistence, authority, concurrency, or recovery. The skill should identify behaviors that are shown, requested, or inferred and carry the reference forward so infrastructure elaboration does not erase the intended experience.

Useful apps-bar questions concern applications that are absent, starting, visible, minimized, or unable to launch. Keyboard interaction and accessibility must be considered where the selected task depends on them. This does not require inventing an entire desktop service catalog merely to fill a checklist.

## 9. Make quality requirements observable

The SEI tactics report connects concrete quality scenarios to design decisions. Its scenario structure names stimulus, source, affected artifact, environment, response, and response measure. This makes vague qualities assessable, while the report's worked examples do not establish universal predictive accuracy. [7](https://www.sei.cmu.edu/documents/704/2003_005_001_14213.pdf)

“Responsive launch feedback” requires identifying the triggering action and the expected observation in a stated environment. A numerical threshold needs a requirement, measurement, or explicitly proposed target as its origin. The skill must not invent a latency threshold and report it as an existing requirement.

Quality scenarios connect presentation and infrastructure. Slow registry access may motivate cached metadata, which introduces invalidation questions. A launch timeout needs an outcome policy. These are decisions tied to a particular behavior, not reasons to add caching and retries everywhere.

## 10. Use structured language carefully

EARS provides forms for ubiquitous, state-driven, event-driven, optional-feature, and unwanted behaviors, with combinations where appropriate. Its unwanted-behavior form makes failure responses visible. The original names should be retained rather than silently treating every conditional requirement as an invariant. [12](https://ccy05327.github.io/SDD/08-PDF/Easy%20Approach%20to%20Requirements%20Syntax%20%28EARS%29.pdf)

These patterns can clarify specifications but cannot define ambiguous nouns. “WHEN an app opens, the system shall update state” remains underspecified until the app identity, opening event, state owner, and observation are explained. An eventual-response obligation is also different from a condition required to hold continuously.

Contrasting examples can expose ambiguity: process creation succeeds but no window appears, or a second click occurs during launch. Where the difference affects the selected outcome, it should become an acceptance scenario. Elaborate wording is less useful than a distinction that an implementer can actually test.

## 11. Check composition as well as parts

Abadi and Lamport study how component specifications compose and refine higher-level specifications. Environment assumptions and temporal behavior are essential. Their work motivates explicit assumptions and composition review, but Markdown contracts do not inherit a proof of compositional correctness. [13](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Composing-Specifications.pdf)

The operational check compares producer guarantees with consumer assumptions. If an apps bar assumes an ordered lifecycle stream and the provider emits lossy notifications, the interface remains incomplete even with detailed documents on both sides. Provider semantics, consumer recovery, or the requirement must change.

The pieces must also jointly deliver the selected behavior. A launch service can correctly acknowledge acceptance while the overall design has no path for later failure to reach the user. Composition review should find that missing obligation rather than declaring success because every component has a test plan.

## 12. Allocate authority and lifecycle

End-to-end arguments ask where sufficient knowledge exists to implement a function completely, while allowing lower-level support. Protection principles such as complete mediation and least privilege constrain which components can authorize transitions. These concerns need to be considered together. [14](https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf), [15](https://web.mit.edu/Saltzer/www/publications/protection/Basic.html)

Each important state set needs a named authority or explicit coordination protocol. Readers, writers, derived views, persistence, failure, and recovery must agree with that allocation. “Shared ownership” is insufficient, but replicated or distributed authority is possible when coordination semantics are specified.

Rust introduces another meaning of ownership. RustBelt establishes safety results for its model and selected unsafe extensions, not arbitrary application correctness. Architectural authority, resource ownership, and human responsibility therefore require separate treatment. A borrowed reference says nothing by itself about whether its holder may launch an application or commit a business transition. [20](https://plv.mpi-sws.org/rustbelt/popl18/paper.pdf)

## 13. Preserve provenance through the design

Gotel and Finkelstein distinguish tracing requirement origins and development from tracing subsequent realization. Their investigation explains why links from requirement to code alone are insufficient and identifies organizational and maintenance costs that additional records do not automatically solve. [8](https://discovery.ucl.ac.uk/id/eprint/749/1/2.2_rtprob.pdf)

Full Stack should retain whether a requirement came from an explicit request, existing contract, observed behavior, or inference, then connect it to decisions, contracts, and checks. A derived matrix can help inspection without becoming an independently maintained roadmap.

An existing test may establish exercised behavior while the architecture specifies a different future placement. The skill must separate current state, target state, and migration. It should not promote the target into an implementation claim or turn an accidental implementation into a permanent product requirement.

## 14. Account for coordination and investigation cost

Conway connects design organization to communication paths. MacCormack and colleagues provide empirical evidence relevant to mirroring in studied software systems. They motivate checking coordination needs, not matching every component to a team or assuming more agents improve delivery. [16](https://www.melconway.com/Home/pdf/committees.pdf), [17](https://www.hbs.edu/ris/Publication%20Files/Research%20Policy%2041%20%282012%29%201309%E2%80%93%201324_c5c2350e-013c-4065-a2f9-d95eb32177d5.pdf)

Work packages should identify shared contract changes and prerequisite agreements. Independent files can depend on unsettled shared semantics. Conversely, closely related changes may belong in one coherent increment even when they touch several crates.

Boehm emphasizes risk-driven iteration; Lampson presents contextual hints instead of universal laws. Research effort here should follow uncertainty and decision consequence. An expensive, difficult-to-reverse dependency deserves more investigation than a local representation choice. Requiring the same number of alternatives at every node would confuse effort with evidence. [18](https://www.cs.hmc.edu/~markk/SWE_copies/boehmspiral.pdf), [19](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/acrobat-17.pdf)

## 15. Treat LLM assistance as an empirical question

The 2025 LLM requirements-engineering review reports concerns including consistency, structured representations, and experimental limitations. It supports evaluating a complete workflow rather than treating fluent output as correctness. It does not establish preferred wording for this skill. [21](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1519437/full)

The 2026 DDD prompting case study reports useful early language/context artifacts but accumulating errors in later aggregate and architecture stages. It involved one company, three models, and detailed German requirements, limiting generalization. The implication for this project is to re-ground consequential decisions between stages rather than blindly pass generated artifacts forward. [22](https://arxiv.org/html/2603.26244v1)

SpecFix studies ambiguity repair using generated programs and tests on coding benchmarks. It motivates evaluating whether clarification changes behavior, but it does not test system architecture. ClarifyCodeBench is a newer exploratory lead; its abstract contains an unresolved count, so no numerical conclusion is used here. [23](https://arxiv.org/html/2505.07270v3), [24](https://arxiv.org/abs/2607.00711v2)

Evaluation should use realistic requests and counterexamples: preserved exclusions, necessary prerequisites, consistent authorities, and usable handoffs with fewer unsupported assumptions. Checking only whether preferred headings appear would measure template imitation. A result from this project's author remains a self-review unless independently evaluated.

## 16. Use platform precedents with explicit fit limits

Wayland documents an input-to-render path with client rendering and compositor scene knowledge. Flatland describes independent client content combined into a system scene graph. They provide concrete precedents for responsibilities and interactions. [25](https://wayland.freedesktop.org/architecture.html), [26](https://fuchsia.dev/fuchsia-src/concepts/ui/scenic/flatland)

Neither selects an implementation for a custom Rust OS. Candidate dependencies still need checks against kernel interfaces, runtime, allocation, graphics capabilities, licensing, and integration cost. An idea can transfer even when the reference implementation cannot. Research should explicitly distinguish those decisions.

The MochiOS apps bar is consequently a useful worked example, not effectiveness evidence. Visible controls can be traced through application identity, lifecycle, surface presentation, and authority. Existing owners must be established from the current repository before proposing replacements.

## Proposed design method

The synthesis is an iterative sequence of framing, grounding, elaborating, allocating, resolving, specifying, and sequencing. These verbs are a project convention. A run can return to an earlier activity when evidence changes; a small request should not trigger a full-system audit.

The first control is scope. Classify discovered items as required now, existing dependencies, unresolved prerequisites, or deferred enhancements. This prevents the analysis needed to understand a dependency chain from becoming authorization to implement the whole chain. Optional discoveries should not become mandatory work because they appeared in research.

The second control is semantic consistency. Requirements, components, interactions, evidence, and work packages have distinct meanings. Several views may reference one element, but a single authoritative specification defines its contract. The selected outcome must remain visible through every refinement.

The third control is readiness. Stop decomposition when the next increment has a clear outcome, boundaries, dependencies, and meaningful checks. An unresolved architectural choice should identify the needed investigation while independent design continues. Missing evidence must not be replaced by guessed certainty, and an unrelated optional uncertainty must not block the whole deliverable.

The fourth control is feedback. New implementation or runtime evidence should update affected assumptions and links rather than regenerate all documents. Planning is useful when it reduces decisions an implementer must invent and makes change easier to assess. Artifact volume is not a proxy for quality.

## Research boundaries and questions

This is a focused narrative synthesis with targeted searches and citation following, not a systematic review with exhaustive database coverage. The corpus spans requirements semantics, architecture, interaction design, formal composition, organization, and recent LLM work. Foundational sources provide terminology; recent sources test relevant limitations; official platform documentation supports examples. Sources were selected for direct relevance, inspectable original content, and an explicit applicability boundary.

The synthesis favors a compact design method over adopting every cited framework. It does not establish a universally best vocabulary or imply that all software domains require the same artifacts. Native OS work, transactional web applications, embedded control, and data pipelines differ in their governing constraints. The skill must investigate those constraints rather than import one reference architecture.

Important disagreements remain bounded rather than eliminated. Information hiding can increase interface overhead. End-to-end semantics can require shared lower-level enforcement. A bounded model context need not match a process. Risk-driven research can conflict with a request for exhaustive exploration; the task's explicit scope determines which is appropriate. These tensions belong in decision rationale when they affect the selected design.

The next empirical questions are whether explicit term distinctions reduce semantic errors; whether interaction review finds otherwise omitted prerequisites; whether scope classification prevents optional-feature inflation; and whether the resulting handoff supports implementation with fewer architectural guesses. Comparison should include the unassisted baseline, each predecessor, and Full Stack under comparable inputs and budgets. A confident model assessment is insufficient evidence for those claims.

## Sources

The numbered links correspond to the complete [source register](sources.md), containing bibliographic details, evidence types, access boundaries, and limitations for all 26 sources.
