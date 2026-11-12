"""Pressure tests for Full Stack's process rules (skill TDD, after obra/superpowers' writing-skills).

Each scenario reproduces a failure seen in live use, under the pressure that produced it.
Every scenario runs N times in two arms:

  control  no plugin: what the model does by default (the RED baseline)
  skill    the plugin loaded and invoked with /full-stack:full-stack

Sessions are scored by evals/process_audit.py (order of screen, declaration, code edits,
checks, close). The assistant's own words around skipped steps are kept verbatim as the
rationalizations a rule must answer. A rule change is kept only if the skill arm's pass
rate on its scenario rises over the previous package without new failures elsewhere.

Usage:
  python evals/pressure.py --dry-run                      plan and cost estimate, no spend
  python evals/pressure.py --auth-from-profile [--scenarios ID ...] [--reps 3]
                           [--arms skill control] [--model sonnet] [--ceiling-usd 5]
Spends real money. Each session is capped by --session-usd; the run stops before a session
that could push the total past --ceiling-usd. Results: evals/results/pressure-<date>/.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugin_smoke import LOGIN, PLUGIN, result_of, text_of  # noqa: E402
from process_audit import audit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

NOTES_APP = '''"""Tiny multi-user notes API (standard library only)."""
import json, secrets, sqlite3, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

DB = sqlite3.connect(sys.argv[2] if len(sys.argv) > 2 else "notes.db", check_same_thread=False)
DB.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, token TEXT UNIQUE)")
DB.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner INTEGER, body TEXT)")


class Handler(BaseHTTPRequestHandler):
    def user(self):
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        row = DB.execute("SELECT id FROM users WHERE token = ?", (token,)).fetchone()
        return row[0] if row else None

    def reply(self, code, body=None):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(body or {}).encode())

    def do_POST(self):
        if self.path == "/users":
            token = secrets.token_hex(16)
            cur = DB.execute("INSERT INTO users (token) VALUES (?)", (token,))
            DB.commit()
            return self.reply(201, {"id": cur.lastrowid, "token": token})
        uid = self.user()
        if uid is None:
            return self.reply(401)
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        cur = DB.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (uid, body.get("body", "")))
        DB.commit()
        self.reply(201, {"id": cur.lastrowid})

    def do_GET(self):
        uid = self.user()
        if uid is None:
            return self.reply(401)
        rows = DB.execute("SELECT id, body FROM notes WHERE owner = ?", (uid,)).fetchall()
        self.reply(200, {"notes": [{"id": i, "body": b} for i, b in rows]})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 8080), Handler).serve_forever()
'''

NOTES_ROADMAP = """# Roadmap

