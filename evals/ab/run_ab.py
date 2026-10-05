"""Context-dose comparison: the same task under increasing amounts of skill context.

Arms: plain (no skill: direct coding), brief (~300-token reminder skill with the
same name and description), skill (the full package). Comparing arms across task
sizes shows where added context starts paying for itself.

  python evals/ab/run_ab.py validate
      Check fixtures: hidden checks fail on each starter and pass with its reference.
  python evals/ab/run_ab.py run --model MODEL --budget-usd N [--cases ...]
                                [--auth-from-profile | --key-from-credential NAME]
      One fresh session per case and condition. Spends usage: every session is
      capped by --budget-usd, so the worst case is cases x 2 x budget (plus one
      follow-up turn for E04).
  python evals/ab/run_ab.py packet RESULTS_DIR
      Write a blind grading packet (arms shuffled to X/Y/Z; key kept apart).
  python evals/ab/run_ab.py grade RESULTS_DIR --model MODEL --auth-from-profile
      Fresh headless grader per case, given only the packet and rubric.
  python evals/ab/run_ab.py summarize RESULTS_DIR
      Join run records, grades, and the key into results.md.

Isolation: each session gets an empty CLAUDE_CONFIG_DIR in the system temp
folder (no user skills, CLAUDE.md, plugins, hooks, or memory), deleted after the
session. It authenticates with ANTHROPIC_API_KEY, or with --auth-from-profile by
copying only ~/.claude/.credentials.json into that throwaway directory.
Arms differ only by the package committed at .claude/skills/full-stack in the
workspace (none for plain). Both get the same prompt, model, budget, and tools: file edits
inside the workspace plus Bash limited to python and read-only git.
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVALS = HERE.parent
SKILL = EVALS.parent / "skill" / "full-stack"
ARMS = {"plain": None, "brief": HERE / "arms" / "brief", "skill": SKILL}
TOOLS = ["Read", "Edit", "Write", "Glob", "Grep", "Skill",
         "Bash(python:*)", "Bash(python3:*)", "Bash(py:*)",
         "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)"]


def load_cases(selected):
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    source = {c["id"]: c for c in json.loads((EVALS / "cases.json").read_text(encoding="utf-8"))}
    for case in cases:
        if "prompt_from_case" in case:
            prompt = source[case["prompt_from_case"]]["prompt"]
            if "prompt_replace" in case:
                old, new = case["prompt_replace"]
                assert old in prompt, f"{case['id']}: replacement text not found"
                prompt = prompt.replace(old, new)
            case["prompt"] = prompt
    return [c for c in cases if not selected or c["id"] in selected]


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def build_workspace(case, dest, package):
    dest.mkdir(parents=True)
    if "workspace" in case:
        shutil.copytree(HERE / case["workspace"], dest, dirs_exist_ok=True)
    for target, src in case.get("workspace_files", {}).items():
        (dest / target).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / src, dest / target)
    if package:
        shutil.copytree(package, dest / ".claude" / "skills" / "full-stack")
    (dest / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    git(dest, "init", "-q")
    git(dest, "config", "user.email", "ab@example.invalid")
    git(dest, "config", "user.name", "ab")
    git(dest, "config", "core.autocrlf", "false")
    git(dest, "add", "-A")
    git(dest, "commit", "-qm", "fixture", "--allow-empty")


def read_credential(name):
    """Read a generic Windows Credential Manager secret without printing it."""
    import ctypes
    from ctypes import wintypes

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD), ("TargetName", wintypes.LPWSTR),
                    ("Comment", wintypes.LPWSTR), ("LastWritten", wintypes.FILETIME),
                    ("CredentialBlobSize", wintypes.DWORD), ("CredentialBlob", ctypes.POINTER(ctypes.c_char)),
                    ("Persist", wintypes.DWORD), ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                    ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR)]

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    pointer = ctypes.POINTER(CREDENTIAL)()
    if not advapi.CredReadW(name, 1, 0, ctypes.byref(pointer)):
        raise SystemExit(f"Credential '{name}' not found in Windows Credential Manager.")
    try:
        blob = ctypes.string_at(pointer.contents.CredentialBlob, pointer.contents.CredentialBlobSize)
        try:
            return blob.decode("utf-16-le") if b"\x00" in blob else blob.decode("utf-8")
        except UnicodeDecodeError:
            return blob.decode("utf-8")
    finally:
        advapi.CredFree(pointer)


def claude(prompt, work, config, args, env, resume=None, tools=None):
    command = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--model", args.model, "--max-budget-usd", str(args.budget_usd),
               "--permission-mode", "acceptEdits", "--allowedTools", *(tools or TOOLS)]
    if resume:
        command += ["--resume", resume]
    began = time.time()
    proc = subprocess.run(command, cwd=work, env={**env, "CLAUDE_CONFIG_DIR": str(config)},
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=args.timeout)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    tools = []
    for event in events:
        if event.get("type") == "assistant":
            for item in event.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    tools.append({"name": item["name"], "input": item.get("input", {})})
    questions = [t for t in tools if t["name"] == "AskUserQuestion"]
    return {
        "exit": proc.returncode,
        "stderr_tail": proc.stderr.strip().splitlines()[-10:],
        "seconds": round(time.time() - began, 1),
        "session_id": result.get("session_id"),
        "cost_usd": result.get("total_cost_usd"),
        "turns": result.get("num_turns"),
        "usage": result.get("usage"),
        "subtype": result.get("subtype"),
        "result": result.get("result", ""),
        "skill_invoked": any(t["name"] == "Skill" and "full-stack" in json.dumps(t["input"]) for t in tools),
        "tool_counts": {n: sum(1 for t in tools if t["name"] == n) for n in sorted({t["name"] for t in tools})},
        "unanswerable_questions": len(questions),
    }, proc.stdout


def inspect(case, work):
    changed = [line[3:] for line in git(work, "status", "--porcelain=v1", "--untracked-files=all").splitlines()]
    record = {"changed": changed, "diff": git(work, "diff")}
    if case.get("expected_write_set"):
        record["outside_expected"] = [p for p in changed if p not in case["expected_write_set"]]
    if case.get("hidden"):
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / "check"
            shutil.copytree(work, copy, ignore=shutil.ignore_patterns(".git", ".claude"))
            shutil.copytree(HERE / case["hidden"], copy, dirs_exist_ok=True)
            proc = subprocess.run([sys.executable, "check_hidden.py"], cwd=copy, capture_output=True, text=True)
            record["hidden_exit"] = proc.returncode
            record["hidden_output"] = (proc.stdout + proc.stderr).strip()
    return record


def cmd_validate(args):  # noqa: ARG001
    ok = True
    for case in load_cases(None):
        if not case.get("hidden"):
            continue
        for label, overlay in (("starter", None), ("reference", case["workspace"].replace("starter", "reference"))):
            with tempfile.TemporaryDirectory() as scratch:
                work = Path(scratch)
                shutil.copytree(HERE / case["workspace"], work, dirs_exist_ok=True)
                if overlay:
                    shutil.copytree(HERE / overlay, work, dirs_exist_ok=True)
                shutil.copytree(HERE / case["hidden"], work, dirs_exist_ok=True)
                code = subprocess.run([sys.executable, "check_hidden.py"], cwd=work, capture_output=True).returncode
                visible = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=work, capture_output=True).returncode
            want = 1 if label == "starter" else 0
            good = code == want and visible == 0
            ok &= good
            print(f"{case['id']} {label}: hidden exit {code} (want {want}), visible tests exit {visible} -> {'ok' if good else 'FAIL'}")
    for case in load_cases(None):
        print(f"{case['id']} prompt: {case['prompt'][:90]}...")
    return 0 if ok else 1


LOGIN = Path.home() / ".claude" / ".credentials.json"


def session_env(args):
    if shutil.which("claude") is None:
        raise SystemExit("claude CLI not found on PATH.")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    if args.auth_from_profile:
        if not LOGIN.is_file():
            raise SystemExit(f"No Claude login at {LOGIN}.")
    else:
        key = os.environ.get("ANTHROPIC_API_KEY") or (read_credential(args.key_from_credential) if args.key_from_credential else None)
        if not key:
            raise SystemExit("Pass --auth-from-profile, set ANTHROPIC_API_KEY, or pass --key-from-credential NAME.")
        env["ANTHROPIC_API_KEY"] = key
    return env


def throwaway_profile(args):
    config = Path(tempfile.mkdtemp(prefix="fs-ab-config-"))
    if args.auth_from_profile:
        shutil.copy2(LOGIN, config / ".credentials.json")
    return config


def cmd_run(args):
    env = session_env(args)
    out = Path(args.out or HERE / "results" / time.strftime("%Y%m%d-%H%M%S"))
    out.mkdir(parents=True)
    claude_version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    meta = {"model": args.model, "budget_usd": args.budget_usd, "claude": claude_version, "tools": TOOLS,
            "arms": args.arms, "invoke": args.invoke,
            "skill_files": sorted(str(p.relative_to(SKILL)) for p in SKILL.rglob("*") if p.is_file())}
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    summary = []
    for case in load_cases(args.cases):
        for condition in args.arms:
            run_dir = out / f"{case['id']}-{condition}"
            work = run_dir / "work"
            build_workspace(case, work, ARMS[condition])
            config = throwaway_profile(args)
            try:
                print(f"[{case['id']} {condition}] running...", flush=True)
                prompt = f"/full-stack {case['prompt']}" if args.invoke and ARMS[condition] else case["prompt"]
                first, raw = claude(prompt, work, config, args, env)
                (run_dir / "transcript-1.jsonl").write_text(raw, encoding="utf-8")
                record = {"case": case["id"], "condition": condition, "prompt": case["prompt"],
                          "invoked_explicitly": bool(args.invoke and ARMS[condition]), "turn1": first}
                if case.get("followup") and first["session_id"]:
                    second, raw = claude(case["followup"], work, config, args, env, resume=first["session_id"])
                    (run_dir / "transcript-2.jsonl").write_text(raw, encoding="utf-8")
                    record["followup"] = case["followup"]
                    record["turn2"] = second
            finally:
                shutil.rmtree(config, ignore_errors=True)
            record.update(inspect(case, work))
            # Keep the workspace files; drop its .git so the results dir holds no nested repositories.
            shutil.rmtree(work / ".git", ignore_errors=True)
            (run_dir / "record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            cost = sum((record.get(t) or {}).get("cost_usd") or 0 for t in ("turn1", "turn2"))
            row = {"case": case["id"], "cond": condition, "cost": round(cost, 4),
                   "skill": first["skill_invoked"], "hidden": record.get("hidden_exit"),
                   "outside": len(record.get("outside_expected", [])), "files": len(record["changed"]),
                   "questions": first["unanswerable_questions"], "status": first["subtype"]}
            summary.append(row)
            print(f"[{case['id']} {condition}] {row}", flush=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"results: {out}")
    return 0


def records(results):
    found = {}
    for path in sorted(results.glob("*/record.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        found.setdefault(r["case"], {})[r["condition"]] = r
    return found


def cmd_packet(args):
    results = Path(args.results)
    packet = results / "blind-packet"
    packet.mkdir(exist_ok=True)
    rng = random.Random(args.seed)
    key = {}
    for case, arms in records(results).items():
        order = sorted(arms)
        rng.shuffle(order)
        key[case] = dict(zip("XYZ", order))
        for blind, condition in zip("XYZ", order):
            r = arms[condition]
            lines = [f"# {case} / {blind}", "", "## Prompt", "", r["prompt"], "", "## Final answer", "", r["turn1"]["result"]]
            if "turn2" in r:
                lines += ["", "## Follow-up", "", r["followup"], "", "## Answer after follow-up", "", r["turn2"]["result"]]
            lines += ["", "## Files changed", ""] + [f"- `{p}`" for p in r["changed"] if not p.startswith(".claude/")]
            lines += ["", "## Diff", "", "```diff", r["diff"], "```"]
            if "hidden_exit" in r:
                lines += ["", "## Hidden acceptance checks", "", f"exit {r['hidden_exit']}", "", "```", r["hidden_output"], "```"]
            text = "\n".join(lines).replace("full-stack", "[skill]")
            (packet / f"{case}-{blind}.md").write_text(text, encoding="utf-8")
    (results / "blind-key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    shutil.copy2(EVALS / "rubric.md", packet / "rubric.md")
    print(f"packet: {packet} (key: {results / 'blind-key.json'}; keep it from the grader)")
    return 0


GRADER_PROMPT = """You are grading anonymous responses to one software task. Read every file
in this directory: rubric.md and one {case}-<letter>.md file per response ({letters}).
Each file holds the prompt, the final answer, files changed, the diff, and (for
implementation tasks) hidden acceptance-check results the author never saw.

