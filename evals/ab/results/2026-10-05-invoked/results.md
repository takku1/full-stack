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
  "invoke": true,
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
| bugfix | plain | False | pass | 0 | 1 | 0 | 0.065 | 6 | 7 | 3 | 0 |
| bugfix | brief | explicit | pass | 0 | 2 | 0 | 0.100 | 8 | 9 | 1 | 0 |
| bugfix | skill | explicit | pass | 0 | 2 | 0 | 0.166 | 14 | 7 | 2 | 0 |
| crosscut | plain | False | pass | 0 | 3 | 0 | 0.175 | 18 | 7 | 3 | 0 |
| crosscut | brief | explicit | pass | 0 | 3 | 0 | 0.205 | 18 | 8.5 | 1 | 0 |
| crosscut | skill | explicit | pass | 0 | 3 | 0 | 0.291 | 24 | 8 | 2 | 0 |
| E02n | plain | False | n/a | 0 | 0 | 0 | 0.077 | 3 | 6 | 3 | 0 |
| E02n | brief | explicit | n/a | 0 | 0 | 0 | 0.094 | 4 | 9 | 1 | 0 |
| E02n | skill | explicit | n/a | 0 | 0 | 0 | 0.116 | 4 | 8 | 2 | 0 |
| E04 | plain | False | n/a | 0 | 0 | 0 | 0.182 | 2 | 7 | 3 | 1 |
| E04 | brief | explicit | n/a | 0 | 0 | 0 | 0.183 | 2 | 8.5 | 1 | 0 |
| E04 | skill | explicit | n/a | 0 | 0 | 0 | 0.231 | 2 | 8 | 2 | 0 |
| E06 | plain | False | n/a | 0 | 1 | 0 | 0.070 | 4 | 9 | 2 | 0 |
| E06 | brief | explicit | n/a | 0 | 1 | 0 | 0.075 | 4 | 9 | 1 | 0 |
| E06 | skill | explicit | n/a | 0 | 1 | 0 | 0.084 | 3 | 8 | 3 | 0 |
| feature | plain | False | pass | 0 | 2 | 0 | 0.115 | 8 | 8 | 2 | 0 |
| feature | brief | explicit | pass | 0 | 2 | 0 | 0.110 | 10 | 9 | 1 | 0 |
| feature | skill | explicit | pass | 0 | 2 | 0 | 0.171 | 11 | 7 | 3 | 0 |

| Arm | Total cost USD | Hidden checks passed | Mean grade |
|---|---|---|---|
| plain | 0.685 | 3/3 | 7.3 |
| brief | 0.768 | 3/3 | 8.8 |
| skill | 1.059 | 3/3 | 7.7 |
