# Version 0.2.0 revision evidence

Date: 2026-09-09. Baseline: `19ddd35a7b2c3022f8b17b563b0b14d385089693`.

This record separates author review, fresh-agent generation, and executed checks. It does not establish academic validation, comparative superiority, or universal reliability. Proposal dispositions and source limits are in the [research review](../../docs/research/improvement-review.md).

## Acceptance and author self-review

| Criterion | Evidence |
|---|---|
| Preserve robust semantics | Entrypoint retains scope dispositions, distinct current/target/migration, authority/ownership/team distinctions, provider guarantees, three coverage views, usable readiness, evidence limits, and one registry. Terminology and upstream notice are unchanged. |
| Improve instruction cost | Token measurement below counts the entrypoint, conditional implementation route, and complete portable Markdown. |
| Support authorized build without changing design default | D-011, entrypoint mode selection, implementation reference, README prompts, and project framing agree. Existing Recurspec execution authority remains intact. |
| Make handoff executable | Work package names selected requirements, responsible paths, dependency availability, integration, checks, and closure evidence; temporary doubles have replacement conditions. |
| Preserve portability and proportionality | All operational references stay inside the skill; no new host/runtime dependency; routine edits remain excluded. |
| Retain evidence from realistic trials | Isolated raw inputs, source, tests, before/after artifacts, and observed limits live under trials. Results below distinguish generation from scoring. |

This semantic mapping is author self-review, not independent proof of instruction equivalence.

## Context measurement

`python evals/measure_context.py --baseline 19ddd35a7b2c3022f8b17b563b0b14d385089693` uses tiktoken 0.14.0, `o200k_base`, full Markdown including frontmatter, UTF-8 without BOM and LF newlines. Tokenizer data download initially failed under the sandbox; an approved retry succeeded. No tokenizer is required to use the portable skill.

| Loaded material | Before | After |
|---|---:|---:|
| Entrypoint | 1,130 | 998 |
| Detailed design method | 1,096 | 706 |
| Entrypoint plus implementation reference | No equivalent route | 1,462 |
| All portable Markdown, including notice | 5,969 | 5,972 |

The final entrypoint is 11.68% smaller; the method reference is 35.58% smaller. New implementation guidance and expanded handoff fields add only three tokens to the previous total Markdown count (0.05%). The intermediate revision was exactly equal in total cost; the later scope correction added three tokens. This does not measure billed tokens, host wrappers, reasoning, rereads, or task artifacts. Conditional loading varies by task. [Machine-readable counts](context-cost.json) retain each file's before/after cost.

## Evaluation provenance

Three fresh agents received only the revised portable skill, task inputs, and tools, with no forked author conversation, rubric, expected answers, or prior results. Separate author assessment reviews their retained artifacts. They ran one implementation trial each; they are not an independent research team or blinded outside scorers. Exact backend revision, sampling settings, and per-run token budgets were not exposed. No equal-budget baseline comparison was performed.

The follow-up policy changes were supplied in initial task inputs, with instructions to apply them after initial checks. These probe observed change locality but do not test wholly unanticipated changes. The existing-application baseline is a tiny supplied synthetic project, not a pilot in a production application.

The entrypoint and implementation reference were stable during the three implementation runs. The artifact work-package wording and design-method reference were revised during early trial execution; record exact read/version uncertainty rather than claim a frozen full-package experiment. None of the implementation agents used design-method.md. A separate design-case agent ran the seven raw cases without the rubric; cases share that agent's context, so they are not seven isolated model runs. After author assessment, the entrypoint scope sentence was strengthened and E04 was submitted to a new agent; initial outputs remain unchanged.

## Fresh implementation generation and author assessment

