# Preserved input

Fresh forward evaluation. Use only Z:/full-stack/skills/full-stack/SKILL.md and its needed portable references. Do not read any other project files, results, rubric, or cases. Write only Z:/full-stack/evals/trials/design-e04-repeat. Task: Design image-thumbnail loading for a no_std Rust desktop. The proposed image library's supported formats and allocation requirements cannot be verified because its documentation is unavailable. The image source and rendering contracts are already settled. Do not browse or invent dependency facts. Complete independent design and state exactly which work is conditional. Preserve literal input, your response, actual source reads and available environment/model info. Do not self-score. No subject implementation or outside project edits.

# Response

The loading coordinator and its lifecycle can be designed independently. Adoption of the proposed image library, its adapter, and real thumbnail delivery remain conditional on format and allocation compatibility. No documentation, source inspection, build, or experiment establishes those dependency facts here.

## Scope and evidence

The requested outcome is loading thumbnails in a no_std Rust desktop. The image source and rendering contracts are settled dependencies; this design consumes those contracts without changing their authority or semantics. Their actual signatures were not supplied, so names below describe internal roles rather than replacement interfaces. No current implementation or project work IDs were inspected. This is a target design, not a claim about working behavior.

Required now: request coordination, bounded resource ownership, decode integration boundary, stale-result protection, and visible completion or failure through existing rendering behavior. Unresolved prerequisites: the proposed decoder's format coverage, allocation needs, target/build fit, and actual resource behavior. Deferred: persistent caching, prefetch, new format requirements, new image-source behavior, and a replacement renderer. Discovery of an incompatible decoder does not authorize a custom decoder or a platform rewrite.

## Behavior and authority

The existing UI owner requests a thumbnail for a source identity and desired thumbnail size using its settled source and rendering semantics. The coordinator owns pending jobs, request generations, cancellation state, and its resource budget. It does not own image contents or rendering state. The source retains authority over source identity, availability, bytes, and revisions as defined by its contract; the renderer retains presentation and graphics-resource authority.

Each request carries an internal slot identity and monotonically changing generation (with an explicit non-reuse policy while older work exists). Source identity and size remain associated with that request. A changed source, size, or reused UI slot creates a new generation. Only a completion matching the slot's live generation may be delivered for presentation. This prevents an old result replacing a newly requested thumbnail without requiring decoder cancellation support.

The state flow is queued -> reading -> decoding -> delivery pending -> completed, with failure or cancellation possible before completion. Queue admission failure is an explicit resource-limit outcome. Reading uses the established source contract. Decoding occurs outside the UI-sensitive execution path, through the platform's existing scheduling mechanism; no new thread API or executor is assumed. Delivery uses the established rendering contract. Completion means that contract's defined completion point, not merely that decoding returned bytes. If its completion is asynchronous, retain resources until its existing release/completion event permits reclamation.

On source or decode failure, terminate that generation and report failure using existing UI/rendering behavior. Internally distinguish source failure, unsupported input, invalid input, resource exhaustion, and decoder failure where the provider exposes those distinctions; otherwise retain a generic decode failure. Do not fabricate diagnostic precision. No automatic infinite retries: a new request or existing explicit retry action creates another generation. Cancellation immediately suppresses delivery; underlying work is interrupted only where existing contracts support it. Late results are released, never displayed. Shutdown stops admission, invalidates generations, and drains or cancels outstanding work according to provider contracts before releasing borrowed resources.

## Boundary and resource design

Use a coordinator and a thin decoder adapter as responsibilities, not necessarily separate crates or processes. The adapter hides the selected decoder's API and translates its actual results into the coordinator's owned success/failure representation. It does not promise unsupported formats, bounded allocations, scaling, or interruptibility. Keep decoder internals opaque. A separate source adapter or rendering abstraction is unnecessary unless inspection later shows an actual mapping gap.

The no_std coordinator uses core-compatible state operations and caller-provided bounded slots/buffers. It requires no hidden unbounded collection. This choice does not assert that the whole pipeline can run without an allocator. Whether the decoder can use caller buffers or requires alloc, a global allocator, or other facilities remains unresolved. Borrowed input must remain alive until the decoder finishes accessing it; ownership is transferred or retained according to the existing source contract. Output is owned by exactly one side at a time, with release governed by the renderer contract. Do not add unsafe lifetime extension to bridge a mismatch.

