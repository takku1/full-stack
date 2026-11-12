"""Audit a Claude Code transcript for which Full Stack steps happened, and in what order.

Reads `claude -p --output-format stream-json` output or a saved Claude Code session file
(both are JSON lines whose assistant entries carry `message.content` tool uses and text).
Reports a timeline of recognised steps and order properties: was the assurance screen run
and assurance declared before the first code edit, did checks name assurance IDs, did the
run close, and what reasons were given for routine runs. Field reports and FS-015 did this
by hand; the pressure tests (evals/pressure.py) and trials use it to score sessions.

Usage: python evals/process_audit.py TRANSCRIPT.jsonl [--json]
Standard library only. It recognises commands and written text; it cannot see intent.
"""

import argparse
import json
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SHELL_TOOLS = {"Bash", "PowerShell"}
ROUTINE = re.compile(r"--routine\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))")


def load_events(path):
    events = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def actions(events):
    """Assistant tool uses and text blocks, in transcript order."""
    out = []
    for e in events:
        if e.get("type") != "assistant":
            continue
        for item in (e.get("message") or {}).get("content", []) or []:
            if item.get("type") == "tool_use":
                out.append(("tool", item.get("name", ""), item.get("input") or {}))
            elif item.get("type") == "text":
                out.append(("text", "", {"text": item.get("text", "")}))
    return out


def is_code(path):
    """A file edit that changes the subject rather than its design notes."""
    p = path.replace("\\", "/").lower()
    return bool(p) and not p.endswith((".md", ".markdown", ".txt")) and "/docs/" not in f"/{p}"


def classify(kind, name, data):
    """Steps one action evidences, as (step, detail) pairs."""
    steps = []
    if kind == "text":
        if re.search(r"^\s*Screen:", data["text"], re.M):
            steps.append(("screen", "Screen line in reply"))
        if "| A-1" in data["text"]:
            steps.append(("table", "assurance table in reply"))
        return steps
    if name == "Skill" and "full-stack" in json.dumps(data):
        steps.append(("skill", data.get("skill") or data.get("command") or "full-stack"))
    if name == "Read":
        path = str(data.get("file_path", "")).replace("\\", "/")
        m = re.search(r"full-stack/(SKILL\.md|flows/\w+\.md|assurance/\w+\.md|layers/\w+\.md)", path)
        if m:
            steps.append(("read", m.group(1)))
    if name in EDIT_TOOLS:
        path = str(data.get("file_path") or data.get("notebook_path") or "")
        body = str(data.get("content") or data.get("new_string") or "") + json.dumps(data.get("edits") or [])
        if re.search(r"^\s*Screen:", body, re.M):
            steps.append(("screen", f"Screen line written to {path}"))
        if "| A-1" in body:
            steps.append(("table", f"assurance table written to {path}"))
        if "```json stack" in body:
            steps.append(("stack_block", path))
        steps.append(("code_edit" if is_code(path) else "doc_edit", path))
    if name in SHELL_TOOLS:
        cmd = str(data.get("command", ""))
        if "check_stack.py" in cmd:
            steps.append(("stack_profiles" if " profiles" in cmd else "stack_check", cmd))
        if "assurance.py" in cmd:
            steps.append(("screen" if " screen" in cmd else "table_check", cmd))
        if "run_guard.py" in cmd:
            for sub in ("start", "declare", "checks", "exec", "close", "finish", "report"):
                if re.search(rf"run_guard\.py[\"']?\s+(?:\S+\s+)*?{sub}\b", cmd):
                    steps.append((f"guard_{sub}", cmd))
                    break
            if "--assurance" in cmd:
                steps.append(("declared_table", cmd))
            m = ROUTINE.search(cmd)
            if m:
                steps.append(("declared_routine", next(g for g in m.groups() if g is not None)))
            if re.search(r"(?<![\w-])A-\d+(?!\w)", cmd) and re.search(r"\b(checks|exec)\b", cmd):
                steps.append(("assurance_check", cmd))
        elif re.search(r"\b(echo|cat|tee|printf|sed|Set-Content|Out-File|Add-Content)\b.*>", cmd) and not cmd.strip().startswith("git"):
            steps.append(("shell_write", cmd))
    return steps


def audit(events):
    timeline = []
    for index, (kind, name, data) in enumerate(actions(events)):
        for step, detail in classify(kind, name, data):
            timeline.append({"at": index, "step": step, "detail": detail[:300]})

    def first(*names):
        hits = [t["at"] for t in timeline if t["step"] in names]
        return min(hits) if hits else None

    code = first("code_edit")
    screen = first("screen")
    declared = first("declared_table", "declared_routine")
    before = lambda at: at is not None and (code is None or at < code)  # noqa: E731
    return {
        "skill_used": first("skill", "read") is not None,
        "stack_profiles_run": first("stack_profiles") is not None,
        "stack_check_run": first("stack_check") is not None,
        "screen": screen is not None,
        "screen_before_code": before(screen),
        "table": first("table") is not None,
        "table_checked": first("table_check") is not None,
        "guard_started": first("guard_start") is not None,
        "guard_before_code": before(first("guard_start")),
        "declared": declared is not None,
        "declared_before_code": before(declared),
        "declared_table": first("declared_table") is not None,
        "routine_reasons": [t["detail"] for t in timeline if t["step"] == "declared_routine"],
        "checks_recorded": first("guard_checks", "guard_exec") is not None,
        "checks_name_assurance_ids": first("assurance_check") is not None,
        "closed": first("guard_close", "guard_finish") is not None,
        "code_edits": sum(1 for t in timeline if t["step"] == "code_edit"),
        "shell_writes": sum(1 for t in timeline if t["step"] == "shell_write"),
        "timeline": timeline,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit a transcript for Full Stack flow steps.")
    parser.add_argument("transcript")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = audit(load_events(args.transcript))
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    for key, value in result.items():
        if key != "timeline":
            print(f"{key}: {value}")
    print("\ntimeline:")
    for t in result["timeline"]:
        print(f"  {t['at']:>4} {t['step']:<18} {t['detail'][:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
