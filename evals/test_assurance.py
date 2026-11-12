"""Exercise skill/full-stack/scripts/assurance.py (screen resolver and table check)."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skill" / "full-stack"
SCRIPT = SKILL / "scripts" / "assurance.py"
RULES = json.loads((SKILL / "rules" / "assurance.json").read_text(encoding="utf-8"))
QUESTIONS = list(RULES["questions"])


def run(*args):
    result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def screen(yes=(), unknown=(), high=(), build=False):
    no = [q for q in QUESTIONS if q not in yes and q not in unknown]
    args = ["screen", "--json", "--no", *no]
    if yes:
        args += ["--yes", *yes]
    if unknown:
        args += ["--unknown", *unknown]
    if high:
        args += ["--high", *high]
    if build:
        args.append("--build")
    code, out = run(*args)
    assert code == 0, out
    return {d["discipline"]: d for d in json.loads(out)["disciplines"]}


class ScreenTest(unittest.TestCase):
    def test_local_tool_raises_nothing_without_build(self):
        result = screen()
        self.assertTrue(all(d["tier"] == 0 for d in result.values()))

    def test_build_always_raises_verification(self):
        result = screen(build=True)
        self.assertEqual(result["verification"]["tier"], 1)
        self.assertEqual(result["verification"]["because"], ["build"])

    def test_multi_tenant_web_app(self):
        result = screen(yes=["boundary", "tenants"], build=True)
        self.assertEqual(result["security"]["tier"], 1)
        self.assertEqual(result["security"]["because"], ["boundary", "tenants"])
        self.assertEqual(result["observability"]["tier"], 1)
        self.assertEqual(result["privacy"]["tier"], 0)

    def test_dependencies_follow_from_rules(self):
        # privacy requires security; performance requires observability
        result = screen(yes=["personal_data"])
        self.assertEqual(result["security"]["tier"], 1)
        self.assertEqual(screen(yes=["slo"])["observability"]["tier"], 1)

    def test_implicit_risk_capabilities_raise_security(self):
        # FS-016 screen-recall case: a local tool that runs untrusted plugins or reads confidential files.
        self.assertEqual(screen(yes=["untrusted_code"])["security"]["tier"], 1)
        self.assertEqual(screen(yes=["confidential"])["security"]["tier"], 1)

    def test_unknown_counts_as_yes(self):
        self.assertEqual(screen(unknown=["money"])["reliability"]["tier"], 1)

    def test_tier_two_only_for_raised_disciplines(self):
        result = screen(yes=["money"], high=["security", "ux"])
        self.assertEqual(result["security"]["tier"], 2)
        self.assertEqual(result["ux"]["tier"], 0)
        result = screen(yes=["money"], high=["all"])
        self.assertEqual(result["reliability"]["tier"], 2)

    def test_every_question_must_be_answered(self):
        code, out = run("screen", "--yes", "boundary")
        self.assertEqual(code, 2)
        self.assertIn("unanswered", out)
        code, out = run("screen", "--yes", "nonsense", "--no", *QUESTIONS)
        self.assertEqual(code, 2)
        self.assertIn("unknown question: nonsense", out)

    def test_text_output_is_a_screen_line_and_load_list(self):
        no = [q for q in QUESTIONS if q != "boundary"]
        code, out = run("screen", "--yes", "boundary", "--no", *no, "--build")
        self.assertEqual(code, 0, out)
        self.assertIn("Screen: security T1 (boundary); verification T1 (build); observability T1 (boundary)", out)
        self.assertIn("Load: assurance/security.md, assurance/verification.md, assurance/observability.md", out)

    def test_rules_cover_every_discipline_module(self):
        modules = {p.stem for p in (SKILL / "assurance").glob("*.md")}
        self.assertEqual(set(RULES["disciplines"]), modules)
        raised = {d for q in RULES["questions"].values() for d in q["raises"]}
        self.assertTrue(raised <= modules)

    def test_flow_screen_table_matches_rules(self):
        flow = (SKILL / "flows" / "assurance.md").read_text(encoding="utf-8")
        for qid, q in RULES["questions"].items():
            self.assertIn(f"| `{qid}` {q['ask']} | {', '.join(q['raises'])} |", flow, qid)


class CheckTest(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "design.md"
            path.write_text(text, encoding="utf-8")
            return run("check", str(path))

    HEADER = ("Screen: security T2 (money); verification T1 (build); others T0\n\n"
              "| ID | Discipline | Claim | Could fail by | Control (owner) | Check | Evidence |\n"
              "|---|---|---|---|---|---|---|\n")

    def test_complete_table_passes_and_lists_untested_tier_two(self):
        code, out = self.check(self.HEADER
                               + "| A-1 | security | no double charge | retry | key (data) | `test_replay` | unknown |\n"
                               + "| A-2 | verification | paths run | skip | probe (tests) | test_paths | tested |\n")
        self.assertEqual(code, 0, out)
        self.assertIn("pending: A-1: tier 2 claim not yet tested", out)

    def test_gaps_are_reported(self):
        code, out = self.check(self.HEADER
                               + "| A-1 | security | no double charge | retry | key (data) | — | unknown |\n"
                               + "| A-1 | ux | labels | none | form (client) | axe | unknown |\n")
        self.assertEqual(code, 1, out)
        self.assertIn("A-1: no check", out)
        self.assertIn("A-1: duplicate ID", out)
        self.assertIn("discipline ux is not raised", out)
        self.assertIn("verification is raised to T1 but has no row", out)

    def test_missing_screen_line_is_a_gap(self):
        code, out = self.check("| A-1 | security | c | f | x (y) | t | tested |\n")
        self.assertEqual(code, 1)
        self.assertIn("no 'Screen:' line", out)


if __name__ == "__main__":
    unittest.main()
