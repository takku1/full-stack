"""Read-only packaging checks; no architectural or outcome claims."""

from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skill = root / "skill" / "full-stack"
    errors = []
    links = 0
    required = [skill / "SKILL.md", skill / "agents" / "openai.yaml"]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path}")
    files = list(root.rglob("*.md"))
    for path in files:
        raw = path.read_text(encoding="utf-8")
        if "[TODO:" in raw or "TODO: replace" in raw:
            errors.append(f"Unfinished scaffold: {path}")
        body = re.sub(r"```.*?```", "", raw, flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\(([^\n)]+)\)", body):
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0].strip("<>"))
            resolved = (path.parent / target).resolve()
            links += 1
            if not resolved.exists():
                errors.append(f"Broken local link: {path.relative_to(root)} -> {target}")
            if path.is_relative_to(skill) and not resolved.is_relative_to(skill):
                errors.append(f"Nonportable skill link: {path.relative_to(root)} -> {target}")
    cases = json.loads((root / "evals" / "cases.json").read_text(encoding="utf-8"))
    identifiers = [case["id"] for case in cases]
    if len(set(identifiers)) != len(identifiers):
        errors.append("Duplicate evaluation case IDs")
    for case in cases:
        if not case.get("prompt", "").strip():
            errors.append(f"Empty prompt: {case['id']}")
        for fixture in case["fixtures"]:
            if not (root / "evals" / fixture).is_file():
                errors.append(f"Missing fixture: {fixture}")
    for error in errors:
        print(error)
    print(f"Checked {len(files)} Markdown files, {links} local links, {len(cases)} cases; {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
