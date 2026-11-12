#!/usr/bin/env python3
"""Check a Full Stack layer profile for mechanical consistency.

Usage:
  check_stack.py check FILE [--rules PATH] [--json]
  check_stack.py profiles FILE [--rules PATH] [--limit N] [--json]

FILE is a .json stack file, or a Markdown file containing one ```json stack
fenced block. `check` validates the committed choices (pass 2). `profiles`
enumerates combinations of each layer's candidates (pass 1) and lists those
that satisfy every rule, neighbor assumption, and the innovation budget.

It checks structure only: tags, rules, assumptions, and budget. It cannot
judge whether a choice is good.

Exit codes: 0 consistent (check) or at least one surviving profile
(profiles); 1 violations, or no surviving profile; 2 unreadable input.
Standard library only.
"""

import argparse
import itertools
import json
import re
import sys
from collections import Counter
from pathlib import Path

STATUSES = {"keep-current", "proposed", "accepted", "conditional", "blocked", "out-of-scope"}
SOFT = {"conditional", "blocked"}  # unmet assumptions are reported, not fatal
DEFAULT_RULES = Path(__file__).resolve().parent.parent / "rules" / "compatibility.json"
MAX_COMBINATIONS = 20000


class InputError(Exception):
    pass


def load_stack(path):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}")
    if path.suffix.lower() in (".md", ".markdown"):
        blocks = re.findall(r"^```json stack[ \t]*\r?\n(.*?)^```", text, flags=re.S | re.M)
        if len(blocks) != 1:
            raise InputError(f"{path}: expected exactly one ```json stack block, found {len(blocks)}")
        text = blocks[0]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path}: invalid JSON: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("layers"), dict) or not data["layers"]:
        raise InputError(f"{path}: needs a non-empty 'layers' object")
    for name, layer in data["layers"].items():
        if not isinstance(layer, dict):
            raise InputError(f"layer {name}: must be an object")
        status = layer.get("status")
        if status not in STATUSES:
            raise InputError(f"layer {name}: status {status!r} not in {sorted(STATUSES)}")
        for i, cand in enumerate(layer.get("candidates", [])):
            if not isinstance(cand, dict) or not cand.get("name"):
                raise InputError(f"layer {name}: candidate {i} needs a name")
    return data


def load_rules(path, stack):
    try:
        base = json.loads(Path(path).read_text(encoding="utf-8-sig")).get("rules", [])
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"rules {path}: {exc}")
    rules = list(base) + list(stack.get("rules", []))
    ids = [r.get("id") for r in rules]
    duplicates = sorted(i for i, n in Counter(ids).items() if n > 1)
    if duplicates:
        raise InputError(f"duplicate rule ids: {duplicates}")
    for rule in rules:
        if not rule.get("id") or not isinstance(rule.get("when", {}), dict):
            raise InputError(f"malformed rule: {rule}")
        if not rule.get("requires") and not rule.get("excludes"):
            raise InputError(f"rule {rule['id']}: needs 'requires' or 'excludes'")
    return rules


def tags_of(choice):
    return set(choice.get("provides", []))


def violations(profile, brief, rules, budget):
    """Return (errors, soft) for one concrete profile: {layer: {status, provides, assumes, novel}}."""
    errors, soft = [], []
    provided = {name: tags_of(c) for name, c in profile.items()}
    provided["brief"] = set(brief.get("tags", []))

    for name, choice in profile.items():
        for neighbor, needed in choice.get("assumes", {}).items():
            if neighbor not in profile:
                msg = f"{name} assumes from undeclared layer '{neighbor}': {sorted(needed)}"
            else:
                missing = set(needed) - provided[neighbor]
                if not missing:
                    continue
                msg = f"{name} assumes {sorted(missing)} from {neighbor}, which does not provide them"
            (soft if choice.get("status") in SOFT else errors).append(("assumption", msg))

    for rule in rules:
        when = rule.get("when", {})
        if not all(layer in provided and set(tags) <= provided[layer] for layer, tags in when.items()):
            continue
        for layer, tags in rule.get("requires", {}).items():
            missing = set(tags) - provided.get(layer, set())
            if missing:
                where = "" if layer in provided else " (layer not declared)"
                errors.append(("rule", f"{rule['id']}: {layer} must provide {sorted(missing)}{where} — {rule.get('why', '')}".rstrip(" —")))
        for layer, tags in rule.get("excludes", {}).items():
            present = set(tags) & provided.get(layer, set())
            if present:
                errors.append(("rule", f"{rule['id']}: {layer} must not provide {sorted(present)} — {rule.get('why', '')}".rstrip(" —")))

    novel = sorted(name for name, c in profile.items() if c.get("novel"))
    if len(novel) > budget:
        errors.append(("budget", f"{len(novel)} novel choices {novel} exceed innovation budget {budget}"))
    return errors, soft


