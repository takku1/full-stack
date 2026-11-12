"""Read-only packaging checks; no architectural or outcome claims."""

from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote


LAYER_KEYS = ("layer", "decides", "constrains", "criteria", "evidence", "tags")
TAG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(path):
    parts = path.read_text(encoding="utf-8").replace("\r\n", "\n").split("---\n", 2)
    if len(parts) != 3 or parts[0].strip():
        return None
    import yaml  # caller handles ImportError
    return yaml.safe_load(parts[1])


def check_layers(skill, layers):
    """Every layer module shares one interface (docs/design/modular-layers.md)."""
    errors = []
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("PyYAML unavailable; layer frontmatter not checked.")
        return errors
    for name in layers:
        path = skill / "layers" / f"{name}.md"
        if not path.is_file():
            continue
        try:
            header = frontmatter(path)
        except Exception as exc:  # yaml.YAMLError and friends
            errors.append(f"{path.name}: frontmatter is not valid YAML: {str(exc).splitlines()[0]}")
            continue
        if not isinstance(header, dict):
            errors.append(f"{path.name}: missing frontmatter")
            continue
        missing = [key for key in LAYER_KEYS if key not in header]
        if missing:
            errors.append(f"{path.name}: frontmatter lacks {missing}")
        if header.get("layer") != name:
            errors.append(f"{path.name}: layer field is {header.get('layer')!r}, expected {name!r}")
        for key in LAYER_KEYS[1:]:
            if key in header and not isinstance(header[key], list):
                errors.append(f"{path.name}: {key} must be a list")
        for tag in header.get("tags") or []:
            if not TAG.match(str(tag)):
                errors.append(f"{path.name}: tag {tag!r} is not kebab-case")
    return errors


def check_rules(skill):
    path = skill / "rules" / "compatibility.json"
    if not path.is_file():
        return []
    try:
        rules = json.loads(path.read_text(encoding="utf-8"))["rules"]
    except (json.JSONDecodeError, KeyError) as exc:
        return [f"compatibility.json unreadable: {exc}"]
    errors, ids = [], set()
    for rule in rules:
        rid = rule.get("id")
        if not rid or rid in ids:
            errors.append(f"compatibility.json: missing or duplicate id {rid!r}")
        ids.add(rid)
        if not rule.get("why"):
            errors.append(f"compatibility.json: {rid} has no 'why'")
        if not (rule.get("requires") or rule.get("excludes")):
            errors.append(f"compatibility.json: {rid} has neither 'requires' nor 'excludes'")
        for section in ("when", "requires", "excludes"):
            for tags in (rule.get(section) or {}).values():
                for tag in tags:
                    if not TAG.match(tag):
                        errors.append(f"compatibility.json: {rid} tag {tag!r} is not kebab-case")
    return errors


DISCIPLINES = ("security", "verification", "reliability", "observability", "operations", "performance",
               "privacy", "ux", "maintainability", "cost", "compliance")
SECTIONS = ("## Policy", "## Framework", "## How to", "## Checks")


def check_assurance(skill):
    """Every discipline module keeps Policy, Framework, How to, and Checks, and the flow links each one."""
    errors = []
    flow = skill / "flows" / "assurance.md"
    flow_text = flow.read_text(encoding="utf-8") if flow.is_file() else ""
    for name in DISCIPLINES:
        path = skill / "assurance" / f"{name}.md"
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        positions = [text.find(h) for h in SECTIONS]
        if -1 in positions or positions != sorted(positions):
            errors.append(f"assurance/{name}.md: needs sections {list(SECTIONS)} in order")
        try:
            header = frontmatter(path)
        except Exception as exc:
            errors.append(f"assurance/{name}.md: frontmatter invalid: {exc}")
            continue
        if not isinstance(header, dict) or header.get("discipline") != name:
            errors.append(f"assurance/{name}.md: discipline field must be {name!r}")
            continue
        for key in ("triggers", "tier2_when"):
            if not isinstance(header.get(key), list) or not header[key]:
                errors.append(f"assurance/{name}.md: {key} must be a non-empty list")
        if f"../assurance/{name}.md" not in flow_text:
            errors.append(f"flows/assurance.md does not link assurance/{name}.md")
    return errors


def check_plugin(root):
    """Plugin root is skill/; the marketplace at the repo root points to it."""
    errors = []
    plugin = root / "skill"
    try:
        manifest = json.loads((plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        hooks = json.loads((plugin / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"plugin files unreadable: {exc}"]
    if manifest.get("name") != "full-stack":
        errors.append("plugin.json name must be full-stack")
    for path in manifest.get("skills", []):
        if not (plugin / path / "SKILL.md").is_file():
            errors.append(f"plugin.json skills path has no SKILL.md: {path}")
    entries = [p for p in market.get("plugins", []) if p.get("name") == "full-stack"]
    if not entries or not (root / entries[0]["source"] / ".claude-plugin" / "plugin.json").is_file():
        errors.append("marketplace.json does not point at the plugin root")
    elif entries[0].get("version") != manifest.get("version"):
        errors.append("marketplace and plugin.json versions differ")
    for event, groups in hooks.get("hooks", {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"\s]+)", hook.get("command", "")):
                    if not (plugin / ref).is_file():
                        errors.append(f"hooks.json {event} references missing {ref}")
    for agent in (plugin / "agents").glob("*.md"):
        try:
            header = frontmatter(agent)
        except Exception as exc:
            errors.append(f"{agent.name}: frontmatter invalid: {exc}")
            continue
        if not isinstance(header, dict) or not header.get("name") or not header.get("description"):
            errors.append(f"{agent.name}: agent needs name and description")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skill = root / "skill" / "full-stack"
    errors = []
    workspace = []
    links = 0
    layers = ["data", "runtime", "interface", "client", "platform", "crosscut", "custom"]
    required = [skill / "SKILL.md", skill / "agents" / "openai.yaml",
                skill / "flows" / "design.md", skill / "flows" / "stack.md", skill / "flows" / "implement.md",
                skill / "templates" / "stack-brief.md", skill / "templates" / "decision-record.md",
                skill / "rules" / "compatibility.json", skill / "scripts" / "check_stack.py",
                skill / "scripts" / "run_guard.py", skill / "flows" / "assurance.md",
                skill / "scripts" / "assurance.py", skill / "rules" / "assurance.json",
                skill / "templates" / "assurance-table.md"] + [skill / "layers" / f"{name}.md" for name in layers]         + [skill / "assurance" / f"{name}.md" for name in DISCIPLINES]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing required file: {path}")
    errors += check_layers(skill, layers)
    errors += check_rules(skill)
    errors += check_plugin(root)
    errors += check_assurance(skill)
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
