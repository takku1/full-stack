# Optimizing cost while holding results

Research date: 2026-11-12. Question: how can Full Stack 0.4.0 cost less per run while producing the same or similar results? Numbers in brackets refer to the [source register](sources.md#sources-for-optimization-2026-11-12). Labels: **measured**, **internal**, **precedent**, **proposal**, as in [modular-redesign.md](modular-redesign.md).

## 1. Where the cost actually is

**Internal.** FS-009's explicit run ([results](../../evals/ab/results/2026-10-05-invoked/results.md)) shows the 0.3.0 skill's extra cost tracking extra *turns*, not instruction size alone:

| Case | Brief: turns / USD | Skill: turns / USD |
|---|---|---|
| bugfix | 8 / 0.100 | 14 / 0.166 |
| crosscut | 18 / 0.205 | 24 / 0.291 |
| feature | 10 / 0.110 | 11 / 0.171 |
| E04 (design) | 2 / 0.183 | 2 / 0.231 |

Every turn resends the conversation. With prompt caching, a repeated prefix is billed at 0.1× the base input price after it is first written (0.05× on Opus 5.5 and Sonnet 5.5). Writing it costs 1.25× for a 5-minute cache or 2× for a 1-hour cache [55]. So the instruction text a skill adds is cheap to *repeat*, but every additional tool call, file read, and written artifact adds new, uncached input and output. Where turns are equal (E04), the gap is smaller and comes from loading and producing more text. Output tokens cost several times input on current Claude models, so long written designs are expensive per token. This was not re-verified on the pricing page this session.

**Reading.** The order of leverage is: (1) fewer process turns, (2) less output, (3) less uncached input (file dumps, reference reads), (4) shorter instructions. The 0.4.0 core cut item 4 from about 3,400 to about 580 tokens. The larger savings are probably in items 1–3.

## 2. Techniques, evidence, and fit

| Technique | Evidence | Fit for Full Stack | Verdict |
|---|---|---|---|
| **Stage gating / progressive disclosure** (load only what applies) | Precedent [27], [28]; internal FS-009 | Already in 0.4.0: routine edit ≈ core only; stack flow only when a technology is chosen | Keep; measure the routing |
| **Fewer turns: batch reads, one-call scripts** | Proposal, grounded in section 1 | Tell the model to read all needed modules in one parallel batch; scripts do multi-step work in one call (`check_stack.py profiles` already intersects in one call) | **Do first** |
| **Proportional output** (one line for keep-current, tables over prose, "none" for empty sections) | Proposal; output priced higher | Templates already lean this way; add explicit length caps per artifact | **Do first** |
| **Observation masking** (drop old tool output, keep reasoning) | Measured: about half the cost of a raw agent at equal or slightly higher solve rate on SWE-bench Verified; matched LLM summarization; needed per-scaffold tuning [54] | Host-level, so a skill cannot change it. The skill can avoid creating bulk: read excerpts, have subagents return summaries only, don't re-read files | Adopt the skill-side habits |
| **Prompt caching** (stable prefix first) | Vendor docs: reads at 0.1× base (0.05× on Opus and Sonnet 5.5); prefix order tools → system → messages; any change invalidates later content; models have a minimum cacheable length (512 tokens on Haiku 5.5) [55] | Keep the core byte-stable (no dates, versions, or per-run text). Hosts handle the rest | Free; keep |
| **Model routing / cascades** (cheap model first, strong model where needed) | Measured: FrugalGPT reports up to 98% cost reduction matching GPT-4 on its benchmarks [56]; RouteLLM reports costs reduced "by over 2 times in certain cases" without compromising response quality [57]. Anthropic's research system paired an Opus lead with Sonnet subagents [29] | Route evidence gathering (versions, licenses, limits) to a cheaper subagent model; keep orchestration, intersection, and the decision on the main model | Promising; gate behind FS-018 evidence |
| **Automated prompt optimization** (GEPA, DSPy) | Measured: GEPA beats GRPO by 6% on average with up to 35× fewer rollouts, and beats MIPROv2 by over 10% [58]. The abstract makes no prompt-length claim. Practitioner reports, not independently verified: prompts grow unless length is constrained, and a strong reflection model is needed | Use only after FS-016 exists as a metric. Optimize grade minus a token penalty, with a length cap in the reflection step | Later; needs the evaluation first |
| **Prompt compression** (LLMLingua family) | Measured: up to 20× with small loss on its benchmarks; degrades past about 25–30× [52], [53] | Poor fit. Compressed text varies per query, so it defeats caching. Untested on agent instructions. It makes a maintained, human-read skill unreadable | Reject for instructions; at most for bulky tool output |
| **Instruction deduplication** | Precedent: fewer instructions followed more reliably [34]; vendor advice to keep only what the model lacks [27] | Remove text repeated between core, flows, and references; drop guidance the model follows unprompted (find out by ablation) | Do, verified by ablation |

## 3. Proposed changes to 0.4.0

Ranked by expected saving relative to risk. None is applied yet; each needs the check in section 4.

1. **Turn budget in the core.** "Read every file you need in one batch. Run each script once per stage. Don't re-read a file you've already read." Target: fewer turns on bugfix and crosscut, with the same hidden-check results.
2. **Output caps.** Decision record of at most about 250 words per affected layer. Keep-current layers get one line. A routine edit gets a change note of five lines or fewer. A design repeats nothing from the brief; it links to it.
3. **Evidence by excerpt.** In the stack flow, record the version, date, license, and source URL per candidate, not page summaries. Subagents return a fixed evidence table only.
4. **Cheaper evidence model** where the host supports per-subagent models: evidence gathering on a smaller model, decisions on the main one. Gated by FS-018.
5. **Ablation-driven dedup.** Remove one guidance block at a time (for example the design flow's generate guidance, or each layer module's "Traps" section). Keep removals that hold the grade. Then try sampled Shapley values over the modules (FS-017) to catch interactions that one-at-a-time ablation misses.
6. **GEPA-style optimization of flows** once FS-016 provides a metric: a length-penalized objective, a held-out case split, and a strong reflection model.

## 4. How to know results stayed "the same or similar"

"Similar" needs a margin decided *before* the run. Otherwise any result can be read as similar.

- **Non-inferiority design.** For each change, compare the optimized arm with the current arm on the same cases. Pre-register these margins: mean grade drop of at most 0.5 on the 10-point rubric; no new high-impact failures; every hidden check still passes. Use two one-sided tests or a bootstrap confidence interval on paired per-case differences [59]. Declare "similar" only if the whole interval clears the margin.
- **Repeats.** One session per cell, as in FS-009, cannot separate a change from noise. Use at least three sessions per case and arm, and report the variance.
- **Metric.** Report cost per *accepted* task (passes hidden checks and has no high-impact failure), not cost per run. A cheaper arm that fails more often is not cheaper.
- **Order.** Test one change at a time, cheapest-to-verify first (turn budget, output caps). Stack changes only after each holds.
- **Held-out cases.** Optimize on some cases and confirm on others. Otherwise the instructions get tuned to the test set.

## Boundaries

Section 1's turn/cost link comes from six cases with one session each and is correlational. The routing and compression numbers come from QA and chat benchmarks, not agentic design work. GEPA practitioner reports are anecdotal. The pricing ratios in section 1 should be checked against the current price list before cost projections are published.