Expose configured limits for queued requests, in-flight jobs, input bytes, output dimensions, output bytes, and total loader-owned memory. Check arithmetic and output dimensions before reserving loader buffers; reject oversized requests explicitly. These checks alone cannot bound undocumented decoder scratch allocations, full-resolution intermediate buffers, or CPU usage. Real resource-bounded integration is conditional on establishing those behaviors. Use a conservative single in-flight decode as a reversible initial policy, but confirm a responsiveness budget against the actual desktop before adopting it for production. No latency or throughput results are claimed.

A decoder that produces full-resolution images might require a separate scaling responsibility, or the settled renderer might already provide it. Inspect that existing rendering capability and decoder evidence before choosing either. Do not prescribe scaling or pixel-layout conversions that duplicate settled behavior. The final adapter must produce the representation the renderer already accepts, including its size and lifetime constraints; whether the proposed library can meet this is conditional.

## Ordered work and exact conditions

The following is a proposed execution order, not a second work-status registry. When implementation is authorized, add the work to the subject project's existing ROADMAP.md; this evaluation does not edit that project registry.

1. **Ready now: coordinator design and isolated behavior checks.** Define the generation/state transitions, admission limits, cancellation, and resource-release obligations above. A future isolated coordinator implementation can use a scripted decoder double after confirming the existing project module conventions. The double returns controlled completion, error, and late-result events. It simulates no format support, allocation profile, decoder throughput, or production integration.
2. **Ready to specify, unavailable to close: dependency investigation.** Obtain primary documentation or inspect the exact proposed library version when access becomes possible, then compile and exercise it for the actual target. Establish supported formats against the project's required inputs, feature flags, no_std/alloc requirements, peak memory behavior, output representation, and whether thumbnail sizing is available. The required format list is not given here; use existing project requirements, without inventing a PNG/JPEG/etc. commitment. Record evidence and limits. This investigation determines reuse/adaptation feasibility. Adoption remains unresolved now.
3. **Conditional: real decoder adapter and resource sizing.** Requires step 2 to establish compatible format coverage and allocation/build behavior, plus inspection of the settled source and renderer signatures. Then map byte access and output ownership without altering those contracts, settle any necessary scaling/conversion gap, and choose concrete memory and responsiveness limits from the desktop's available budgets. If incompatible, report the precise gap and obtain a dependency decision before further decoder work.
4. **Conditional: real end-to-end loading and closure.** Requires the actual adapter, scheduling integration, resource limits, and real source/render binding. Exercise supported input -> thumbnail presentation, malformed/unsupported input -> existing failure behavior, rapid slot reuse, cancellation during decode, render rejection, oversized input, and shutdown. Measure peak memory and UI responsiveness with the real decoder. Passing isolated coordinator checks cannot close this step.

Planned independent checks cover out-of-order completions, source/size changes during decoding, queue saturation, stale delivery suppression, resource release exactly once, and shutdown with outstanding jobs. Planned real-provider checks cover format compatibility, allocation failure, build/target compatibility, output acceptance, and measured memory/latency limits. None were executed. The independent design is complete to the available evidence; real-library selection, adapter implementation, exact resource guarantees, and operational integration are explicitly conditional.

# Actual source reads

Only these portable skill files were read, with Get-Content; both calls completed with exit code 0 and no output truncation reported:

1. Z:/full-stack/skills/full-stack/SKILL.md (entire file).
2. Z:/full-stack/skills/full-stack/references/design-method.md (entire file).
3. Z:/full-stack/skills/full-stack/references/artifacts.md (entire file).
4. Z:/full-stack/skills/full-stack/references/research.md (entire file).

The latter three were read together in one Get-Content call. No subject source, external documentation, evaluation rubric, results, cases, or other project files were read. No browser calls were made. The available user-supplied AGENTS.md guidance and environment context were already present in the conversation; they were not filesystem reads. No domain terms or project workflow were edited.

# Available environment and model information

- Working directory supplied in context: Z:/full-stack.
- Shell: PowerShell; platform context: Windows paths.
- Date supplied in context: 2026-09-09; timezone: America/New_York.
- Writable workspace: Z:/full-stack; this task restricts writes to evals/trials/design-e04-repeat.
- Agent task identity: /root/design_e04_repeat.
- Developer identifies the assistant as Codex based on GPT-6. Exact serving model identifier, model build, sampling parameters, and reasoning configuration were not exposed to this agent.
- This artifact preserves the assigned literal input and authored response. No subject implementation, runtime tests, measurements, independent evaluation, or self-score were performed.
