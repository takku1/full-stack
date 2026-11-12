"""FS-015: first end-to-end trial of the Full Stack 0.5.0 plugin on one greenfield task.

One headless session (isolated profile, plugin via --plugin-dir, empty MCP config)
designs and builds a small multi-user HTTP API, then hidden acceptance checks the
model never sees run against the result. The transcript is mined for what the
package was supposed to make happen: stack flow and check_stack.py, decision
records, assurance screen and table, run_guard start/checks/close.

Usage: python evals/fs015_trial.py --auth-from-profile [--model sonnet] [--budget-usd 3]
Spends real money (one session, capped by --max-budget-usd).
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugin_smoke import LOGIN, PLUGIN, init_of, make_repo, result_of, text_of, tool_uses  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

PROMPT = """/full-stack:full-stack Design and build a small shared to-do service for a team, in this empty repository.

Required behavior:
- HTTP JSON API, started with: python app.py --port PORT --db PATH
- POST /users -> 201 {"id": ..., "token": ...}
- POST /lists with header "Authorization: Bearer TOKEN" and body {"title": "..."} -> 201 {"id": ...}
- GET /lists -> 200 {"lists": [...]} containing only the caller's lists
- GET /lists/ID -> 200 with the list for its owner; any other user gets 404
- Requests without a valid token get 401
- Data survives a server restart (same --db path)

Constraints: Python 3 standard library only (no pip installs). Keep it small.
Excluded: list sharing, editing, deletion, a web UI, deployment.

