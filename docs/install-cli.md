# CLI Tool Installation (Windows)

This guide covers installing Claude Code and Codex CLI on Windows, including API key storage in Windows Credential Manager.

## Prerequisites

- Windows 10 (build 19041+) or Windows 11
- Node.js 20+ LTS and npm (install via `winget install OpenJS.NodeJS.LTS`)
- PowerShell 5.1+ or Windows Terminal

## Claude Code

### Install

**Native installer (recommended, no Node required):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**npm (if Node is already installed):**

```powershell
npm install -g @anthropic-ai/claude-code
```

Verify:

```powershell
claude --version
```

### Authenticate

```powershell
claude
```

On first launch, Claude Code opens a browser for Anthropic account login. To use an API key instead:

```powershell
claude login --with-api-key
```

Paste your Anthropic API key when prompted.

### Store API Key in Windows Credential Manager

```powershell
cmdkey /generic:claude-api /user:anthropic /pass:YOUR_ANTHROPIC_API_KEY
```

Retrieve later with:

```powershell
cmdkey /list:claude-api
```

Delete with:

```powershell
cmdkey /delete:claude-api
```

## Codex CLI

### Install

**Native installer (recommended, no Node required):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

**npm (if Node is already installed):**

```powershell
npm install -g @openai/codex
```

Verify:

```powershell
codex --version
```

### Authenticate

```powershell
codex login
```

Opens a browser for ChatGPT OAuth. To use an API key directly:

```powershell
codex login --with-api-key
```

Paste your OpenAI API key when prompted.

Codex stores auth in its own encrypted keyring backend on Windows. No manual `cmdkey` entry is needed for Codex itself.

### Store OpenAI API Key in Windows Credential Manager

For scripts or tools that read the key outside Codex:

```powershell
cmdkey /generic:openai-api /user:openai /pass:YOUR_OPENAI_API_KEY
```

Retrieve:

```powershell
cmdkey /list:openai-api
```

Delete:

```powershell
cmdkey /delete:openai-api
```

## Updating

```powershell
# Claude Code
npm install -g @anthropic-ai/claude-code@latest

# Codex CLI
codex update
# or
npm install -g @openai/codex@latest
```

## Troubleshooting

- **`claude` or `codex` not recognized:** Open a new terminal after install. Check `npm config get prefix` and ensure the global `bin` directory is on your PATH.
- **Permission errors on npm global install:** Reinstall Node.js from the official installer (it sets correct permissions). Do not use `sudo`.
- **Codex keyring errors on Windows:** Codex v0.140+ uses encrypted local secrets with the OS keyring by default. If you see `TooLong` errors, update Codex (`codex update`).
- **PATH not updating:** Run `$env:PATH` in PowerShell to inspect. Add `$(npm config get prefix)` to your user PATH if missing, then restart the terminal.
