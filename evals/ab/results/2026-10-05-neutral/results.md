# Context-dose results

Meta: `{
  "model": "claude-sonnet-5-5",
  "budget_usd": 1.0,
  "claude": "2.1.289 (Claude Code)",
  "tools": [
    "Read",
    "Edit",
    "Write",
    "Glob",
    "Grep",
    "Skill",
    "Bash(python:*)",
    "Bash(python3:*)",
    "Bash(py:*)",
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)"
  ],
  "arms": [
    "plain",
    "brief",
    "skill"
  ],
  "invoke": false,
  "skill_files": [
    "NOTICE.md",
    "SKILL.md",
    "agents\\openai.yaml",
    "references\\artifacts.md",
    "references\\design-method.md",
    "references\\existing-projects.md",
    "references\\implementation.md",
    "references\\research.md",
    "references\\terminology.md",
    "scripts\\run_guard.py"
  ]
}`

| Case | Arm | Skill invoked | Hidden checks | Outside expected files | Files changed | Questions | Cost USD | Turns | Grade | Rank | High-impact |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bugfix | plain | False | pass | 0 | 1 | 0 | 0.077 | 5 | 9 | 1 | 0 |
| bugfix | brief | False | pass | 0 | 1 | 0 | 0.077 | 5 | 8 | 2 | 0 |
| bugfix | skill | False | pass | 0 | 1 | 0 | 0.077 | 5 | 8 | 3 | 0 |
| crosscut | plain | False | pass | 0 | 3 | 0 | 0.227 | 22 | 7 | 3 | 0 |
| crosscut | brief | False | pass | 0 | 3 | 0 | 0.226 | 18 | 9 | 1 | 0 |
| crosscut | skill | False | pass | 0 | 3 | 0 | 0.217 | 20 | 8 | 2 | 0 |
| E02n | plain | False | n/a | 0 | 0 | 0 | 0.074 | 3 | 7 | 2 | 0 |
| E02n | brief | False | n/a | 0 | 0 | 0 | 0.094 | 5 | 8 | 1 | 0 |
| E02n | skill | True | n/a | 0 | 0 | 0 | 0.098 | 5 | 6 | 3 | 0 |
| E04 | plain | False | n/a | 0 | 0 | 0 | 0.188 | 2 | 8 | 2 | 0 |
| E04 | brief | True | n/a | 0 | 0 | 0 | 0.195 | 4 | 7.5 | 3 | 0 |
| E04 | skill | True | n/a | 0 | 0 | 0 | 0.278 | 5 | 9 | 1 | 0 |
| E06 | plain | False | n/a | 0 | 1 | 0 | 0.072 | 4 | 7 | 3 | 1 |
| E06 | brief | False | n/a | 0 | 1 | 0 | 0.071 | 4 | 8 | 2 | 0 |
| E06 | skill | False | n/a | 0 | 1 | 0 | 0.080 | 5 | 9 | 1 | 0 |
| feature | plain | False | pass | 0 | 2 | 0 | 0.081 | 5 | 6 | 3 | 1 |
| feature | brief | False | pass | 0 | 2 | 0 | 0.112 | 12 | 9 | 1 | 0 |
| feature | skill | False | pass | 0 | 2 | 0 | 0.115 | 11 | 8 | 2 | 0 |

| Arm | Total cost USD | Hidden checks passed | Mean grade |
|---|---|---|---|
| plain | 0.718 | 3/3 | 7.3 |
| brief | 0.775 | 3/3 | 8.2 |
| skill | 0.865 | 3/3 | 8.0 |
