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
    workspace = []
    links = 0
    required = [skill / "SKILL.md", skill / "agents" / "openai.yaml"]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path}")
    entry = skill / "SKILL.md"
    if entry.is_file():
        # Hosts parse the header with a general YAML parser, which is stricter than
        # the SkillWren profile in places (an unquoted Enum[...] inside {...}).
        parts = entry.read_text(encoding="utf-8").split("---\n", 2)
        try:
            import yaml
        except ImportError:
            print("PyYAML unavailable; host frontmatter parse not checked.")
        else:
            try:
                header = yaml.safe_load(parts[1]) if len(parts) == 3 else None
                if not isinstance(header, dict) or not header.get("name") or not header.get("description"):
                    errors.append("SKILL.md frontmatter lacks name or description")
            except yaml.YAMLError as exc:
                errors.append(f"SKILL.md frontmatter is not valid YAML: {str(exc).splitlines()[0]}")
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
            if not resolved.is_relative_to(root):
                # Development-workspace references (sibling checkouts) are optional
                # context, not part of the distributed package.
                workspace.append(f"{path.relative_to(root)} -> {target}" + ("" if resolved.exists() else " (absent)"))
                continue
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
    for link in workspace:
        print(f"Optional workspace link: {link}")
    print(f"Checked {len(files)} Markdown files, {links} local links ({len(workspace)} optional workspace), {len(cases)} cases; {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
