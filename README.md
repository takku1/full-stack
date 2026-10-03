# Full Stack

Full Stack turns a bounded software request into a connected design across the relevant stack, then carries it through implementation when requested. It defines requirements, ownership, contracts, and ordered work from a prompt, roadmap slice, prototype, or existing repository. Research targets decisions that could change the design.

The method is **requirements elaboration and architectural synthesis with traceability**. Version 0.2.0 adds an authorized implementation path. This is a research-informed instruction skill, not an agent runtime or an academically validated method; comparative improvement remains unestablished.

Start with the [project framing](docs/project-framing.md), then the [research report](docs/research/foundations.md). The [terminology](skill/full-stack/references/terminology.md) defines the concepts used throughout. The [MochiOS example](docs/examples/mochios-desktop.md) shows how a visual concept becomes a bounded architectural design.

## CLI tools

[Install Claude Code and Codex CLI](docs/install-cli.md) on Windows, including API key storage in Windows Credential Manager.

## Skill

The portable skill lives in [skill/full-stack/SKILL.md](skill/full-stack/SKILL.md). The entrypoint is a SkillWren logic-first contract (validator-checked); method prose lives in the references, self-contained within that folder. Host applications may expose an installed skill with different invocation syntax; `full-stack` is its public name.

Run the Windows [installer](install.ps1) from this checkout:

```powershell
.\install.ps1                 # Install/reinstall for both hosts
.\install.ps1 -Target Codex   # Or -Target Claude
```

It copies the portable package into the user's `.agents/skills/full-stack` for Codex and `.claude/skills/full-stack` for Claude Code, checking every file's SHA256. Reinstall overwrites known package files; unexpected files or redirected paths stop installation before copying. `-ProfileDirectory` selects a different user profile or an isolated test destination. The script installs instructions only; it does not install either CLI or call a model. Locations follow the [Codex documentation](https://learn.chatgpt.com/docs/build-skills) and [Claude Code documentation](https://code.claude.com/docs/en/skills).

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

A build request authorizes implementation within its scope; a design-only request ends with a handoff. The host must load the skill and provide editing/execution tools and any needed runtime. The skill cannot supply these capabilities or override host permissions. See the [implementation reference](skill/full-stack/references/implementation.md) and [revision evidence](evals/results/revision-review.md).

## Project contents

| Location | Purpose |
|---|---|
| [docs/index.md](docs/index.md) | Reading guide |
| [docs/install-cli.md](docs/install-cli.md) | CLI tool installation (Claude Code, Codex) |
| [docs/research](docs/research/foundations.md) | Academic foundations, source register, research boundaries |
| [docs/design-decisions.md](docs/design-decisions.md) | Rationale and differences from predecessor skills |
| [skill/full-stack](skill/full-stack/SKILL.md) | Portable skill and operational references |
| [evals](evals/README.md) | Behavioral cases and evaluation protocol |
| [ROADMAP.md](ROADMAP.md) | Remaining project work |

Recurspec and Architectural Reasoning remain independent. Full Stack can produce a design without either being installed; when a subject project already uses Recurspec, its contracts and roadmap remain authoritative.
