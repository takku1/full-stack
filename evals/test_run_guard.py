"""Exercise skill/full-stack/scripts/run_guard.py against throwaway git repositories."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).resolve().parents[1] / "skill" / "full-stack" / "scripts" / "run_guard.py"


def sh(cwd, *args):
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=True).stdout


def guard(cwd, *args):
    result = subprocess.run([sys.executable, str(GUARD), *args], cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


class RunGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        sh(self.repo, "git", "init", "-q")
        sh(self.repo, "git", "config", "user.email", "t@example.com")
        sh(self.repo, "git", "config", "user.name", "t")
        sh(self.repo, "git", "config", "core.autocrlf", "false")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "a.py").write_text("a = 1\n")
        (self.repo / "src" / "b.py").write_text("b = 1\n")
        (self.repo / "README.md").write_text("readme\n")
        sh(self.repo, "git", "add", ".")
        sh(self.repo, "git", "commit", "-qm", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def test_checks_runs_all_in_one_call(self):
        guard(self.repo, "start", "--write-set", "src/")
        ok = f'"{sys.executable}" -c "print(1)"'
        bad = f'"{sys.executable}" -c "raise SystemExit(4)"'
        code, out = guard(self.repo, "checks", "--each", f"prints :: {ok}", "--each", f"fails :: {bad}")
        self.assertEqual(code, 1, out)
        self.assertIn("1/2 checks passed", out)
        code, out = guard(self.repo, "report")
        self.assertIn("| prints | 0 |", out)
        self.assertIn("| fails | 4 |", out)

    def test_checks_accepts_json_plan_and_rejects_bad_each(self):
        guard(self.repo, "start", "--write-set", "src/")
        plan = Path(self.tmp.name) / "plan.json"
        plan.write_text(json.dumps([{"criterion": "c1", "command": [sys.executable, "-c", "print(2)"]}]))
        code, out = guard(self.repo, "checks", "--plan", str(plan))
        self.assertEqual(code, 0, out)
        code, out = guard(self.repo, "checks", "--each", "no separator")
        self.assertEqual(code, 2, out)

    def test_close_finishes_clean_run_and_holds_dirty_one(self):
        guard(self.repo, "start", "--write-set", "src/a.py")
        (self.repo / "src" / "a.py").write_text("a = 5\n")
        code, out = guard(self.repo, "close")
        self.assertEqual(code, 1, out)  # no checks recorded
        self.assertIn("run left open", out)
        guard(self.repo, "exec", "--criterion", "c", "--", sys.executable, "-c", "print(3)")
        code, out = guard(self.repo, "close")
        self.assertEqual(code, 0, out)
        self.assertIn("finished", out)
        code, out = guard(self.repo, "start", "--write-set", "src/a.py", "--adopt", "src/a.py")  # closed run no longer collides
        self.assertEqual(code, 0, out)

    def test_close_accept_blockers_finishes_with_violation(self):
        guard(self.repo, "start", "--write-set", "src/a.py")
        (self.repo / "README.md").write_text("out of scope\n")
        guard(self.repo, "exec", "--criterion", "c", "--", sys.executable, "-c", "print(4)")
        code, out = guard(self.repo, "close", "--accept-blockers")
        self.assertEqual(code, 1, out)
        self.assertIn("finished with reported blockers", out)

    def test_clean_run_within_write_set(self):
        code, out = guard(self.repo, "start", "--write-set", "src/a.py", "--label", "WP-1")
        self.assertEqual(code, 0, out)
        (self.repo / "src" / "a.py").write_text("a = 2\n")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 0, out)
        self.assertIn("changed: src/a.py", out)

    def test_bare_directory_name_claims_its_contents(self):
        # Observed live: a model claimed "tasks" (no trailing slash) for tasks/*.py.
        guard(self.repo, "start", "--write-set", "src")
        (self.repo / "src" / "a.py").write_text("a = 3\n")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 0, out)

    def test_change_outside_write_set_is_a_violation(self):
        guard(self.repo, "start", "--write-set", "src/a.py")
        (self.repo / "README.md").write_text("expanded scope\n")
        (self.repo / "new.txt").write_text("new\n")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 1)
        self.assertIn("outside the write set: README.md", out)
        self.assertIn("outside the write set: new.txt", out)

    def test_committed_change_outside_write_set_is_caught(self):
        guard(self.repo, "start", "--write-set", "src/")
        (self.repo / "README.md").write_text("sneaky\n")
        sh(self.repo, "git", "commit", "-qam", "edit")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 1)
        self.assertIn("outside the write set: README.md", out)

    def test_start_refuses_write_set_over_outside_edits(self):
        (self.repo / "src" / "a.py").write_text("developer edit\n")
        code, out = guard(self.repo, "start", "--write-set", "src/")
        self.assertEqual(code, 3)
        self.assertIn("uncommitted edit made outside this run: src/a.py", out)
        self.assertIn("rerun with: --adopt src/a.py", out)  # one list form (field report 3, D1)

    def test_adopted_edit_is_allowed_and_tracked_as_run_change(self):
        (self.repo / "src" / "a.py").write_text("resumed work\n")
        code, out = guard(self.repo, "start", "--write-set", "src/", "--adopt", "src/a.py")
        self.assertEqual(code, 0, out)
        (self.repo / "src" / "a.py").write_text("finished work\n")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 0, out)
        self.assertIn("changed: src/a.py", out)

    def test_touching_preexisting_edit_outside_write_set_is_a_violation(self):
        (self.repo / "README.md").write_text("developer edit\n")
        self.assertEqual(guard(self.repo, "start", "--write-set", "src/")[0], 0)
        (self.repo / "README.md").write_text("overwritten\n")
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 1)
        self.assertIn("changed an edit that existed before the run: README.md", out)

    def test_overlapping_parallel_runs_collide_until_finished(self):
        self.assertEqual(guard(self.repo, "start", "--write-set", "src/", "--label", "WP-1")[0], 0)
        code, out = guard(self.repo, "start", "--write-set", "src/b.py", "--label", "WP-2")
        self.assertEqual(code, 3)
        self.assertIn("WP-1", out)
        self.assertEqual(guard(self.repo, "start", "--write-set", "docs/", "--label", "WP-3")[0], 0)
        guard(self.repo, "finish")  # finishes the latest run (WP-3); WP-1 still open
        self.assertEqual(guard(self.repo, "start", "--write-set", "src/b.py")[0], 3)

    def test_worktrees_share_open_runs(self):
        self.assertEqual(guard(self.repo, "start", "--write-set", "src/a.py", "--label", "main-tree")[0], 0)
        tree = Path(self.tmp.name) / "tree"
        sh(self.repo, "git", "worktree", "add", "-q", str(tree))
        code, out = guard(tree, "start", "--write-set", "src/a.py")
        self.assertEqual(code, 3, out)
        self.assertIn("main-tree", out)

    # FS-023 operational cases (external review, 2026-11-12). Written before any fix.

    def hook_at(self, cwd, event):
        result = subprocess.run([sys.executable, str(GUARD), "hook"], cwd=cwd,
                                input=json.dumps({"cwd": str(cwd), **event}), capture_output=True, text=True)
        return result.returncode, result.stderr

    def test_each_worktree_hook_checks_its_own_run(self):
        self.assertEqual(guard(self.repo, "start", "--write-set", "src/a.py", "--label", "main")[0], 0)
        tree = Path(self.tmp.name) / "tree"
        sh(self.repo, "git", "worktree", "add", "-q", str(tree))
        self.assertEqual(guard(tree, "start", "--write-set", "src/b.py", "--label", "tree")[0], 0)
        # main's run does not claim src/b.py: an edit to it from the main tree must be refused
        code, err = self.hook_at(self.repo, {"hook_event_name": "PreToolUse", "tool_name": "Write",
                                             "tool_input": {"file_path": str(self.repo / "src" / "b.py")}})
        self.assertEqual(code, 2, f"main tree edit to b.py was allowed: {err}")
        code, err = self.hook_at(tree, {"hook_event_name": "PreToolUse", "tool_name": "Write",
                                        "tool_input": {"file_path": str(tree / "src" / "a.py")}})
        self.assertEqual(code, 2, f"tree edit to a.py was allowed: {err}")

    def test_commands_without_run_id_resolve_this_worktrees_run(self):
        guard(self.repo, "start", "--write-set", "src/a.py", "--label", "main")
        tree = Path(self.tmp.name) / "tree"
        sh(self.repo, "git", "worktree", "add", "-q", str(tree))
        guard(tree, "start", "--write-set", "src/b.py", "--label", "tree")
        out = guard(self.repo, "report")[1]
        self.assertIn("`src/a.py`", out, "main tree report resolved another worktree's run")

    def test_close_refuses_failed_checks_without_accept_blockers(self):
        guard(self.repo, "start", "--write-set", "src/a.py")
        (self.repo / "src" / "a.py").write_text("a = 9\n")
        guard(self.repo, "exec", "--criterion", "tests", "--", sys.executable, "-c", "raise SystemExit(1)")
        code, out = guard(self.repo, "close")
        self.assertEqual(code, 1, out)
        self.assertIn("run left open", out)
        # a later passing rerun of the same criterion makes the run closable
        guard(self.repo, "exec", "--criterion", "tests", "--", sys.executable, "-c", "print('ok')")
        code, out = guard(self.repo, "close")
        self.assertEqual(code, 0, out)

    def test_hook_without_python_is_visible(self):
        hook = GUARD.parent / "guard_hook.sh"
        shell = shutil.which("sh")
        if not shell:
            self.skipTest("no sh on PATH")
        env = {**os.environ, "FULL_STACK_GUARD_PYTHONS": "no-such-python-a,no-such-python-b"}
        for event, visible in (("SessionStart", True), ("Stop", True), ("PreToolUse", False)):
            result = subprocess.run([shell, str(hook)], input=json.dumps({"hook_event_name": event}),
                                    capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual("guard inactive" in result.stdout, visible, f"{event}: {result.stdout!r}")

    def test_hook_launcher_passes_event_to_guard(self):
        shell = shutil.which("sh")
        if not shell:
            self.skipTest("no sh on PATH")
        guard(self.repo, "start", "--write-set", "src/a.py")
        event = {"hook_event_name": "PreToolUse", "cwd": str(self.repo), "tool_name": "Write",
                 "tool_input": {"file_path": str(self.repo / "README.md")}}
        result = subprocess.run([shell, str(GUARD.parent / "guard_hook.sh")], input=json.dumps(event),
                                capture_output=True, text=True, cwd=self.repo)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outside this run's write set", result.stderr)

    def test_exec_records_checks_and_report_lists_them(self):
        guard(self.repo, "start", "--write-set", "src/")
        code, _ = guard(self.repo, "exec", "--criterion", "passes", "--", sys.executable, "-c", "print('ok')")
        self.assertEqual(code, 0)
        code, _ = guard(self.repo, "exec", "--", sys.executable, "-c", "import sys; sys.exit(4)")
        self.assertEqual(code, 4)
        code, out = guard(self.repo, "report")
        self.assertEqual(code, 0, out)
        self.assertIn("| passes | 0 |", out)
        self.assertIn("| 4 |", out)

    def test_report_with_no_checks_says_none_executed(self):
        guard(self.repo, "start", "--write-set", "src/")
        self.assertIn("none executed", guard(self.repo, "report")[1])

    def shared_file(self):
        lines = [f"line {i}\n" for i in range(1, 11)]
        (self.repo / "shared.txt").write_text("".join(lines))
        sh(self.repo, "git", "add", "shared.txt")
        sh(self.repo, "git", "commit", "-qm", "shared")
        lines[1] = "line 2 edited by someone else\n"  # outside edit on line 2
        (self.repo / "shared.txt").write_text("".join(lines))
        return lines

    def test_shared_claim_allows_edit_beside_outside_hunk(self):
        lines = self.shared_file()
        code, out = guard(self.repo, "start", "--shared", "shared.txt")
        self.assertEqual(code, 0, out)
        lines[7] = "line 8 edited by this run\n"
        (self.repo / "shared.txt").write_text("".join(lines))
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 0, out)
        self.assertIn("changed: shared.txt", out)

    def test_shared_claim_flags_edit_to_outside_hunk(self):
        lines = self.shared_file()
        self.assertEqual(guard(self.repo, "start", "--shared", "shared.txt")[0], 0)
        lines[1] = "overwrote someone else's line\n"
        (self.repo / "shared.txt").write_text("".join(lines))
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 1)
        self.assertIn("shared.txt (line 2", out)

    def test_shared_claim_allows_insert_adjacent_to_outside_hunk(self):
        # Field report 3, D4: another session's uncommitted section is followed by this run's
        # new section. The protected lines stay byte-identical, but difflib may align the
        # insert inside the protected span; that must not count as changing the outside edit.
        base = ["# Roadmap\n", "\n", "## A\n", "| A | row |\n", "\n", "## Z\n", "| Z | row |\n"]
        (self.repo / "reg.md").write_text("".join(base))
        sh(self.repo, "git", "add", "reg.md")
        sh(self.repo, "git", "commit", "-qm", "reg")
        theirs = base[:5] + ["\n", "## B\n", "| B | row |\n"] + base[5:]
        (self.repo / "reg.md").write_text("".join(theirs))
        self.assertEqual(guard(self.repo, "start", "--shared", "reg.md")[0], 0)
        mine = theirs[:5] + ["\n", "## C\n", "| C | row |\n"] + theirs[5:]
        (self.repo / "reg.md").write_text("".join(mine))
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 0, out)
        # Splitting the outside section is still a violation.
        split = theirs[:7] + ["| C | wedged |\n"] + theirs[7:]
        (self.repo / "reg.md").write_text("".join(split))
        code, out = guard(self.repo, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("reg.md (line", out)

    def test_repeated_list_flags_accumulate(self):
        # Field report 3, D1: --adopt a --adopt b kept only b, and --write-set x --write-set y only y.
        (self.repo / "src" / "a.py").write_text("a = 2\n")
        (self.repo / "src" / "b.py").write_text("b = 2\n")
        code, out = guard(self.repo, "start", "--write-set", "src/", "--write-set", "README.md",
                          "--adopt", "src/a.py", "--adopt", "src/b.py")
        self.assertEqual(code, 0, out)
        self.assertIn("write set: src/, README.md", out)

    def test_report_shows_check_argv_with_quoting(self):
        # Field report 3, D3: the report joined argv with spaces, so a quoted argument read as
        # several words and the report did not show what actually ran.
        guard(self.repo, "start", "--write-set", "src/")
        guard(self.repo, "checks", "--each", f"""spaced :: "{sys.executable}" -c 'print("a b")'""")
        out = guard(self.repo, "report")[1]
        self.assertIn("""'print("a b")'""", out)

    def test_two_workers_may_share_a_file_but_not_an_exclusive_claim(self):
        self.assertEqual(guard(self.repo, "start", "--shared", "README.md", "--label", "WP-1")[0], 0)
        self.assertEqual(guard(self.repo, "start", "--shared", "README.md", "--label", "WP-2")[0], 0)
        self.assertEqual(guard(self.repo, "start", "--write-set", "README.md", "--label", "WP-3")[0], 3)

    def hook(self, event, *flags):
        result = subprocess.run([sys.executable, str(GUARD), "hook", *flags], cwd=self.repo,
                                input=__import__("json").dumps({"cwd": str(self.repo), **event}),
                                capture_output=True, text=True)
        return result.returncode, result.stderr

    def test_hook_blocks_edit_outside_write_set(self):
        guard(self.repo, "start", "--write-set", "src/")
        inside = {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                  "tool_input": {"file_path": str(self.repo / "src" / "a.py")}}
        outside = {"hook_event_name": "PreToolUse", "tool_name": "Write",
                   "tool_input": {"file_path": str(self.repo / "README.md")}}
        self.assertEqual(self.hook(inside)[0], 0)
        code, err = self.hook(outside)
        self.assertEqual(code, 2)
        self.assertIn("outside this run's write set", err)

    def test_hook_require_run_blocks_unguarded_edits(self):
        event = {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                 "tool_input": {"file_path": str(self.repo / "src" / "a.py")}}
        self.assertEqual(self.hook(event)[0], 0)
        code, err = self.hook(event, "--require-run")
        self.assertEqual(code, 2)
        self.assertIn("no guarded run is open", err)

    def test_hook_stop_requires_checks_and_clean_scope(self):
        guard(self.repo, "start", "--write-set", "src/")
        code, err = self.hook({"hook_event_name": "Stop"})
        self.assertEqual(code, 2)
        self.assertIn("no checks were run", err)
        self.assertEqual(self.hook({"hook_event_name": "Stop", "stop_hook_active": True})[0], 0)
        guard(self.repo, "exec", "--", sys.executable, "-c", "pass")
        self.assertEqual(self.hook({"hook_event_name": "Stop"})[0], 0)
        guard(self.repo, "finish")
        self.assertEqual(self.hook({"hook_event_name": "Stop"})[0], 0)

    def test_outside_git_is_an_environment_error(self):
        plain = Path(self.tmp.name) / "plain"
        plain.mkdir()
        code, out = guard(plain, "start", "--write-set", "x")
        self.assertEqual(code, 2)
        self.assertIn("not inside a git repository", out)


if __name__ == "__main__":
    unittest.main()
