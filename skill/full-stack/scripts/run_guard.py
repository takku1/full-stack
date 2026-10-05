"""Mechanical checks for a full-stack run in a git repository.

start   record the starting state and this worker's write set; refuse a write
        set that overlaps uncommitted edits made outside the run or another
        open run's write set. --shared claims files several workers edit:
        overlap is allowed, but the hunks that were already uncommitted at
        start are protected line by line
exec    run a check command and record its exit code and output tail
check   list files the run changed; flag changes outside the write set and
        changes to edits that existed before the run
report  print changed files, violations, and executed checks as Markdown
finish  close the run so its write set no longer blocks other workers
hook    opt-in host hook (Claude Code PreToolUse/Stop): reads the event JSON
        on stdin, blocks an edit outside the open run's write set, and blocks
        stopping while the run has violations or no recorded checks

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
import subprocess
import sys
import time
import uuid
from pathlib import Path

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


def hunk_violations(before, after, protected):
    """Edits from `before` to `after` that change or split a protected line."""
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


def load(runs, run_id):
    if run_id is None:
        latest = runs / "latest"
        if not latest.exists():
            raise SystemExit("run_guard: no run started; use start first.")
        run_id = latest.read_text(encoding="utf-8").strip()
    path = runs / f"{run_id}.json"
    if not path.exists():
        raise SystemExit(f"run_guard: unknown run {run_id}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path, record):
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")


def cmd_start(args):
    root = repo_root()
    runs = runs_dir(root)
    shared = [p.replace("\\", "/") for p in args.shared]
    write_set = [p.replace("\\", "/") for p in args.write_set] + shared
    if not write_set:
        print("run_guard: declare the write set (--write-set or --shared PATTERN ...).", file=sys.stderr)
        return 2
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
        print("If the user confirms an edit belongs to this work, rerun with --adopt PATH.")
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
        "started": now,
        "head": head(root),
        "write_set": write_set,
        "shared": shared,
        "shared_snapshots": snapshots,
        "dirty_at_start": {p: digest(root / p) for p in dirty if p not in adopted},
        "adopted": sorted(adopted),
        "checks": [],
        "finished": False,
    }
    save(runs / f"{run_id}.json", record)
    (runs / "latest").write_text(run_id, encoding="utf-8")
    print(f"run {run_id} started; write set: {', '.join(write_set)}; {len(dirty)} pre-existing uncommitted paths recorded")
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


def cmd_exec(args):
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        print("run_guard: give the check command after --.", file=sys.stderr)
        return 2
    began = time.time()
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, errors="replace")
        code, output = result.returncode, (result.stdout + result.stderr)
    except FileNotFoundError as exc:
        code, output = 127, str(exc)
    tail = output.strip().splitlines()[-args.tail:]
    record["checks"].append({
        "command": " ".join(command),
        "criterion": args.criterion,
        "exit": code,
        "seconds": round(time.time() - began, 2),
        "tail": tail,
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    save(path, record)
    print("\n".join(tail))
    print(f"[run_guard] exit {code}: {' '.join(command)}")
    return code


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


def cmd_report(args):
    root = repo_root()
    _, record = load(runs_dir(root), args.run)
    changed, touched, outside = changes(root, record)
    print(f"### Run {record['id']}\n")
    print(f"Write set: {', '.join(f'`{p}`' for p in record['write_set'])}\n")
    print("Changed files: " + (", ".join(f"`{p}`" for p in changed) or "none"))
    problems = [f"outside the write set: `{p}`" for p in outside] + [f"changed a pre-existing edit: `{p}`" for p in touched]
    print("\nScope violations: " + ("; ".join(problems) or "none"))
    print("\n| Check | Criterion | Exit | Seconds |\n|---|---|---|---|")
    for c in record["checks"]:
        print(f"| `{c['command']}` | {c['criterion'] or ''} | {c['exit']} | {c['seconds']} |")
    if not record["checks"]:
        print("| none executed | | | |")
    return 1 if problems else 0


def cmd_finish(args):
    root = repo_root()
    path, record = load(runs_dir(root), args.run)
    record["finished"] = True
    save(path, record)
    print(f"run {record['id']} finished")
    return 0


def open_run(root):
    runs = runs_dir(root)
    latest = runs / "latest"
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
        return 0
    if name == "Stop":
        if record is None or event.get("stop_hook_active"):
            return 0
        _changed, touched, outside = changes(root, record)
        problems = [f"outside the write set: {p}" for p in outside] + [f"changed an outside edit: {p}" for p in touched]
        if not record["checks"]:
            problems.append("no checks were run through run_guard.py exec")
        if problems:
            print("run_guard: the open run is not ready to close: " + "; ".join(problems)
                  + ". Fix these, or report them as blockers and run run_guard.py finish.", file=sys.stderr)
            return 2
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="run_guard", description="Mechanical checks for a full-stack run.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--write-set", nargs="+", default=[], metavar="PATTERN",
                   help="repo-relative globs or directory prefixes ending in /")
    p.add_argument("--label", help="work package ID or short name")
    p.add_argument("--shared", nargs="+", default=[], metavar="PATTERN",
                   help="files other workers may also edit; their uncommitted hunks are protected")
    p.add_argument("--adopt", nargs="+", default=[], metavar="PATH",
                   help="uncommitted paths the user confirmed belong to this work")
    p = sub.add_parser("exec")
    p.add_argument("--run")
    p.add_argument("--criterion", help="acceptance criterion this check evidences")
    p.add_argument("--tail", type=int, default=20)
    p.add_argument("command", nargs=argparse.REMAINDER)
    for name in ("check", "report", "finish"):
        sub.add_parser(name).add_argument("--run")
    p = sub.add_parser("hook")
    p.add_argument("--require-run", action="store_true",
                   help="block edits in a git repository when no guarded run is open")
    args = parser.parse_args(argv)
    return {"start": cmd_start, "exec": cmd_exec, "check": cmd_check,
            "report": cmd_report, "finish": cmd_finish, "hook": cmd_hook}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