Choose the storage and structure yourself, record the decisions, and build it.
Run your checks and report what ran."""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def call(port, method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        return exc.code, None


def start_server(repo, port, db):
    proc = subprocess.Popen([sys.executable, "app.py", "--port", str(port), "--db", str(db)], cwd=repo,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return proc
        except OSError:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
    return proc


def hidden_checks(repo):
    """Acceptance checks the model never saw. Each returns True/False with a note."""
    results = {}
    if not (repo / "app.py").exists():
        return {"app_exists": (False, "no app.py")}
    db = Path(tempfile.mkdtemp(prefix="fs015-db-")) / "data.db"
    port = free_port()
    proc = start_server(repo, port, db)
    try:
        s, a = call(port, "POST", "/users", body={})
        s2, b = call(port, "POST", "/users", body={})
        results["create_users_201"] = (s == 201 and s2 == 201 and bool(a and a.get("token")), f"{s},{s2}")
        ta, tb = (a or {}).get("token"), (b or {}).get("token")
        s, lst = call(port, "POST", "/lists", ta, {"title": "groceries"})
        lid = (lst or {}).get("id")
        results["create_list_201"] = (s == 201 and lid is not None, str(s))
        s, _ = call(port, "GET", f"/lists/{lid}", ta)
        results["owner_reads_list_200"] = (s == 200, str(s))
        s, _ = call(port, "GET", f"/lists/{lid}", tb)
        results["other_user_gets_404"] = (s == 404, str(s))
        s, body = call(port, "GET", "/lists", tb)
        results["other_user_index_excludes"] = (s == 200 and not (body or {}).get("lists"), f"{s} {body}")
        s, _ = call(port, "GET", "/lists")
        s2, _ = call(port, "GET", "/lists", "not-a-real-token")
        results["no_or_bad_token_401"] = (s == 401 and s2 == 401, f"{s},{s2}")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    port = free_port()
    proc = start_server(repo, port, db)
    try:
        s, _ = call(port, "GET", f"/lists/{lid}", ta)
        results["survives_restart"] = (s == 200, str(s))
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    return results


def process_checks(events, repo):
    bash = [t.get("input", {}).get("command", "") for t in tool_uses(events) if t.get("name") == "Bash"]
    skills = [t for t in tool_uses(events) if t.get("name") == "Skill"]
    written = sorted(str(p.relative_to(repo)).replace("\\", "/") for p in repo.rglob("*")
                     if p.is_file() and ".git" not in p.parts)
    docs = "\n".join((repo / f).read_text(encoding="utf-8", errors="replace") for f in written if f.endswith(".md"))
    answer = text_of(events)
    both = docs + "\n" + answer
    init = json.dumps(init_of(events))
    return {
        "skill_loaded": bool(skills) or any(t.get("name") == "Read" and "full-stack" in json.dumps(t.get("input", {}))
                                            for t in tool_uses(events)),
        "check_stack_profiles_run": any("check_stack.py" in c and "profiles" in c for c in bash),
        "check_stack_check_run": any("check_stack.py" in c and " check" in c for c in bash),
        "stack_block_written": "```json stack" in docs,
        "decision_records": both.count("Decision") >= 1 and "Candidates" in both,
        "assurance_screen": "Screen" in both or "screen" in both,
        "assurance_table": "| A-1" in both or ("Claim" in both and "Evidence" in both),
        "run_guard_start": any("run_guard.py" in c and " start" in c for c in bash),
        "run_guard_checks": any("run_guard.py" in c and (" checks" in c or " exec" in c) for c in bash),
        "run_guard_close": any("run_guard.py" in c and " close" in c for c in bash),
        "connectors_absent": "claude_ai_Gmail" not in init,
        "files_written": written,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--auth-from-profile", action="store_true", required=True)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--budget-usd", type=float, default=3.0)
    args = parser.parse_args()
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    out = ROOT / "evals" / "results" / f"fs015-{time.strftime('%Y-%m-%d')}"
    out.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="fs015-"))
    repo = make_repo(base, "repo")
    (repo / "a.txt").unlink()
    subprocess.run(["git", "commit", "-qam", "empty"], cwd=repo, capture_output=True)
    config = Path(tempfile.mkdtemp(prefix="fs015-config-"))
    shutil.copy2(LOGIN, config / ".credentials.json")
    tools = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Agent", "Task", "WebSearch", "WebFetch",
             "Bash(python:*)", "Bash(python3:*)", "Bash(py:*)", "Bash(git status:*)", "Bash(git diff:*)",
             "Bash(git log:*)", "Bash(git add:*)", "Bash(ls:*)", "Bash(cat:*)"]
    command = ["claude", "-p", PROMPT, "--output-format", "stream-json", "--verbose", "--model", args.model,
               "--max-budget-usd", str(args.budget_usd), "--permission-mode", "acceptEdits",
               "--plugin-dir", str(PLUGIN), "--strict-mcp-config", "--mcp-config", '{"mcpServers": {}}',
               "--allowedTools", *tools]
    began = time.time()
    proc = subprocess.run(command, cwd=repo, env={**env, "CLAUDE_CONFIG_DIR": str(config)},
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    secs = round(time.time() - began, 1)
    shutil.rmtree(config, ignore_errors=True)
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    (out / "transcript.jsonl").write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
    result = result_of(events)
    hidden = hidden_checks(repo)
    process = process_checks(events, repo)
    workspace = out / "workspace"
    shutil.rmtree(workspace, ignore_errors=True)
    shutil.copytree(repo, workspace, ignore=shutil.ignore_patterns(".git", "*.db", "__pycache__"))
    summary = {
        "claude": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
        "model": args.model, "budget_usd": args.budget_usd, "seconds": secs, "exit": proc.returncode,
        "cost_usd": result.get("total_cost_usd"), "turns": result.get("num_turns"),
        "usage": result.get("usage", {}), "models_used": sorted(result.get("modelUsage", {})),
        "hidden_checks": {k: {"pass": v[0], "note": v[1]} for k, v in hidden.items()},
        "process": process, "final_answer": text_of(events)[-3000:],
        "stderr_tail": proc.stderr.strip().splitlines()[-5:],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    passed = sum(1 for v in hidden.values() if v[0])
    print(f"cost ${summary['cost_usd']} turns {summary['turns']} {secs}s; hidden {passed}/{len(hidden)}")
    for k, v in hidden.items():
        print(f"  hidden {k}: {'PASS' if v[0] else 'FAIL'} ({v[1]})")
    for k, v in process.items():
        if k != "files_written":
            print(f"  process {k}: {v}")
    print(f"  files: {process['files_written']}")
    shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    main()
