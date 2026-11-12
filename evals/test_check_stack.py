"""Exercise skill/full-stack/scripts/check_stack.py on small stack files."""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "full-stack" / "scripts" / "check_stack.py"
STACK_FLOW = ROOT / "skill" / "full-stack" / "flows" / "stack.md"


def run(path, *args):
    result = subprocess.run([sys.executable, str(SCRIPT), *args, str(path)], capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def layer(status="accepted", choice="x", provides=(), assumes=None, novel=False, candidates=None):
    out = {"status": status, "choice": choice, "provides": list(provides), "assumes": assumes or {}, "novel": novel}
    if candidates is not None:
        out["candidates"] = candidates
    else:
        out["candidates"] = [{"name": choice, "provides": list(provides)}, {"name": "alt"}]
    return out


class CheckStackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, stack, name="stack.json"):
        path = self.dir / name
        path.write_text(json.dumps(stack), encoding="utf-8")
        return path

    def test_consistent_profile_passes(self):
        path = self.write({"brief": {"tags": []}, "layers": {
            "data": layer(provides=["transactional-writes"], assumes={"runtime": ["python"]}),
            "runtime": layer(provides=["python"]),
        }})
        code, out = run(path, "check")
        self.assertEqual(code, 0, out)
        self.assertIn("0 errors", out)

    def test_unmet_assumption_fails(self):
        path = self.write({"layers": {
            "data": layer(assumes={"runtime": ["postgres-driver"]}),
            "runtime": layer(provides=["python"]),
        }})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("postgres-driver", out)

    def test_assumption_on_undeclared_layer_fails(self):
        path = self.write({"layers": {"data": layer(assumes={"interface": ["sync-capable"]})}})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("undeclared layer 'interface'", out)

    def test_conditional_layer_downgrades_unmet_assumption(self):
        path = self.write({"layers": {
            "data": layer(status="conditional", assumes={"runtime": ["postgres-driver"]}),
            "runtime": layer(provides=["python"]),
        }})
        code, out = run(path, "check")
        self.assertEqual(code, 0, out)
        self.assertIn("warning data assumes", out)

    def test_seed_exclude_rule_fires(self):
        path = self.write({"layers": {
            "data": layer(provides=["embedded-single-writer"]),
            "platform": layer(provides=["horizontally-scaled-instances"]),
        }})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("R-002", out)

    def test_brief_tag_rule_requires_declared_layer(self):
        path = self.write({"brief": {"tags": ["user-accounts"]}, "layers": {"data": layer()}})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("R-009", out)
        self.assertIn("layer not declared", out)

    def test_innovation_budget(self):
        path = self.write({"brief": {"innovation_budget": 1}, "layers": {
            "data": layer(novel=True), "runtime": layer(novel=True)}})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("innovation budget", out)

    def test_affected_layer_without_decision(self):
        path = self.write({"brief": {"affected": ["data", "client"]}, "layers": {"data": layer()}})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("'client' has no decision", out)

    def test_project_local_rule_and_duplicate_ids(self):
        rule = {"id": "P-001", "when": {"runtime": ["python"]}, "excludes": {"data": ["x"]}, "why": "local"}
        path = self.write({"rules": [rule], "layers": {
            "data": layer(provides=["x"]), "runtime": layer(provides=["python"])}})
        code, out = run(path, "check")
        self.assertEqual(code, 1, out)
        self.assertIn("P-001", out)
        dup = self.write({"rules": [dict(rule, id="R-001")], "layers": {"data": layer()}}, "dup.json")
        code, out = run(dup, "check")
        self.assertEqual(code, 2, out)

    def test_profiles_intersects_candidate_sets(self):
        path = self.write({"brief": {"innovation_budget": 1}, "layers": {
            "data": {"status": "proposed", "candidates": [
                {"name": "sqlite", "provides": ["embedded-single-writer"]},
                {"name": "postgres", "provides": ["transactional-writes"], "assumes": {"runtime": ["pg-driver"]}},
            ]},
            "runtime": {"status": "proposed", "candidates": [
                {"name": "py", "provides": ["python", "pg-driver"]},
                {"name": "exotic", "provides": ["pg-driver"], "novel": True},
            ]},
            "platform": {"status": "keep-current", "choice": "k8s", "provides": ["horizontally-scaled-instances"]},
        }})
        code, out = run(path, "profiles", "--json")
        self.assertEqual(code, 0, out)
        result = json.loads(out)
        self.assertEqual(result["combinations"], 4)
        self.assertEqual(result["surviving"], 2)
        self.assertEqual(result["profiles"][0]["profile"], {"data": "postgres", "runtime": "py", "platform": "k8s"})
        self.assertTrue(any("R-002" in e["reason"] for e in result["eliminated_by"]))

    def test_profiles_none_survive(self):
        path = self.write({"layers": {
            "data": {"status": "proposed", "candidates": [{"name": "sqlite", "provides": ["embedded-single-writer"]}]},
            "platform": {"status": "keep-current", "provides": ["horizontally-scaled-instances"]},
        }})
        code, out = run(path, "profiles")
        self.assertEqual(code, 1, out)
        self.assertIn("0 of 1", out)

    def test_markdown_block_and_bad_input(self):
        md = self.dir / "design.md"
        md.write_text("# D\n\n```json stack\n" + json.dumps({"layers": {"data": layer()}}) + "\n```\n", encoding="utf-8")
        self.assertEqual(run(md, "check")[0], 0)
        bad = self.dir / "bad.md"
        bad.write_text("no block here\n", encoding="utf-8")
        self.assertEqual(run(bad, "check")[0], 2)
        status = self.write({"layers": {"data": {"status": "maybe"}}}, "status.json")
        self.assertEqual(run(status, "check")[0], 2)

    def test_stack_flow_example_is_consistent(self):
        text = STACK_FLOW.read_text(encoding="utf-8")
        match = re.search(r"## Stack block shape\s+```json\n(.*?)```", text, flags=re.S)
        assert match is not None, "stack.md lost its example block"
        path = self.write(json.loads(match.group(1)), "example.json")
        code, out = run(path, "check")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
