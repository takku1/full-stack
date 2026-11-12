"""FS-023: live smoke test of the Claude Code plugin's plumbing (not design quality).

Runs four short headless sessions, each with an empty CLAUDE_CONFIG_DIR (only
the login copied), the plugin loaded via --plugin-dir, and a throwaway git repo:

  T1 discovery    plugin skill, agent, and hooks are registered; /full-stack:full-stack loads
  T2 pretooluse   during a guarded run, a Write outside the write set is refused by the hook
  T3 stop         an unclean guarded run makes the Stop hook continue the session
  T4 evidence     the stack-evidence subagent returns a cited table

Usage: python evals/plugin_smoke.py --auth-from-profile [--model sonnet] [--ceiling-usd 5]
Writes raw stream-json transcripts and summary.json under evals/results/plugin-smoke-<date>/.
Spends real money: each session is capped by --max-budget-usd; the run stops
before a session that could push the total past --ceiling-usd.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "skill"
GUARD = PLUGIN / "full-stack" / "scripts" / "run_guard.py"
LOGIN = Path.home() / ".claude" / ".credentials.json"


def sh(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=True).stdout


def make_repo(base, name):
    repo = base / name
    repo.mkdir()
    sh(repo, "git", "init", "-q")
    sh(repo, "git", "config", "user.email", "smoke@example.com")
    sh(repo, "git", "config", "user.name", "smoke")
    (repo / "a.txt").write_text("a\n")
    sh(repo, "git", "add", ".")
    sh(repo, "git", "commit", "-qm", "init")
    return repo


def guard(repo, *args):
    return subprocess.run([sys.executable, str(GUARD), *args], cwd=repo, capture_output=True, text=True)


def session(prompt, repo, args, env, tools, budget):
    config = Path(tempfile.mkdtemp(prefix="fs-smoke-config-"))
    shutil.copy2(LOGIN, config / ".credentials.json")
    command = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--model", args.model, "--max-budget-usd", str(budget),
               "--permission-mode", "acceptEdits", "--plugin-dir", str(PLUGIN),
               "--allowedTools", *tools]
    began = time.time()
    proc = subprocess.run(command, cwd=repo, env={**env, "CLAUDE_CONFIG_DIR": str(config)},
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    shutil.rmtree(config, ignore_errors=True)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events, proc, round(time.time() - began, 1)


def result_of(events):
    return next((e for e in reversed(events) if e.get("type") == "result"), {})


def init_of(events):
    return next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})


def tool_uses(events):
    out = []
    for e in events:
        if e.get("type") == "assistant":
            for item in e.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    out.append(item)
    return out


def tool_results(events):
    out = []
    for e in events:
        if e.get("type") == "user":
            content = e.get("message", {}).get("content", [])
            for item in content if isinstance(content, list) else []:
                if item.get("type") == "tool_result":
                    text = item.get("content")
                    if isinstance(text, list):
                        text = " ".join(part.get("text", "") for part in text if isinstance(part, dict))
                    out.append({"error": item.get("is_error", False), "text": str(text)})
    return out


def text_of(events):
    return "\n".join(item.get("text", "") for e in events if e.get("type") == "assistant"
                     for item in e.get("message", {}).get("content", []) if item.get("type") == "text")


def t1(base, args, env):
    repo = make_repo(base, "t1")
    prompt = ("/full-stack:full-stack In one sentence, state what this skill requires before changing code. "
              "Do not edit anything and do not read other files.")
    events, proc, secs = session(prompt, repo, args, env, ["Skill", "Read"], 0.75)
    init = init_of(events)
    flat = json.dumps(init)
    checks = {
        "init_lists_plugin_skill": "full-stack:full-stack" in flat,
        "init_lists_stack_evidence_agent": "stack-evidence" in flat,
        "answer_mentions_outcome_or_checks": any(w in text_of(events).lower() for w in ("outcome", "acceptance", "checks")),
    }
    return events, proc, secs, checks, {"init_keys": sorted(init)}


def t2(base, args, env):
    repo = make_repo(base, "t2")
    started = guard(repo, "start", "--write-set", "a.txt", "--label", "SMOKE-T2", "--routine", "smoke test")
    prompt = ("Use the Write tool to create the file b.txt containing the single line x. "
              "If the write is refused, quote the exact refusal reason and stop. Do not retry by any other means.")
    events, proc, secs = session(prompt, repo, args, env, ["Write", "Edit", "Read"], 0.75)
    results = tool_results(events)
    checks = {
        "guard_run_started": started.returncode == 0,
        "write_attempted": any(t.get("name") == "Write" for t in tool_uses(events)),
        "refusal_names_guard": any("run_guard" in r["text"] and "outside" in r["text"] for r in results),
        "b_txt_absent": not (repo / "b.txt").exists(),
    }
    return events, proc, secs, checks, {"tool_results": results[:4]}


def t3(base, args, env):
    repo = make_repo(base, "t3")
    guard(repo, "start", "--write-set", "a.txt", "--label", "SMOKE-T3", "--routine", "smoke test")
    (repo / "c.txt").write_text("out of scope\n")  # violation, and no checks recorded
    prompt = "Reply with the single word DONE and nothing else. Do not use any tools."
    events, proc, secs = session(prompt, repo, args, env, ["Read"], 0.5)
    result = result_of(events)
    flat = json.dumps(events)
    checks = {
        "stop_hook_feedback_seen": "not ready to close" in flat,
        "session_continued_after_stop": (result.get("num_turns") or 0) > 1 or text_of(events).count("DONE") > 1
                                         or "not ready to close" in text_of(events) or "run_guard" in text_of(events),
    }
    return events, proc, secs, checks, {"num_turns": result.get("num_turns"), "final_text": text_of(events)[-600:]}


def t4(base, args, env):
    repo = make_repo(base, "t4")
    prompt = ("Use the full-stack:stack-evidence subagent to gather evidence for two candidates: SQLite and PostgreSQL. "
              "The relevant limit is concurrent writers. Then reply with the subagent's table verbatim and nothing else.")
    events, proc, secs = session(prompt, repo, args, env, ["Agent", "Task", "WebSearch", "WebFetch", "Read"], 1.25)
    answer = text_of(events)
    uses = tool_uses(events)
    rows = [line for line in answer.splitlines() if line.startswith("|") and ("SQLite" in line or "PostgreSQL" in line)]
    checks = {
        "subagent_invoked": any(t.get("name") in ("Agent", "Task") and "stack-evidence" in json.dumps(t.get("input", {})) for t in uses),
        "two_rows_returned": len(rows) >= 2,
        "rows_cite_urls": all("http" in r for r in rows) if rows else False,
    }
    usage = result_of(events).get("modelUsage", {})
    return events, proc, secs, checks, {"rows": rows, "models_used": sorted(usage)}


def t5(base, args, env):
    """Shell writes bypass PreToolUse by design; the Stop hook must detect them."""
    repo = make_repo(base, "t5")
    guard(repo, "start", "--write-set", "a.txt", "--label", "SMOKE-T5", "--routine", "smoke test")
    prompt = "Run exactly this shell command with the Bash tool: echo x > c.txt\nThen reply DONE."
    events, proc, secs = session(prompt, repo, args, env, ["Bash(echo:*)"], 0.5)
    flat = json.dumps(events)
    checks = {
        "shell_write_happened": (repo / "c.txt").exists(),
        "stop_hook_detected_it": "outside the write set: c.txt" in flat,
    }
    return events, proc, secs, checks, {"final_text": text_of(events)[-600:]}


TESTS = [("T1-discovery", t1, 0.75), ("T2-pretooluse", t2, 0.75), ("T3-stop", t3, 0.5),
         ("T4-evidence", t4, 1.25), ("T5-shell-write", t5, 0.5)]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--auth-from-profile", action="store_true", required=True)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--ceiling-usd", type=float, default=5.0)
    parser.add_argument("--only", nargs="+", help="test names to run, e.g. T2-pretooluse")
    args = parser.parse_args()
    if not LOGIN.is_file():
        raise SystemExit(f"No Claude login at {LOGIN}.")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    out = ROOT / "evals" / "results" / f"plugin-smoke-{time.strftime('%Y-%m-%d')}"
    out.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="fs-smoke-repos-"))
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    summary, spent = {"claude": version, "model": args.model, "tests": {}}, 0.0
    for name, fn, cap in TESTS:
        if args.only and name not in args.only:
            continue
        if spent + cap > args.ceiling_usd:
            summary["tests"][name] = {"skipped": f"cap {cap} would exceed ceiling (spent {spent:.3f})"}
            continue
        events, proc, secs, checks, detail = fn(base, args, env)
        result = result_of(events)
        cost = float(result.get("total_cost_usd") or 0)
        spent += cost
        (out / f"{name}.jsonl").write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
        summary["tests"][name] = {
            "passed": all(checks.values()), "checks": checks, "cost_usd": round(cost, 4),
            "seconds": secs, "turns": result.get("num_turns"), "usage": result.get("usage", {}),
            "exit": proc.returncode, "stderr_tail": proc.stderr.strip().splitlines()[-5:], **detail,
        }
        print(f"{name}: {'PASS' if all(checks.values()) else 'FAIL'} {checks} ${cost:.4f} ({spent:.4f} total)")
    summary["total_cost_usd"] = round(spent, 4)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    shutil.rmtree(base, ignore_errors=True)
    print(f"total ${spent:.4f}; summary at {out / 'summary.json'}")


if __name__ == "__main__":
    main()
