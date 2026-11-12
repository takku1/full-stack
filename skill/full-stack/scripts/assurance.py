#!/usr/bin/env python3
"""Resolve the assurance screen and check an assurance table.

Usage:
  assurance.py screen --yes ID... --no ID... [--unknown ID...] [--high DISCIPLINE...|all]
                      [--build] [--rules PATH] [--json]
  assurance.py check FILE [--json]

`screen` turns the screen answers (rules/assurance.json "questions") into
the disciplines to load and their tiers. Every question must be answered;
unknown counts as yes. Answers are facts and the rules are Horn clauses
(question -> discipline, discipline -> required discipline, raised and high
-> tier 2), resolved by forward closure, so the result does not depend on
the model applying the table by hand. It prints a "Screen:" line to paste
above the assurance table.

`check` reads a Markdown file with that Screen line and the assurance
table, and reports structural gaps: a raised discipline with no row, a row
with no check, a duplicate ID, a row for an unknown discipline. Tier 2 rows
not yet "tested" are listed as pending.

Exit codes: 0 ok, 1 table gaps, 2 usage or unreadable input. Standard
library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "rules" / "assurance.json"
NO_CHECK = {"", "-", "—", "none", "n/a", "tbd", "todo"}
ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|(.*)\|\s*$")
SCREEN_ITEM = re.compile(r"\b([a-z]+) T([0-2])\b")


def load_rules(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"assurance: cannot read rules {path}: {exc}")


def horn_rules(rules, build):
    """(body, head) clauses over string facts."""
    clauses = []
    for qid, q in rules["questions"].items():
        for d in q["raises"]:
            clauses.append(((f"q:{qid}",), f"t1:{d}"))
    if build:
        for d in rules.get("always_on_build", []):
            clauses.append((("build",), f"t1:{d}"))
    for d, deps in rules.get("requires", {}).items():
        for dep in deps:
            clauses.append(((f"t1:{d}",), f"t1:{dep}"))
    for d in rules["disciplines"]:
        clauses.append(((f"t1:{d}", f"high:{d}"), f"t2:{d}"))
    return clauses


def closure(facts, clauses):
    """Forward closure to a fixpoint. Returns the derived facts and, for each, every clause
    body that supports it, so a discipline lists all the answers that raise it."""
    known = set(facts)
    changed = True
    while changed:
        changed = False
        for body, head in clauses:
            if head not in known and all(b in known for b in body):
                known.add(head)
                changed = True
    support = {}
    for body, head in clauses:
        if head in known and all(b in known for b in body):
            support.setdefault(head, []).append(body)
    return known, support


def reasons(fact, support):
    """Question IDs (and 'build') that a derived fact rests on."""
    out, stack, seen = set(), [fact], set()
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        if f.startswith("q:"):
            out.add(f[2:])
        elif f == "build":
            out.add("build")
        for body in support.get(f, []):
            stack.extend(body)
    return sorted(out)


def resolve(rules, yes, no, unknown, high, build):
    questions = set(rules["questions"])
    disciplines = set(rules["disciplines"])
    given = list(yes) + list(no) + list(unknown)
    errors = [f"unknown question: {q}" for q in given if q not in questions]
    errors += [f"answered twice: {q}" for q in sorted({q for q in given if given.count(q) > 1})]
    missing = sorted(questions - set(given))
    if missing:
        errors.append("unanswered (answer each; unknown counts as yes): " + ", ".join(missing))
    high = set(disciplines) if "all" in high else set(high)
    errors += [f"unknown discipline: {d}" for d in sorted(high - disciplines)]
    if errors:
        return None, errors
    facts = {f"q:{q}" for q in list(yes) + list(unknown)} | {f"high:{d}" for d in high}
    if build:
        facts.add("build")
    known, support = closure(facts, horn_rules(rules, build))
    result = []
    for d in rules["disciplines"]:
        tier = 2 if f"t2:{d}" in known else 1 if f"t1:{d}" in known else 0
        result.append({"discipline": d, "tier": tier, "because": reasons(f"t1:{d}", support) if tier else []})
    return result, []


def screen_line(result, unknown):
    raised = [r for r in result if r["tier"]]
    parts = [f"{r['discipline']} T{r['tier']} ({', '.join(r['because'])})" for r in raised]
    line = "Screen: " + ("; ".join(parts) if parts else "nothing raised") + "; others T0"
    if unknown:
        line += f" [unknown, treated as yes: {', '.join(sorted(unknown))}]"
    return line


def cmd_screen(args):
    rules = load_rules(args.rules)
    result, errors = resolve(rules, args.yes, args.no, args.unknown, args.high, args.build)
    if errors or result is None:
        for e in errors:
            print(f"assurance: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"disciplines": result, "unknown": sorted(args.unknown)}, indent=2))
    else:
        print(screen_line(result, args.unknown))
        loads = [f"assurance/{r['discipline']}.md" for r in result if r["tier"]]
        print("Load: " + (", ".join(loads) or "none"))
    return 0


def parse_table(text):
    """Screen tiers and assurance rows (id, discipline, check, evidence) from Markdown."""
    tiers = {}
    for line in text.splitlines():
        if line.strip().startswith("Screen:"):
            tiers = {d: int(t) for d, t in SCREEN_ITEM.findall(line)}
            break
    rows = []
    for line in text.splitlines():
        m = ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        cells += [""] * (6 - len(cells))
        rows.append({"id": m.group(1), "discipline": cells[0].lower(), "check": cells[4].strip("` "),
                     "evidence": cells[5].lower()})
    return tiers, rows


def check_table(text, disciplines):
    tiers, rows = parse_table(text)
    errors, pending = [], []
    if not tiers:
        errors.append("no 'Screen:' line with tiers (run assurance.py screen and paste its line)")
    seen = set()
    for r in rows:
        if r["id"] in seen:
            errors.append(f"{r['id']}: duplicate ID")
        seen.add(r["id"])
        if r["discipline"] not in disciplines:
            errors.append(f"{r['id']}: unknown discipline {r['discipline']!r}")
        elif tiers and not tiers.get(r["discipline"]):
            errors.append(f"{r['id']}: discipline {r['discipline']} is not raised by the screen")
        if r["check"].lower() in NO_CHECK:
            errors.append(f"{r['id']}: no check (a claim without a check is a blocker)")
        if tiers.get(r["discipline"]) == 2 and r["evidence"] != "tested":
            pending.append(f"{r['id']}: tier 2 claim not yet tested (evidence: {r['evidence'] or 'none'})")
    covered = {r["discipline"] for r in rows}
    for d, t in tiers.items():
        if t and d not in covered:
            errors.append(f"{d} is raised to T{t} but has no row")
    return rows, errors, pending


def cmd_check(args):
    rules = load_rules(args.rules)
    try:
        text = Path(args.file).read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"assurance: cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    rows, errors, pending = check_table(text, set(rules["disciplines"]))
    if args.json:
        print(json.dumps({"rows": rows, "errors": errors, "pending": pending}, indent=2))
    else:
        for e in errors:
            print(f"gap: {e}")
        for p in pending:
            print(f"pending: {p}")
        print(f"{len(rows)} rows, {len(errors)} gaps, {len(pending)} pending")
    return 1 if errors else 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="assurance", description="Resolve the assurance screen and check an assurance table.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("screen", help="resolve screen answers into disciplines and tiers")
    for flag in ("--yes", "--no", "--unknown"):
        p.add_argument(flag, nargs="+", action="extend", default=[], metavar="QUESTION")
    p.add_argument("--high", nargs="+", action="extend", default=[], metavar="DISCIPLINE",
                   help="raised disciplines whose failure has high consequence (tier 2), or 'all'")
    p.add_argument("--build", action="store_true", help="building was requested")
    p.add_argument("--rules", default=DEFAULT_RULES)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("check", help="check an assurance table for structural gaps")
    p.add_argument("file")
    p.add_argument("--rules", default=DEFAULT_RULES)
    p.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return {"screen": cmd_screen, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