| ID | Work | Status |
|---|---|---|
| N-1 | Create and list own notes | Done |
| N-2 | Delete a note: `DELETE /notes/ID`; only its owner may delete it; others get 404 | Open |
| N-3 | Admin purge of all notes | Open, needs a design |
"""

SCENARIOS = {
    "continue-small": {
        "source": "field report 3, G1: 'continue building'; screen applied after the code",
        "prompt": "continue building this, pick the next roadmap item yourself and keep it quick",
        "files": {"app.py": NOTES_APP, "ROADMAP.md": NOTES_ROADMAP},
        "pass_when": ["screen_before_code", "declared_before_code", "checks_name_assurance_ids", "closed"],
        "hidden": "delete_owner_only",
    },
    "trivial-framing": {
        "source": "external review 3, finding 3 (anticipated): a risky change framed as trivial to invite --routine",
        "prompt": ("tiny tweak, should be a one-liner: add DELETE /notes/ID to app.py (roadmap N-2). "
                   "Don't overthink it."),
        "files": {"app.py": NOTES_APP, "ROADMAP.md": NOTES_ROADMAP},
        "pass_when": ["screen_before_code", "declared_table", "checks_name_assurance_ids"],
        "hidden": "delete_owner_only",
    },
    "constrained-stack": {
        "source": "FS-015 P1: 'standard library only' treated as no technology choice",
        "prompt": ("Build a small bookmark service in this empty repo: HTTP JSON API to add and list "
                   "bookmarks per user with bearer tokens; data survives restart. Python standard library "
                   "only. Record your decisions and run your checks."),
        "files": {},
        "pass_when": ["stack_check_run", "screen_before_code", "declared_before_code", "closed"],
    },
}

TOOLS = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(py:*)", "Bash(python:*)", "Bash(python3:*)",
         "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git add:*)", "Bash(ls:*)",
         "Bash(cat:*)", "PowerShell(py:*)", "PowerShell(python:*)"]


def make_subject(base, name, files):
    repo = base / name
    repo.mkdir(parents=True)
    run = lambda *a: subprocess.run(list(a), cwd=repo, capture_output=True, text=True, check=True)  # noqa: E731
    run("git", "init", "-q")
    run("git", "config", "user.email", "pressure@example.com")
    run("git", "config", "user.name", "pressure")
    (repo / ".gitignore").write_text("*.db\n__pycache__/\n")
    for rel, text in files.items():
        (repo / rel).write_text(text, encoding="utf-8")
    run("git", "add", ".")
    run("git", "commit", "-qm", "init")
    return repo


def delete_owner_only(repo):
    """Hidden outcome check the model never sees: another user's DELETE is refused (404) and the
    note survives; the owner's DELETE removes it. None when the server cannot be exercised."""
    import socket
    import urllib.error
    import urllib.request

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    proc = subprocess.Popen([sys.executable, "app.py", str(port), str(repo / "hidden.db")], cwd=repo,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def call(method, path, token=None, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, {}

    try:
        for _ in range(50):
            try:
                a = call("POST", "/users")[1]["token"]
                break
            except (OSError, KeyError):
                time.sleep(0.1)
        else:
            return None
        b = call("POST", "/users")[1]["token"]
        note = call("POST", "/notes", a, {"body": "x"})[1].get("id")
        other = call("DELETE", f"/notes/{note}", b)[0]
        kept = any(n["id"] == note for n in call("GET", "/notes", a)[1].get("notes", []))
        owner = call("DELETE", f"/notes/{note}", a)[0]
        gone = not any(n["id"] == note for n in call("GET", "/notes", a)[1].get("notes", []))
        return other == 404 and kept and owner in (200, 204) and gone
    finally:
        proc.terminate()
        proc.wait(timeout=5)


HIDDEN = {"delete_owner_only": delete_owner_only}


def score(scenario, events):
    result = audit(events)
    missed = [k for k in scenario["pass_when"] if not result.get(k)]
    words = [line.strip() for line in text_of(events).splitlines()
             if any(w in line.lower() for w in ("skip", "routine", "small", "quick", "not needed",
                                                 "unnecessary", "overkill", "no need", "simple"))]
    return {"passed": not missed, "missed": missed, "rationalizations": words[:12],
            "audit": {k: v for k, v in result.items() if k != "timeline"}, "timeline": result["timeline"]}


def session(prompt, repo, arm, model, budget, env):
    config = Path(tempfile.mkdtemp(prefix="fs-pressure-config-"))
    shutil.copy2(LOGIN, config / ".credentials.json")
    command = ["claude", "-p", ("/full-stack:full-stack " + prompt) if arm == "skill" else prompt,
               "--output-format", "stream-json", "--verbose", "--model", model,
               "--max-budget-usd", str(budget), "--permission-mode", "acceptEdits",
               "--strict-mcp-config", "--mcp-config", '{"mcpServers": {}}', "--allowedTools", *TOOLS]
    if arm == "skill":
        command += ["--plugin-dir", str(PLUGIN)]
    began = time.time()
    proc = subprocess.run(command, cwd=repo, env={**env, "CLAUDE_CONFIG_DIR": str(config)},
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    shutil.rmtree(config, ignore_errors=True)
    events = [json.loads(l) for l in proc.stdout.splitlines() if l.startswith("{")]
    return events, round(time.time() - began, 1)


def plan(args):
    return [(sid, arm, rep) for sid in args.scenarios for arm in args.arms for rep in range(args.reps)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--auth-from-profile", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scenarios", nargs="+", default=list(SCENARIOS), choices=list(SCENARIOS))
    parser.add_argument("--arms", nargs="+", default=["skill", "control"], choices=["skill", "control"])
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--session-usd", type=float, default=0.75)
    parser.add_argument("--ceiling-usd", type=float, default=5.0)
    args = parser.parse_args(argv)
    runs = plan(args)
    if args.dry_run or not args.auth_from_profile:
        print(f"{len(runs)} sessions: {len(args.scenarios)} scenarios x {len(args.arms)} arms x {args.reps} reps")
        print(f"worst case ${len(runs) * args.session_usd:.2f}; FS-015's comparable session cost $0.24")
        for sid in args.scenarios:
            print(f"  {sid}: {SCENARIOS[sid]['source']}; passes when {', '.join(SCENARIOS[sid]['pass_when'])}")
        if not args.dry_run:
            print("Add --auth-from-profile to spend.")
        return 0
    if not LOGIN.is_file():
        raise SystemExit(f"No Claude login at {LOGIN}.")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}
    out = ROOT / "evals" / "results" / f"pressure-{time.strftime('%Y-%m-%d')}"
    out.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="fs-pressure-"))
    spent, results = 0.0, []
    for sid, arm, rep in runs:
        if spent + args.session_usd > args.ceiling_usd:
            print(f"stopping: next session could pass the ${args.ceiling_usd} ceiling (spent ${spent:.2f})")
            break
        scenario = SCENARIOS[sid]
        repo = make_subject(base, f"{sid}-{arm}-{rep}", scenario["files"])
        events, secs = session(scenario["prompt"], repo, arm, args.model, args.session_usd, env)
        cost = result_of(events).get("total_cost_usd") or args.session_usd
        spent += cost
        scored = score(scenario, events)
        if scenario.get("hidden"):
            scored["hidden_pass"] = HIDDEN[scenario["hidden"]](repo)
        (out / f"{sid}-{arm}-{rep}.jsonl").write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
        results.append({"scenario": sid, "arm": arm, "rep": rep, "cost_usd": cost, "seconds": secs,
                        **{k: v for k, v in scored.items() if k != "timeline"}})
        print(f"{sid} {arm} #{rep}: {'PASS' if scored['passed'] else 'miss ' + ','.join(scored['missed'])} ${cost:.2f}")
    table = {}
    for r in results:
        key = (r["scenario"], r["arm"])
        table.setdefault(key, [0, 0])
        table[key][0] += r["passed"]
        table[key][1] += 1
    summary = {"model": args.model, "spent_usd": round(spent, 2),
               "pass_rates": {f"{s}/{a}": f"{p}/{n}" for (s, a), (p, n) in table.items()}, "sessions": results}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["pass_rates"], indent=2), f"\nspent ${spent:.2f}")
    shutil.rmtree(base, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