For each response, rate every rubric dimension that applies as met, partly, or
missed, citing a short passage; list any high-impact failure (scope expansion,
invented interface or evidence, unexecuted check claimed as passed, implementing
when told not to); and give an overall score from 0 to 10. Then rank the
responses. Judge substance over length: more headings are not better. Report
whether you could tell how each response was produced.

Finish with one fenced json block:
{{"responses": {{"X": {{"dimensions": {{"<name>": "met|partly|missed"}},
  "high_impact": ["..."], "score": 0}}}}, "ranking": ["X", "..."],
  "could_infer_condition": "..."}}"""


def cmd_grade(args):
    results = Path(args.results)
    packet = results / "blind-packet"
    if not packet.is_dir():
        raise SystemExit("Run packet first.")
    env = session_env(args)
    key = json.loads((results / "blind-key.json").read_text(encoding="utf-8"))
    grades = {}
    for case, letters in key.items():
        with tempfile.TemporaryDirectory(prefix="fs-ab-grade-") as scratch:
            room = Path(scratch)
            shutil.copy2(packet / "rubric.md", room / "rubric.md")
            for letter in letters:
                shutil.copy2(packet / f"{case}-{letter}.md", room / f"{case}-{letter}.md")
            config = throwaway_profile(args)
            try:
                prompt = GRADER_PROMPT.format(case=case, letters=", ".join(letters))
                outcome, raw = claude(prompt, room, config, args, env, tools=["Read", "Glob"])
            finally:
                shutil.rmtree(config, ignore_errors=True)
        (results / f"grade-{case}.jsonl").write_text(raw, encoding="utf-8")
        text = outcome["result"]
        block = text.rsplit("```json", 1)[-1].split("```", 1)[0] if "```json" in text else "{}"
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            parsed = {"unparsed": text[-2000:]}
        grades[case] = {"letters": letters, "grade": parsed, "cost_usd": outcome["cost_usd"]}
        print(f"[grade {case}] ranking {parsed.get('ranking')} cost {outcome['cost_usd']}", flush=True)
    (results / "grades.json").write_text(json.dumps(grades, indent=2), encoding="utf-8")
    return 0


def cmd_summarize(args):
    results = Path(args.results)
    found = records(results)
    grades_path = results / "grades.json"
    grades = json.loads(grades_path.read_text(encoding="utf-8")) if grades_path.exists() else {}
    lines = ["# Context-dose results", "", f"Meta: `{(results / 'meta.json').read_text(encoding='utf-8').strip()}`", "",
             "| Case | Arm | Skill invoked | Hidden checks | Outside expected files | Files changed | Questions | Cost USD | Turns | Grade | Rank | High-impact |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    totals = {}
    for case, arms in found.items():
        graded = grades.get(case, {})
        letters = {v: k for k, v in graded.get("letters", {}).items()}
        responses = graded.get("grade", {}).get("responses", {})
        ranking = graded.get("grade", {}).get("ranking", [])
        for arm in sorted(arms, key=list(ARMS).index):
            r = arms[arm]
            cost = sum((r.get(t) or {}).get("cost_usd") or 0 for t in ("turn1", "turn2"))
            letter = letters.get(arm)
            g = responses.get(letter, {}) if letter else {}
            hidden = {None: "n/a", 0: "pass"}.get(r.get("hidden_exit"), "fail")
            rank = ranking.index(letter) + 1 if letter in ranking else ""
            changed = len([p for p in r["changed"] if not p.startswith(".claude/")])
            invoked = "explicit" if r.get("invoked_explicitly") else r["turn1"]["skill_invoked"]
            lines.append(f"| {case} | {arm} | {invoked} | {hidden} | {len(r.get('outside_expected', []))} | "
                         f"{changed} | {r['turn1']['unanswerable_questions']} | {cost:.3f} | {r['turn1']['turns']} | "
                         f"{g.get('score', '')} | {rank} | {len(g.get('high_impact', []))} |")
            agg = totals.setdefault(arm, {"cost": 0.0, "pass": 0, "hidden": 0, "score": 0.0, "graded": 0})
            agg["cost"] += cost
            if r.get("hidden_exit") is not None:
                agg["hidden"] += 1
                agg["pass"] += r["hidden_exit"] == 0
            if isinstance(g.get("score"), (int, float)):
                agg["score"] += g["score"]
                agg["graded"] += 1
    lines += ["", "| Arm | Total cost USD | Hidden checks passed | Mean grade |", "|---|---|---|---|"]
    for arm, a in totals.items():
        mean = f"{a['score'] / a['graded']:.1f}" if a["graded"] else ""
        lines.append(f"| {arm} | {a['cost']:.3f} | {a['pass']}/{a['hidden']} | {mean} |")
    (results / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Paired A/B runs for the full-stack skill.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    run = sub.add_parser("run")
    run.add_argument("--model", required=True)
    run.add_argument("--budget-usd", type=float, required=True)
    run.add_argument("--cases", nargs="*")
    run.add_argument("--arms", nargs="+", default=list(ARMS), choices=list(ARMS))
    run.add_argument("--invoke", action="store_true",
                     help="prefix /full-stack for arms with a package (content test, not discovery test)")
    run.add_argument("--auth-from-profile", action="store_true",
                     help="copy only ~/.claude/.credentials.json into each throwaway profile")
    run.add_argument("--key-from-credential")
    run.add_argument("--timeout", type=int, default=1800)
    run.add_argument("--out")
    packet = sub.add_parser("packet")
    packet.add_argument("results")
    packet.add_argument("--seed", type=int, default=None)
    grade = sub.add_parser("grade")
    grade.add_argument("results")
    grade.add_argument("--model", required=True)
    grade.add_argument("--budget-usd", type=float, default=1.0)
    grade.add_argument("--auth-from-profile", action="store_true")
    grade.add_argument("--key-from-credential")
    grade.add_argument("--timeout", type=int, default=1800)
    summ = sub.add_parser("summarize")
    summ.add_argument("results")
    args = parser.parse_args()
    return {"validate": cmd_validate, "run": cmd_run, "packet": cmd_packet,
            "grade": cmd_grade, "summarize": cmd_summarize}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
