# Full Stack

Full Stack turns a bounded software request into a researched, connected design across the relevant stack. It works from a prompt, roadmap slice, prototype, or existing repository and produces requirements, responsibility boundaries, interaction flows, specifications, and ordered implementation work.

The method is **requirements elaboration and architectural synthesis with traceability**. This is a descriptive framing, not a new academic discipline. The implementation is an initial research-informed agent skill; improved engineering outcomes have not yet been demonstrated.

Start with the [project framing](docs/project-framing.md), then the [research report](docs/research/foundations.md). The [terminology](skills/full-stack/references/terminology.md) defines the concepts used throughout. The [MochiOS example](docs/examples/mochios-desktop.md) shows how a visual concept becomes a bounded architectural design.

## CLI tools

[Install Claude Code and Codex CLI](docs/install-cli.md) on Windows, including API key storage in Windows Credential Manager.

## Skill

The portable skill lives in [skills/full-stack/SKILL.md](skills/full-stack/SKILL.md). Its supporting references are self-contained within that folder. Host applications may expose an installed skill with different invocation syntax; `full-stack` is its public name. This repository does not install it into a host application.

Example request:

> Use full-stack to elaborate the apps-bar milestone from ROADMAP.md. Preserve the existing architecture. Trace launch and running-state behavior through the stack, research unresolved technology choices, and produce linked component and interaction specifications. Keep window previews and application installation outside this milestone.

## Project contents

| Location | Purpose |
|---|---|
| [docs/index.md](docs/index.md) | Reading guide |
| [docs/install-cli.md](docs/install-cli.md) | CLI tool installation (Claude Code, Codex) |
| [docs/research](docs/research/foundations.md) | Academic foundations, source register, research boundaries |
| [docs/design-decisions.md](docs/design-decisions.md) | Rationale and differences from predecessor skills |
| [skills/full-stack](skills/full-stack/SKILL.md) | Portable skill and operational references |
| [evals](evals/README.md) | Behavioral cases and evaluation protocol |
| [ROADMAP.md](ROADMAP.md) | Remaining project work |

Recurspec and Architectural Reasoning remain independent. Full Stack can produce a design without either being installed; when a subject project already uses Recurspec, its contracts and roadmap remain authoritative.
