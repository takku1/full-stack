# FS-023 plugin smoke test, 2026-11-12

Operational plumbing only, not design quality. Harness: [`evals/plugin_smoke.py`](../plugin_smoke.py). Claude Code 2.1.322, Windows 11, main model `sonnet` (Claude Sonnet 5.5), plugin loaded with `--plugin-dir ./skill`. Each session ran in an empty `CLAUDE_CONFIG_DIR` (login copied) against a throwaway git repo. Authorized ceiling: $5. **Spent: $0.58** ($0.31 run 1, $0.27 rerun after fixes).

Retained here: `summary-run1.json`, `summary.json` (rerun), and unit-test output before and after the fixes. The raw stream-json transcripts are not committed, because they list the account's connected claude.ai integrations (see "Unexpected behavior").

## Live results

| Test | What it shows | Run 1 (before fixes) | Rerun (after fixes) | Turns | Cost |
|---|---|---|---|---|---|
| T1 discovery | Init lists `full-stack:full-stack` and the `stack-evidence` agent; `/full-stack:full-stack` loads and answers from the core | PASS | not rerun (unchanged) | 1 | $0.059 |
| T2 PreToolUse | In a guarded run, `Write b.txt` (outside the write set `a.txt`) is refused with the guard's reason; `b.txt` not created | PASS | PASS | 3 | $0.069 / $0.083 |
| T3 Stop | Unclean run (an out-of-scope file, no checks) makes the Stop hook continue the session; the model reports both problems and does not self-accept blockers | PASS | PASS | 2 | $0.086 / $0.111 |
| T4 evidence | `stack-evidence` ran on `claude-haiku-5-5` and returned two rows (SQLite, PostgreSQL) with release, date, license, the writer-concurrency limit, and primary-source URLs | PASS | not rerun (unchanged) | 2 | $0.095 |
| T5 shell write | `echo x > c.txt` through Bash is **not prevented** (by design, since PreToolUse covers file tools only) but the Stop hook **detects** it and the model reports it | not run | PASS | 3 | $0.079 |

Tokens per session were dominated by the cached prefix: about 14k–26k cache-write tokens and 14k–76k cache-read tokens, against 100–1,100 output tokens.

## Defects found (external review, 2026-11-12) and fixed under the freeze's defect exception

Each was first reproduced by a failing unit test against the unchanged 0.4.0 code ([before](plugin-smoke-2026-11-12/unit-before-fix.txt): 4 failures of 26). Then the smallest correction was applied ([after](plugin-smoke-2026-11-12/unit-after-fix.txt): 27 of 27 pass).

| ID | Defect | Reproduction | Fix |
|---|---|---|---|
| D1 | One `latest` run pointer, shared by every worktree (it lives in the git common directory). With runs in two worktrees, the hook in one worktree checked edits against the other's write set and **allowed** an edit it should block | `test_each_worktree_hook_checks_its_own_run` | Per-worktree pointer `latest-<hash of worktree path>`; the run record stores its worktree |
| D2 | Commands without `--run` (`report`, `check`, `close`) resolved the other worktree's run | `test_commands_without_run_id_resolve_this_worktrees_run` | Same pointer fix |
| D3 | `close` finished a run whose recorded checks had failed | `test_close_refuses_failed_checks_without_accept_blockers` | The latest result per criterion must pass; failures need `--accept-blockers`, and a corrected rerun clears them |
| D4 | Without Python the hook silently allowed everything, so the loss of enforcement was invisible | `test_hook_without_python_is_visible` | `guard_hook.sh` emits a host `systemMessage` ("guard inactive") on SessionStart and Stop when no Python is found; a SessionStart hook was added |
| D5 | Found while fixing D4: the rewritten launcher derived its folder with `${0%/*}`, which fails on Windows backslash paths | `test_hook_launcher_passes_event_to_guard` | Normalize separators before splitting |

## Limits and known gaps

- **Shell writes are detected, not prevented.** PreToolUse cannot know which files an arbitrary command will touch. The guarantee is detection at Stop, and the README already says so.
- **Two runs in the same worktree** now fail closed: the pointer names the most recent run, so edits that belong only to the earlier run are refused. Telling sessions apart would need a session identity the guard does not have.
- **Not exercised live:** two worktrees (covered by unit tests through the same hook code path), a real environment with no Python (covered by unit tests through the interpreter override), interrupted and resumed sessions, macOS/Linux, a marketplace install, an upgrade over an older install, and Codex.
- One session per test, so this is a plumbing check, not a reliability rate.

## Unexpected behavior

- **Isolation is incomplete.** An empty `CLAUDE_CONFIG_DIR` still loaded the account's claude.ai connectors (dozens of Gmail, Docs, and Calendar tool definitions) into every session. That adds tokens to every cell and leaks account integrations into transcripts. FS-016 must fix this, for example with `--strict-mcp-config` or an API-key profile without connectors, before comparing cost across arms.
- The hook path mixed separators (`Z:\full-stack\skill/full-stack/...`) and still worked.
- In T3 and T5 the model declined to run `close --accept-blockers` itself and asked the user. That is the intended authority boundary.