| Trial | Executed evidence | Author assessment and limits |
|---|---|---|
| [CLI input](../trials/cli/PROMPT.md), [design](../trials/cli/DESIGN.md), [outcome](../trials/cli/OUTCOME.md) | 26 initial and 30 follow-up real subprocess calls; import/update, rejected rows, missing input, SQLite-trigger rollback, normalized duplicates, and persisted list results | Selected behavior, real storage ownership, and policy locality met for exercised inputs. Name normalization changed validation while storage/CLI stayed intact. Input-format conventions were explicit. No crash-during-commit/concurrency study. |
| [Existing-feature input](../trials/existing/INPUT.md), [design](../trials/existing/docs/design/checkout.md), [results](../trials/existing/evidence/RESULTS.md) | Literal baseline: 1 passing test; 50% version: 9; 30% version: 9. Author reran final suite: 9 passed | Preserved checkout shape/default and pricing authority; integer validation, boundaries, and aggregate rounding exercised through real imports. Cap changed in pricing only; checkout hash unchanged. Tiny synthetic baseline limits transfer. |
| [Stateful input](../trials/stateful/INPUT.md), [design](../trials/stateful/DESIGN.md), [evidence](../trials/stateful/EVIDENCE.md) | Initial/follow-up HTTP logs cover forms/redirects, blank 400, absent/repeated delete 404, escaping, independent notes, actual process restart, 80/81 limits and legacy notes | Real HTTP-to-SQLite behavior met for exercised flows. Policy change stayed in Notes.create; presentation unchanged. Browser interaction/visual accessibility unexecuted. Restart followed committed responses, not interrupted writes. |

All three performed documentation-only label edits without new architecture. These are executed bounded samples, not evidence that every invocation stays small. Failure records retain sandbox temporary-directory failures and the CLI harness's unclosed test connection; the latter was fixed before successful reruns. Required escalations were approved. Failed-run scratch directories were subsequently removed; logs remain.

## Design-case author assessment

The [run provenance](../trials/design/PROVENANCE.md) records the raw inputs, actual reads, and unexecuted subject-project checks. “Met” below means the author found the applicable rubric dimensions supported by the response; it is not runtime validation.

| Case | Assessment | Concrete support or disagreement |
|---|---|---|
| [E01](../trials/design/E01/response.md) | Met | Distinguishes application/instance/window, pending versus running, owner inspection, unknown feedback and restart; excludes installation and platform replacement. |
| [E02](../trials/design/E02/response.md) | Met | BookingService owns cancellation/capacity; uncertain post-commit result reconciles through existing details; no new endpoint, invented path, or implementation. |
| [E03](../trials/design/E03/response.md) | Met | Adapter atomicity and acknowledgment investigation precede retry; row rejection versus whole-file policy remains unresolved; nonvisual shape preserved. |
| [E04](../trials/design/E04/response.md) | Partly met: scope | Honest unavailable codec evidence, conditional integration, and bounded double semantics. However, “Cache only bounded derived results” introduces caching without a requirement or deferred disposition. The rest of the design does not need this mechanism. |
| [E05](../trials/design/E05/response.md) | Met | Single coordinated focus authority, serialized dispatch/lifetime, revision/epoch recovery, no process-per-owner assumption. Checks remain proposed. |
| [E06](../trials/design/E06/response.md) | Met | Exact local label replacement, no architecture or research. Integrity checked against before.txt. |
| [E07](../trials/design/E07/response.md) | Met | One registry; final-notification loss addressed; reentrant bootstrap and outstanding fetches handled; runtime cycle separated from delivery order. |

Focused correction: apply the existing four scope dispositions to **proposed mechanisms** as well as discoveries. This closes a wording gap without adding a cache-specific prohibition. The initial E04 finding remains retained; a fresh repeat tests the revised instruction without being told the suspected error.

Author assessment of the [fresh E04 repeat](../trials/design-e04-repeat/trial.md): met for the supplied scope/evidence criteria. It explicitly defers persistent caching/prefetch, preserves source/rendering authority, and makes allocation, format coverage, adapter fit, and real integration conditional. It separates double-based coordinator checks from codec evidence. The response is more detailed than the first run; one changed output cannot establish causation or improved total token value. The final implementation wording was not otherwise changed after the three runtime trials.

## Executed checks

The installed `C:/Users/dcarn/.codex/skills/.system/skill-creator/scripts/quick_validate.py` reported “Skill is valid!” for the revised package. Validator SHA-256: `6068513D924ED3559E186DFCDEAD7439129828DCF402167FD925C06DFFBF2806` (no version exposed).

Initial link checking found links to this then-unwritten report, then relative links in flattened instruction snapshots. The report now exists; snapshots retain unchanged contents as `.md.txt` raw evidence instead of presenting incomplete copies as runnable skills. Final packaging/frontmatter/diff outputs are retained in validation.json. A diagnostic run overriding Git's configured newline conversion reported CRLF as trailing whitespace; the normal repository-configured `git diff --check` passed. Remaining evaluation work is tracked in the root [roadmap](../../ROADMAP.md).
