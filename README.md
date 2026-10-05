# Full Stack

Full Stack turns a bounded software request into a connected design across the relevant stack, then carries it through implementation when requested. It defines requirements, ownership, contracts, and ordered work from a prompt, roadmap slice, prototype, or existing repository. Research targets decisions that could change the design.

The method is **requirements elaboration and architectural synthesis with traceability**. Package release 0.3.0 (see [ROADMAP.md](ROADMAP.md) for open work). This is a research-informed instruction skill, not an agent runtime or an academically validated method; comparative improvement remains unestablished.

Start with the [project framing](docs/project-framing.md), then the [research report](docs/research/foundations.md). The [terminology](skill/full-stack/references/terminology.md) defines the concepts used throughout. The [MochiOS example](docs/examples/mochios-desktop.md) shows how a visual concept becomes a bounded architectural design.

## Install

The package is the whole [skill/full-stack](skill/full-stack/SKILL.md) folder (entrypoint, references, notice), not `SKILL.md` alone. Install and reinstall with the scripts; a manual copy skips the conflict, backup, and hash checks.

| Platform | Claude Code, user-wide | Claude Code, one project | Codex too |
|---|---|---|---|
| Windows | `.\install.ps1 -Target Claude` | `.\install.ps1 -Target Claude -ProfileDirectory <project>` | `-Target Both` (the default) |
| macOS / Linux | `./install.sh --target claude` | `./install.sh --target claude --home <project>` | `--target both` (the default) |

User-wide installs land in `~/.claude/skills/full-stack` (Codex: `~/.agents/skills/full-stack`); the project form lands in `<project>/.claude/skills/full-stack`. Add `-Preview` / `--preview` to see each destination's state (new, unchanged, update) and any installed file that differs from the source, without copying. An update stages and hash-checks the new copy first, moves the previous copy to `.full-stack-backups/<host>-<timestamp>` under the profile (outside every skills folder, so hosts never load it), and restores it if the final move fails. An unexpected file or a redirected path stops installation before anything changes. `install.sh` has been exercised under Git Bash only, not yet on macOS or Linux. Hash equality proves the copy matches this checkout, not that the checkout is trustworthy. Neither script installs a CLI or calls a model. Locations follow the [Codex documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills). Setting up the CLIs themselves on Windows is a separate [guide](docs/install-cli.md); its commands have not been re-verified for this release.

## Use

The skill is meant for changes that cross components, state, or contracts. Invoke it by name (in Claude Code, `/full-stack <request>`, or "use full-stack to ..."). Hosts may also select it automatically from its description; how often that happens has not been measured. For a one-file fix, plain prompting is usually enough.

What it does, by request type:

| Request | Questions it may ask | Files it may write |
|---|---|---|
| Routine edit ("rename this label") | Only if the outcome is unclear | A short entry in the project's existing tracker, if one exists |
| Design only | Unclear outcome; approval for a costly-to-reverse commitment | One design file (see below) and the tracker entry. Say "keep it in chat" for no files |
| Design and build | The above, plus acceptance criteria only when they cannot be derived | The design, the code edits, and the tracker entry |

Design files go, in order of preference: into the project's existing design note for that component; into its documented design location; else `docs/design/<outcome-slug>.md`. Rerunning updates the same file. Project instructions win: if a project forbids new documentation files, the design stays in chat. The skill never creates a new tracker file without being asked.

If you decline a costly commitment, the design is still filed but every piece of work that depends on it is marked conditional and is not built; independent work proceeds. If you dismiss the question, nothing is written. To build a design you already accepted, pass it back ("implement the design in docs/design/x.md"); the skill rechecks facts it relied on rather than redesigning.

Design-only example:

> Use full-stack to elaborate the apps-bar milestone from ROADMAP.md. Preserve the existing architecture. Trace launch and running-state behavior through the stack, research unresolved technology choices, and produce linked component and interaction specifications. Keep window previews and application installation outside this milestone.

Design-and-implementation prompt (replace brackets):

```text
Use full-stack to design and implement [outcome] in [repository].
Required behavior: [observable success, relevant failures, lifecycle].
Constraints: [existing stack, compatibility, resource limits].
Excluded: [features outside this milestone].
Preserve existing owners and contracts. Implement and exercise real integration
until the selected criteria are met or concrete blockers prevent progress.
Report executed checks and limits; record unfinished work in the existing roadmap.
```

The host supplies editing, execution tools, and permissions; the skill cannot override them. See the [implementation reference](skill/full-stack/references/implementation.md) and [revision evidence](evals/results/revision-review.md).

