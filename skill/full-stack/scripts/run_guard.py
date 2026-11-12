"""Mechanical checks for a full-stack run in a git repository.

start   record the starting state and this worker's write set; refuse a write
        set that overlaps uncommitted edits made outside the run or another
        open run's write set. --shared claims files several workers edit:
        overlap is allowed, but the hunks that were already uncommitted at
        start are protected line by line
exec    run a check command and record its exit code and output tail
check   list files the run changed; flag changes outside the write set and
        changes to edits that existed before the run
        Declare the run's assurance table with --assurance DESIGN.md, or say
        why it is a routine edit with --routine REASON (or later with declare;
        the hook blocks edits until one is declared)
declare set or change the run's assurance declaration
report  print changed files, violations, and executed checks as Markdown;
        --all lists every recorded run (handoff: which work was verified)
finish  same as close (it used to finish without any gates)
hook    opt-in host hook (Claude Code PreToolUse/Stop): reads the event JSON
        on stdin, blocks an edit outside the open run's write set, and blocks
        stopping while the run has violations, no recorded checks, or an
        assurance row without an executed check
close   check, report, and finish; refuses while scope, checks, or
        assurance have problems unless --accept-blockers

Run records live under the repository's common git directory, so worktrees
of one repository see each other's open runs. Standard library only.
Exit codes: 0 ok, 1 violations, 2 usage or environment error, 3 collision.
"""

import argparse
import difflib
import fnmatch
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assurance import DEFAULT_RULES, check_table, load_rules  # noqa: E402  (sibling script, stdlib only)

STALE_HOURS = 24


def git(*args, cwd=None):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def repo_root(cwd=None):
    try:
        return Path(git("rev-parse", "--show-toplevel", cwd=cwd).strip())
    except (SystemExit, FileNotFoundError, NotADirectoryError):
        print("run_guard: not inside a git repository; checks unavailable.", file=sys.stderr)
        sys.exit(2)


def head(root):
    result = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=root, capture_output=True, text=True)
    return result.stdout.strip() or None


def runs_dir(root):
    common = Path(git("rev-parse", "--git-common-dir", cwd=root).strip())
    if not common.is_absolute():
        common = root / common
    path = common / "full-stack-runs"
    path.mkdir(exist_ok=True)
    return path


def digest(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, IsADirectoryError):
        return None


def dirty_files(root):
    """Uncommitted paths (modified, staged, untracked, deleted), repo-relative."""
    out = git("status", "--porcelain=v1", "-z", "--untracked-files=all", cwd=root)
    entries = out.split("\0")
    paths, skip = [], False
    for entry in entries:
        if skip:
            skip = False
            continue
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            skip = True  # the next entry is the rename source
        paths.append(path)
    return sorted(set(paths))


def in_write_set(path, patterns):
    for pattern in patterns:
        pattern = pattern.replace("\\", "/")
        if pattern.endswith("/") and path.startswith(pattern):
            return True
        # A bare directory name ("tasks") claims everything under it.
        if not any(c in pattern for c in "*?[") and path.startswith(pattern.rstrip("/") + "/"):
            return True
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def sets_overlap(a, b):
    """Conservative: patterns overlap if either matches the other literally or shares a prefix."""
    for x in a:
        for y in b:
            if in_write_set(x.rstrip("/*"), [y]) or in_write_set(y.rstrip("/*"), [x]):
                return True
            px, py = x.split("*")[0], y.split("*")[0]
            if px.startswith(py) or py.startswith(px):
                return True
    return False