def committed_profile(stack):
    return {
        name: {"status": layer["status"], "provides": layer.get("provides", []),
               "assumes": layer.get("assumes", {}), "novel": bool(layer.get("novel"))}
        for name, layer in stack["layers"].items() if layer["status"] != "out-of-scope"
    }


def cmd_check(stack, rules):
    brief = stack.get("brief", {})
    budget = int(brief.get("innovation_budget", 1))
    errors, soft = violations(committed_profile(stack), brief, rules, budget)
    warnings = [msg for _, msg in soft]

    for name in brief.get("affected", []):
        if name not in stack["layers"]:
            errors.append(("coverage", f"affected layer '{name}' has no decision"))
    for name, layer in stack["layers"].items():
        status = layer["status"]
        if status in ("proposed", "accepted"):
            if not layer.get("choice"):
                errors.append(("record", f"{name}: {status} without a choice"))
            names = [c["name"] for c in layer.get("candidates", [])]
            if len(names) < 2:
                warnings.append(f"{name}: fewer than two candidates recorded")
            elif layer.get("choice") not in names:
                warnings.append(f"{name}: choice is not one of the recorded candidates")
        if status in SOFT:
            warnings.append(f"{name}: {status}; dependent work is not ready")
    return {"errors": [m for _, m in errors], "warnings": warnings}


def cmd_profiles(stack, rules, limit):
    brief = stack.get("brief", {})
    budget = int(brief.get("innovation_budget", 1))
    names, options = [], []
    for name, layer in stack["layers"].items():
        if layer["status"] == "out-of-scope":
            continue
        cands = layer.get("candidates") if layer["status"] != "keep-current" else None
        if not cands:
            cands = [{"name": layer.get("choice") or "(current)", "provides": layer.get("provides", []),
                      "assumes": layer.get("assumes", {}), "novel": layer.get("novel", False)}]
        names.append(name)
        options.append([dict(c, status=layer["status"]) for c in cands])
    total = 1
    for opts in options:
        total *= len(opts)
    if total > MAX_COMBINATIONS:
        raise InputError(f"{total} combinations exceed {MAX_COMBINATIONS}; narrow the candidate sets")

    survivors, eliminated = [], Counter()
    for combo in itertools.product(*options):
        profile = dict(zip(names, combo))
        errors, soft = violations(profile, brief, rules, budget)
        if errors:
            for _, msg in errors:
                eliminated[msg] += 1
            continue
        survivors.append({
            "profile": {n: c["name"] for n, c in profile.items()},
            "novel": sum(1 for c in profile.values() if c.get("novel")),
            "open_assumptions": [m for _, m in soft],
        })
    survivors.sort(key=lambda s: (s["novel"], len(s["open_assumptions"])))
    return {"combinations": total, "surviving": len(survivors), "profiles": survivors[:limit],
            "eliminated_by": [{"reason": r, "combinations": n} for r, n in eliminated.most_common()]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "profiles"):
        p = sub.add_parser(command)
        p.add_argument("file")
        p.add_argument("--rules", default=str(DEFAULT_RULES))
        p.add_argument("--json", action="store_true")
        if command == "profiles":
            p.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)

    try:
        stack = load_stack(args.file)
        rules = load_rules(args.rules, stack)
        result = cmd_check(stack, rules) if args.command == "check" else cmd_profiles(stack, rules, args.limit)
    except InputError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "check":
        for msg in result["errors"]:
            print(f"ERROR   {msg}")
        for msg in result["warnings"]:
            print(f"warning {msg}")
        print(f"{len(result['errors'])} errors, {len(result['warnings'])} warnings; {len(rules)} rules checked.")
    else:
        print(f"{result['surviving']} of {result['combinations']} combinations survive ({len(rules)} rules).")
        for i, s in enumerate(result["profiles"], 1):
            line = ", ".join(f"{k}={v}" for k, v in s["profile"].items())
            print(f"  {i}. [{s['novel']} novel] {line}")
            for msg in s["open_assumptions"]:
                print(f"       open: {msg}")
        if result["eliminated_by"]:
            print("Eliminated by:")
            for e in result["eliminated_by"]:
                print(f"  {e['combinations']:>5}  {e['reason']}")

    if args.command == "check":
        return 1 if result["errors"] else 0
    return 0 if result["surviving"] else 1


if __name__ == "__main__":
    sys.exit(main())