## What is enforced, and by what

Most of this skill is instructions the model follows. These parts are checked mechanically:

| Guarantee | Checked by | When |
|---|---|---|
| Header parses as YAML; flows are well-formed (values defined before use, every file touched is declared, nothing written before a question the user could dismiss) | SkillWren validator, `evals/check_artifacts.py` | Before release |
| Installed files equal this checkout | Installer SHA256 checks | Install |
| Edits stay inside the work package's declared write set | `scripts/run_guard.py check` | During implement, in a git repository |
| Uncommitted edits made outside the run are not touched | `run_guard.py start` refuses them; `check` flags any change to them | Same |
| Parallel workers do not claim overlapping files, including across git worktrees | `run_guard.py start` (exit 3 on overlap) | Same |
| Reported checks were actually run, with their real exit codes | `run_guard.py exec` records them; `report` prints them | Same |

Everything else relies on the model following the instructions: when to ask, when scope is ambiguous, design quality, not inventing interfaces, and honest evidence when the guard cannot run. Header fields such as `authority`, `effects`, and `budget` are declarations; no host enforces them. Your host's permission mode is the only hard boundary on what the model can do. Whether the instructions help is measured by the [comparison harness](evals/README.md#ab-comparison-with-plain-claude-code). The [first run](evals/results/context-dose-2026-10-05.md) found that a 312-token brief scored best on small and medium tasks.

`run_guard.py` needs Python 3 and git. It writes run records under the repository's git directory (`.git/full-stack-runs/`), never into the working tree. Files several workers must edit can be claimed with `--shared`: overlapping claims are then allowed, and uncommitted hunks that already exist when the run starts are protected line by line.

### Optional: make the host run the guard

A skill cannot install host configuration, so by default the guard runs only when the model remembers to run it. To make Claude Code enforce it, add this to a project's `.claude/settings.json` (or your user settings), adjusting the script path:

```json
{
  "hooks": {
    "PreToolUse": [{ "matcher": "Edit|Write|MultiEdit|NotebookEdit",
      "hooks": [{ "type": "command", "command": "python ~/.claude/skills/full-stack/scripts/run_guard.py hook" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python ~/.claude/skills/full-stack/scripts/run_guard.py hook" }] }]
  }
}
```

While a guarded run is open, the PreToolUse hook blocks any edit outside its write set and tells the model why. The Stop hook keeps the session going while the run has scope violations or no recorded checks. Add `--require-run` to the PreToolUse command to block all edits in a git repository until a run is started. With no open run and without that flag, the hook does nothing. The PreToolUse block was checked in a live headless Claude Code 2.1.289 session on 2026-10-05: the edit was refused, and the model reported the guard's reason. The Stop hook is covered by unit tests only. Edits made through shell commands bypass PreToolUse; the Stop check still catches them.

## Reading SKILL.md

The entrypoint is written in [SkillWren](docs/design-decisions.md#d-013-adopt-a-logic-first-entrypoint) structure: a header, a `contract` block of resources and invariants, and two `logic` blocks (`design`, `implement`). Nothing executes these blocks. The model reads them as ordered instructions, and the file's appendix defines every step in plain language. Claude Code and Codex read only `name` and `description` from the header. `version: 0.4.1` is the SkillWren format version, not this package's release.

Instruction size, approximate (characters / 4): the entrypoint is about 3,400 tokens (header ~400, body ~3,000). A substantial design also reads the artifact reference (~1,200) and others as needed; a build reads the implementation reference (~1,000). Questions and written files usually cost more than the instructions do.

## Project contents

| Location | Purpose |
|---|---|
| [docs/index.md](docs/index.md) | Reading guide |
| [docs/install-cli.md](docs/install-cli.md) | Windows CLI setup for Claude Code and Codex (separate from installing this skill) |
| [docs/research](docs/research/foundations.md) | Academic foundations, source register, research boundaries |
| [docs/design-decisions.md](docs/design-decisions.md) | Rationale and differences from predecessor skills |
| [skill/full-stack](skill/full-stack/SKILL.md) | Portable skill and operational references |
| [evals](evals/README.md) | Behavioral cases, evaluation protocol, A/B harness |
| [ROADMAP.md](ROADMAP.md) | Remaining project work |

Recurspec and Architectural Reasoning remain independent. Full Stack can produce a design without either being installed; when a subject project already uses Recurspec, its contracts and roadmap remain authoritative.