def file_lines(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except FileNotFoundError:
        return []


def committed_lines(root, rel):
    result = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    return result.stdout.splitlines(keepends=True) if result.returncode == 0 else []


def protected_lines(base, current):
    """Line indexes of `current` that differ from `base` (someone else's uncommitted hunks)."""
    protected = set()
    for tag, _i1, _i2, j1, j2 in difflib.SequenceMatcher(None, base, current, autojunk=False).get_opcodes():
        if tag != "equal":
            protected.update(range(j1, j2))
    return protected


def protected_blocks_intact(before, after, protected):
    """True when every run of protected lines appears unchanged, contiguous, and in order in `after`.
    difflib may align an insert next to a protected hunk as if it were inside it; comparing content
    avoids that false report (field report 3, D4). Whitespace-only blocks could match elsewhere, so
    they are left to the positional check."""
    blocks, run = [], []
    for i in sorted(protected):
        if run and i != run[-1] + 1:
            blocks.append(run)
            run = []
        run.append(i)
    if run:
        blocks.append(run)
    start = 0
    for block in blocks:
        lines = [before[i] for i in block if i < len(before)]
        if not any(line.strip() for line in lines):
            return False
        for pos in range(start, len(after) - len(lines) + 1):
            if after[pos:pos + len(lines)] == lines:
                start = pos + len(lines)
                break
        else:
            return False
    return True


def hunk_violations(before, after, protected):
    """Edits from `before` to `after` that change or split a protected line."""
    if protected and protected_blocks_intact(before, after, protected):
        return []
    hits = []
    for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        touched = set(range(i1, i2)) & protected
        splits = tag == "insert" and (i1 - 1) in protected and i1 in protected
        if touched or splits:
            first = min(touched) if touched else i1
            hits.append(first + 1)
    return hits


def pointer(runs, root):
    """Per-worktree pointer to this worktree's latest run. The runs directory is shared by every
    worktree of a repository; one shared pointer let a worktree's edits be checked against another
    worktree's write set (FS-023 defect D1)."""
    key = hashlib.sha256(str(Path(root).resolve()).lower().encode("utf-8")).hexdigest()[:12]
    return runs / f"latest-{key}"


def load(runs, run_id, root=None):
    if run_id is None:
        latest = pointer(runs, root or repo_root())
        if not latest.exists():
            raise SystemExit("run_guard: no run started in this worktree; use start first.")
        run_id = latest.read_text(encoding="utf-8").strip()
    path = runs / f"{run_id}.json"
    if not path.exists():
        raise SystemExit(f"run_guard: unknown run {run_id}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path, record):
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


ASSURANCE_ID = re.compile(r"(?<![\w-])A-\d+(?!\w)")


def assurance_declaration(root, args):
    """None (undeclared), {"routine": reason}, or {"file": path} for the design holding the table."""
    if getattr(args, "routine", None) is not None:
        reason = args.routine.strip()
        if not reason:
            raise SystemExit("run_guard: --routine needs a one-line reason the report can show.")
        return {"routine": reason}
    if getattr(args, "assurance", None):
        path = Path(args.assurance)
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.exists():
            raise SystemExit(f"run_guard: assurance file not found: {args.assurance}")
        try:
            return {"file": path.resolve().relative_to(root.resolve()).as_posix()}
        except ValueError:
            return {"file": str(path.resolve())}
    return None


def is_routine(declared):
    return declared == "routine" or (isinstance(declared, dict) and "routine" in declared)


def assurance_ids(criterion):
    """Assurance row IDs a criterion names, in order ("A-1 ..." evidences row A-1)."""
    seen = []
    for found in ASSURANCE_ID.findall(criterion or ""):
        if found not in seen:
            seen.append(found)
    return seen


def latest_for(record, row_id):
    """The most recent executed check that names the row, or None. Only the latest counts, so an
    earlier pass cannot cover a later failure (external review 3, finding 4)."""
    latest = None
    for c in record["checks"]:
        ids = c.get("assurance_ids")
        if ids is None:
            ids = assurance_ids(c.get("criterion"))
        if row_id in ids:
            latest = c
    return latest


def history(results):
    """Compress a sequence of exits into 'fail → pass', 'pass only', and so on."""
    states = []
    for code in results:
        state = "pass" if code == 0 else "fail"
        if not states or states[-1] != state:
            states.append(state)
    return "pass only" if states == ["pass"] else " → ".join(states)


def read_table(root, declared):
    """(tiers, rows, structural errors) for the declared design, or an error string."""
    path = Path(declared["file"])
    if not path.is_absolute():
        path = root / path
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return f"assurance file unreadable: {declared['file']}"
    disciplines = set(load_rules(DEFAULT_RULES)["disciplines"])
    tiers, rows, errors, _pending = check_table(text, disciplines)
    if not rows:
        errors = errors + [f"no assurance rows (| A-1 | ... |) in {declared['file']}"]
    return tiers, rows, errors


def assurance_gaps(root, record):
    """Why the run's assurance does not yet support closing it. Field report 3 (G1) and external
    review 3: undeclared, declared after the code, structurally incomplete, or a row whose latest
    executed check is missing or failing. Tier 2 needs a passing executed check whatever the label."""
    declared = record.get("assurance")
    gaps = []
    late = record.get("declared_after_changes") or []
    if late:
        gaps.append("assurance declared after changes to " + ", ".join(late)
                    + " (screen and declare before editing)")
    if is_routine(declared):
        return gaps
    if not declared:
        return gaps + ["no assurance declared: run_guard.py declare --assurance DESIGN.md "
                       "(the file with the assurance table), or --routine \"<why this is routine>\""]
    table = read_table(root, declared)
    if isinstance(table, str):
        return gaps + [table]
    tiers, rows, errors = table
    gaps += [f"assurance table: {e}" for e in errors]
    for row in rows:
        tier = tiers.get(row["discipline"], 0)
        label = f"{row['id']} ({row['discipline']}, tier 2)" if tier == 2 else f"{row['id']} ({row['discipline']})"
        latest = latest_for(record, row["id"])
        if latest is None:
            if row["evidence"] == "documented" and tier < 2:
                continue
            gaps.append(f"assurance {label} has no executed check; name the ID in a criterion, "
                        f"e.g. --each \"{row['id']} <claim> :: <command>\"")
        elif latest["exit"] != 0:
            gaps.append(f"assurance {label}: latest check failed (exit {latest['exit']})")
    return gaps


def describe_assurance(record):
    declared = record.get("assurance")
    if declared == "routine":
        return "routine edit (no reason recorded)"
    if is_routine(declared):
        text = f"routine edit: {declared['routine']}"
        if declared.get("downgraded_from"):
            text += f" (downgraded from `{declared['downgraded_from']}` with --override)"
        return text
    if not declared:
        return "not declared"
    return f"table in `{declared['file']}`"


def cmd_declare(args):
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    new = assurance_declaration(root, args)
    if new is None:
        print("run_guard: give --assurance DESIGN.md or --routine \"<reason>\".", file=sys.stderr)
        return 2
    old = record.get("assurance")
    if is_routine(new) and isinstance(old, dict) and old.get("file"):
        if not args.override:
            print(f"run_guard: this run declared the assurance table in {old['file']}; replacing it with "
                  "--routine needs --override, and the report will show the downgrade.", file=sys.stderr)
            return 2
        new["downgraded_from"] = old["file"]
    if not old:
        changed = changes(root, record)[0]
        if changed:
            record["declared_after_changes"] = changed
    record["assurance"] = new
    save(path, record)
    print(f"run {record['id']} assurance: {describe_assurance(record)}")
    if record.get("declared_after_changes"):
        print("note: declared after files changed; close will report it as a blocker.")
    return 0


def cmd_start(args):
    root = repo_root()
    runs = runs_dir(root)
    shared = [p.replace("\\", "/") for p in args.shared]
    write_set = [p.replace("\\", "/") for p in args.write_set] + shared
    if not write_set:
        print("run_guard: declare the write set (--write-set or --shared PATTERN ...).", file=sys.stderr)
        return 2
    declared = assurance_declaration(root, args)
    dirty = dirty_files(root)
    adopted = {p.replace("\\", "/") for p in args.adopt}
    outside_edits = [p for p in dirty if in_write_set(p, write_set) and p not in adopted
                     and not in_write_set(p, shared)]
    others = []
    now = time.time()
    for other in runs.glob("*.json"):
        record = json.loads(other.read_text(encoding="utf-8"))
        if record.get("finished") or now - record["started"] > STALE_HOURS * 3600:
            continue
        theirs_shared = record.get("shared", [])
        mine_exclusive = [p for p in write_set if p not in shared]
        theirs_exclusive = [p for p in record["write_set"] if p not in theirs_shared]
        if sets_overlap(mine_exclusive, record["write_set"]) or sets_overlap(write_set, theirs_exclusive):
            others.append(f"{record['id']} ({record.get('label') or 'unlabeled'}): {', '.join(record['write_set'])}")
    if outside_edits or others:
        for p in outside_edits:
            print(f"collision: uncommitted edit made outside this run: {p}")
        for o in others:
            print(f"collision: open run with overlapping write set: {o}")
        print("Edit around these, sequence after the other run, or ask; nothing was recorded.")
        if outside_edits:
            print("If the user confirms these edits belong to this work, rerun with: --adopt "
                  + " ".join(shlex.quote(p) for p in outside_edits))
        return 3
    run_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    snapshots = {}
    for rel in dirty:
        if in_write_set(rel, shared) and rel not in adopted:
            current = file_lines(root / rel)
            snapshots[rel] = {"lines": current,
                              "protected": sorted(protected_lines(committed_lines(root, rel), current))}
    record = {
        "id": run_id,
        "label": args.label,
        "worktree": str(root.resolve()),
        "started": now,
        "head": head(root),
        "write_set": write_set,
        "shared": shared,
        "shared_snapshots": snapshots,
        "dirty_at_start": {p: digest(root / p) for p in dirty if p not in adopted},
        "adopted": sorted(adopted),
        "assurance": declared,
        "checks": [],
        "finished": False,
    }
    save(runs / f"{run_id}.json", record)
    pointer(runs, root).write_text(run_id, encoding="utf-8")
    print(f"run {run_id} started; write set: {', '.join(write_set)}; {len(dirty)} pre-existing uncommitted paths recorded")
    if declared is None:
        print("note: no assurance declared. Beyond a routine edit, screen first (flows/assurance.md), then "
              "run_guard.py declare --assurance DESIGN.md; for a routine edit, declare --routine. "
              "close refuses until one is declared.")
    return 0


def changes(root, record):
    changed, touched = set(), []
    for p in dirty_files(root):
        if p not in record["dirty_at_start"]:
            changed.add(p)
    snapshots = record.get("shared_snapshots", {})
    for p, before in record["dirty_at_start"].items():
        if digest(root / p) == before:
            continue
        if p in snapshots:
            changed.add(p)
            snap = snapshots[p]
            for line in hunk_violations(snap["lines"], file_lines(root / p), set(snap["protected"])):
                touched.append(f"{p} (line {line} of the start state)")
        else:
            touched.append(p)
    if record["head"]:
        for p in git("diff", "--name-only", record["head"], "HEAD", cwd=root).splitlines():
            if p and p not in record["dirty_at_start"]:
                changed.add(p)
    outside = sorted(p for p in changed if not in_write_set(p, record["write_set"]))
    return sorted(changed), sorted(touched), outside


def run_check(root, record, command, criterion, tail_lines):
    began = time.time()
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, errors="replace")
        code, output = result.returncode, (result.stdout + result.stderr)
    except FileNotFoundError as exc:
        code, output = 127, str(exc)
    tail = output.strip().splitlines()[-tail_lines:]
    record["checks"].append({
        "command": shlex.join(command),
        "criterion": criterion,
        "assurance_ids": assurance_ids(criterion),
        "exit": code,
        "seconds": round(time.time() - began, 2),
        "tail": tail,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    return code, tail


def cmd_exec(args):
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        print("run_guard: give the check command after --.", file=sys.stderr)
        return 2
    code, tail = run_check(root, record, command, args.criterion, args.tail)
    save(path, record)
    print("\n".join(tail))
    print(f"[run_guard] exit {code}: {shlex.join(command)}")
    return code


def parse_plan(args):
    """Checks from --each "criterion :: command" and/or a JSON --plan [{criterion, command}]."""
    plan = []
    for item in args.each:
        criterion, sep, command = item.partition("::")
        if not sep or not command.strip():
            raise ValueError(f"--each needs 'criterion :: command': {item!r}")
        plan.append((criterion.strip(), shlex.split(command.strip(), posix=True)))
    if args.plan:
        entries = json.loads(Path(args.plan).read_text(encoding="utf-8-sig"))
        for entry in entries:
            command = entry["command"]
            plan.append((entry.get("criterion"), shlex.split(command) if isinstance(command, str) else list(command)))
    if not plan:
        raise ValueError("give at least one --each or a --plan file")
    return plan


def cmd_checks(args):
    """Run every acceptance check in one call; each is recorded like exec."""
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    try:
        plan = parse_plan(args)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"run_guard: {exc}", file=sys.stderr)
        return 2
    failed = 0
    for criterion, command in plan:
        code, tail = run_check(root, record, command, criterion, args.tail)
        save(path, record)
        status = "PASS" if code == 0 else f"FAIL (exit {code})"
        print(f"[run_guard] {status}: {criterion or ''} :: {shlex.join(command)}")
        if code:
            failed += 1
            print("\n".join("    " + line for line in tail))
    print(f"[run_guard] {len(plan) - failed}/{len(plan)} checks passed")
    return 1 if failed else 0


def cmd_close(args):
    """check + report + finish in one call. Refuses to finish a run with problems unless told to."""
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    problems = cmd_report(args)
    if not record["checks"]:
        print("\nNo checks were recorded.")
        problems = 1
    # The latest result per criterion counts, so a corrected rerun replaces an earlier failure.
    # Before this, close finished runs whose checks had failed (FS-023 defect D3).
    latest = {}
    for c in record["checks"]:
        latest[c["criterion"] or c["command"]] = c
    failed = [name for name, c in latest.items() if c["exit"] != 0]
    if failed:
        print("\nFailing checks: " + "; ".join(failed))
        problems = 1
    gaps = assurance_gaps(root, record)
    if gaps:
        print("\nAssurance gaps: " + "; ".join(gaps))
        problems = 1
    if problems and not args.accept_blockers:
        print("\n[run_guard] run left open: fix the problems above, or report them as blockers "
              "and rerun close with --accept-blockers.")
        return 1
    record["finished"] = True
    save(path, record)
    print(f"\n[run_guard] run {record['id']} finished" + (" with reported blockers" if problems else ""))
    return 1 if problems else 0


def cmd_check(args):
    root = repo_root()
    _, record = load(runs_dir(root), args.run)
    changed, touched, outside = changes(root, record)
    for p in changed:
        print(f"changed: {p}")
    for p in outside:
        print(f"violation: outside the write set: {p}")
    for p in touched:
        print(f"violation: changed an edit that existed before the run: {p}")
    print(f"{len(changed)} changed, {len(outside) + len(touched)} violations")
    return 1 if outside or touched else 0


def run_summary(record):
    latest = {}
    for c in record.get("checks", []):
        latest[c.get("criterion") or c["command"]] = c
    passed = sum(1 for c in latest.values() if c["exit"] == 0)
    last = record["checks"][-1] if record.get("checks") else None
    if record.get("finished"):
        state = "closed"
    elif time.time() - record["started"] > STALE_HOURS * 3600:
        state = "stale"
    else:
        state = "open"
    return {
        "id": record["id"], "label": record.get("label") or "", "state": state,
        "started": time.strftime("%Y-%m-%d %H:%M", time.localtime(record["started"])),
        "write_set": len(record.get("write_set", [])), "passing": passed, "failing": len(latest) - passed,
        "last": f"{last.get('criterion') or last['command']} (exit {last['exit']})" if last else "none",
    }


def cmd_report_all(args):
    """One row per recorded run, newest first: lets a new session tell verified work from
    unverified work without trusting memory (field report 3; FS-028)."""
    runs = runs_dir(repo_root())
    records = []
    for path in runs.glob("*.json"):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    records.sort(key=lambda r: r.get("started", 0), reverse=True)
    if args.limit:
        records = records[:args.limit]
    rows = [run_summary(r) for r in records]
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    print("| Run | Label | Started | State | Write-set entries | Criteria passing / failing | Last check |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['id']} | {r['label']} | {r['started']} | {r['state']} | {r['write_set']} | "
              f"{r['passing']} / {r['failing']} | {r['last']} |")
    if not rows:
        print("| none recorded | | | | | | |")
    return 0


def cmd_report(args):
    if getattr(args, "all", False):
        return cmd_report_all(args)
    root = repo_root()
    _, record = load(runs_dir(root), args.run)
    changed, touched, outside = changes(root, record)
    print(f"### Run {record['id']}\n")
    print(f"Write set: {', '.join(f'`{p}`' for p in record['write_set'])}\n")
    print("Changed files: " + (", ".join(f"`{p}`" for p in changed) or "none"))
    problems = [f"outside the write set: `{p}`" for p in outside] + [f"changed a pre-existing edit: `{p}`" for p in touched]
    print("\nScope violations: " + ("; ".join(problems) or "none"))
    print(f"\nAssurance: {describe_assurance(record)}")
    print("\n| Check | Criterion | Exit | Seconds |\n|---|---|---|---|")
    for c in record["checks"]:
        print(f"| `{c['command']}` | {c['criterion'] or ''} | {c['exit']} | {c['seconds']} |")
    if not record["checks"]:
        print("| none executed | | | |")
    exits = {}
    for c in record["checks"]:
        exits.setdefault(c["criterion"] or c["command"], []).append(c["exit"])
    if exits:
        # A criterion seen failing before it passed shows the check can detect its failure.
        print("\n| Criterion | Latest | History |\n|---|---|---|")
        for name, codes in exits.items():
            print(f"| {name} | {'pass' if codes[-1] == 0 else 'fail'} | {history(codes)} |")
    declared = record.get("assurance")
    if isinstance(declared, dict) and declared.get("file"):
        table = read_table(root, declared)
        if not isinstance(table, str):
            tiers, rows, _errors = table
            print("\n| Assurance row | Tier | Declared evidence | Executed (latest) | History |\n|---|---|---|---|---|")
            for row in rows:
                runs = [c["exit"] for c in record["checks"]
                        if row["id"] in (c.get("assurance_ids") or assurance_ids(c.get("criterion")))]
                latest = "none" if not runs else ("pass" if runs[-1] == 0 else f"fail (exit {runs[-1]})")
                print(f"| {row['id']} | {tiers.get(row['discipline'], 0)} | {row['evidence'] or 'none'} | "
                      f"{latest} | {history(runs) if runs else ''} |")
    return 1 if problems else 0


def cmd_finish(args):
    """Same gates as close (external review 3, finding 6): finishing never skips scope, checks, or assurance."""
    return cmd_close(args)


def open_run(root):
    runs = runs_dir(root)
    latest = pointer(runs, root)
    if not latest.exists():
        return None
    path = runs / f"{latest.read_text(encoding='utf-8').strip()}.json"
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("finished") or time.time() - record["started"] > STALE_HOURS * 3600:
        return None
    return record


def cmd_hook(args):
    """Exit 2 tells the host to block the action and show stderr to the model."""
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    cwd = event.get("cwd") or os.getcwd()
    probe = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True)
    if probe.returncode:
        return 0
    root = Path(probe.stdout.strip())
    record = open_run(root)
    name = event.get("hook_event_name", "")
    if name == "PreToolUse":
        target = (event.get("tool_input") or {}).get("file_path") or (event.get("tool_input") or {}).get("notebook_path")
        if not target:
            return 0
        target = Path(target)
        if not target.is_absolute():
            target = Path(cwd) / target
        try:
            rel = target.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return 0
        if record is None:
            if args.require_run:
                print("run_guard: no guarded run is open. Start one before editing: "
                      "run_guard.py start --write-set <paths> --label <work ID>", file=sys.stderr)
                return 2
            return 0
        if not in_write_set(rel, record["write_set"]):
            print(f"run_guard: {rel} is outside this run's write set ({', '.join(record['write_set'])}). "
                  "Narrow the change, or finish this run and start one that claims it.", file=sys.stderr)
            return 2
        if not record.get("assurance"):
            print("run_guard: declare this run's assurance before editing (external review 3): screen first "
                  "(flows/assurance.md), then run_guard.py declare --assurance DESIGN.md, or "
                  "declare --routine \"<why this is routine>\".", file=sys.stderr)
            return 2
        return 0
    if name == "Stop":
        if record is None or event.get("stop_hook_active"):
            return 0
        _changed, touched, outside = changes(root, record)
        problems = [f"outside the write set: {p}" for p in outside] + [f"changed an outside edit: {p}" for p in touched]
        if not record["checks"]:
            problems.append("no checks were run through run_guard.py checks or exec")
        problems += assurance_gaps(root, record)
        if problems:
            print("run_guard: the open run is not ready to close: " + "; ".join(problems)
                  + ". Fix these, or report them as blockers and run run_guard.py close --accept-blockers.", file=sys.stderr)
            return 2
    return 0


def add_assurance_flags(p):
    group = p.add_mutually_exclusive_group()
    group.add_argument("--assurance", metavar="DESIGN.md",
                       help="file with the assurance table; each row ID must appear in an executed check's criterion")
    group.add_argument("--routine", metavar="REASON",
                       help="a routine edit with no assurance table; the reason is shown in the report")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run_guard", description="Mechanical checks for a full-stack run.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--write-set", nargs="+", action="extend", default=[], metavar="PATTERN",
                   help="repo-relative globs or directory prefixes ending in /")
    p.add_argument("--label", help="work package ID or short name")
    p.add_argument("--shared", nargs="+", action="extend", default=[], metavar="PATTERN",
                   help="files other workers may also edit; their uncommitted hunks are protected")
    p.add_argument("--adopt", nargs="+", action="extend", default=[], metavar="PATH",
                   help="uncommitted paths the user confirmed belong to this work")
    add_assurance_flags(p)
    p = sub.add_parser("declare", help="set the run's assurance declaration")
    p.add_argument("--run")
    p.add_argument("--override", action="store_true",
                   help="allow replacing an assurance table with --routine; the report shows the downgrade")
    add_assurance_flags(p)
    p = sub.add_parser("exec")
    p.add_argument("--run")
    p.add_argument("--criterion", help="acceptance criterion this check evidences")
    p.add_argument("--tail", type=int, default=20)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p = sub.add_parser("checks", help="run several acceptance checks in one call")
    p.add_argument("--run")
    p.add_argument("--each", action="append", default=[], metavar="'CRITERION :: COMMAND'",
                   help="COMMAND is split like a POSIX shell and run without a shell: quotes group "
                        "words and are removed. Put pipes, redirects, or commands that need their "
                        "own quoting (powershell -Command, sh -c) in a script file, or use --plan")
    p.add_argument("--plan", help="JSON list of {criterion, command}; an argv array is passed unchanged")
    p.add_argument("--tail", type=int, default=20)
    sub.add_parser("check").add_argument("--run")
    p = sub.add_parser("report", help="report this run, or --all runs")
    p.add_argument("--run")
    p.add_argument("--all", action="store_true", help="one row per recorded run, newest first")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("finish", help="same as close")
    p.add_argument("--run")
    p.add_argument("--accept-blockers", action="store_true")
    p = sub.add_parser("close", help="check, report, and finish in one call")
    p.add_argument("--run")
    p.add_argument("--accept-blockers", action="store_true",
                   help="finish even with violations or no checks; they must be reported as blockers")
    p = sub.add_parser("hook")
    p.add_argument("--require-run", action="store_true",
                   help="block edits in a git repository when no guarded run is open")
    args = parser.parse_args(argv)
    return {"start": cmd_start, "declare": cmd_declare, "exec": cmd_exec, "checks": cmd_checks, "check": cmd_check,
            "report": cmd_report, "finish": cmd_finish, "close": cmd_close, "hook": cmd_hook}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
