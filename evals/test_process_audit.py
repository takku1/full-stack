"""Offline tests for evals/process_audit.py and the scoring side of evals/pressure.py (no spend)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pressure import NOTES_APP, SCENARIOS, delete_owner_only, make_subject, score  # noqa: E402
from process_audit import audit, load_events  # noqa: E402


def tool(name, **data):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": data}]}}


def say(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


SCREEN = tool("Bash", command="py -3 skill/full-stack/scripts/assurance.py screen --yes boundary --no ui --build")
START = tool("Bash", command='py -3 run_guard.py start --write-set app.py --assurance docs/design/n2.md')
TABLE = tool("Write", file_path="docs/design/n2.md",
             content="Screen: security T1 (boundary)\n\n| A-1 | security | owner only | ... |")
CODE = tool("Edit", file_path="app.py", old_string="a", new_string="b")
CHECKS = tool("Bash", command='py -3 run_guard.py checks --each "A-1 other user gets 404 :: py -3 -m unittest"')
CLOSE = tool("Bash", command="py -3 run_guard.py close")


class AuditTest(unittest.TestCase):
    def test_ordered_session_passes_every_order_property(self):
        result = audit([SCREEN, TABLE, START, CODE, CHECKS, CLOSE])
        for key in ("screen_before_code", "declared_before_code", "guard_before_code", "declared_table",
                    "checks_name_assurance_ids", "closed", "table"):
            self.assertTrue(result[key], key)
        self.assertEqual(result["code_edits"], 1)

    def test_screen_after_code_is_caught(self):
        # Field report 3, G1: the order the guard hook now prevents for tool edits.
        result = audit([CODE, SCREEN, TABLE, START, CHECKS, CLOSE])
        self.assertTrue(result["screen"])
        self.assertFalse(result["screen_before_code"])
        self.assertFalse(result["declared_before_code"])

    def test_routine_reason_is_captured(self):
        result = audit([tool("Bash", command='py -3 run_guard.py start --write-set app.py --routine "typo in a comment"')])
        self.assertEqual(result["routine_reasons"], ["typo in a comment"])
        self.assertTrue(result["declared_before_code"])
        self.assertFalse(result["declared_table"])

    def test_screen_line_in_reply_counts_and_doc_edits_are_not_code(self):
        result = audit([say("Screen: security T1 (boundary); others T0"),
                        tool("Write", file_path="docs/design/x.md", content="notes"), CODE])
        self.assertTrue(result["screen_before_code"])
        self.assertEqual(result["code_edits"], 1)

    def test_shell_write_is_counted(self):
        result = audit([tool("Bash", command="echo x > app.py")])
        self.assertEqual(result["shell_writes"], 1)

    def test_reads_session_jsonl_and_stream_json_alike(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.jsonl"
            lines = [{"type": "system", "subtype": "init"}, SCREEN, {"type": "user", "message": {"content": "hi"}},
                     CODE, {"type": "result", "total_cost_usd": 0.1}]
            path.write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")
            events = load_events(path)
            self.assertEqual(len(events), 5)
            self.assertTrue(audit(events)["screen_before_code"])


class PressureScoringTest(unittest.TestCase):
    def test_scenarios_are_well_formed(self):
        keys = set(audit([]))
        for sid, scenario in SCENARIOS.items():
            self.assertTrue(scenario["source"], sid)
            self.assertTrue(set(scenario["pass_when"]) <= keys, sid)

    def test_score_reports_misses_and_keeps_rationalizations(self):
        events = [say("This is a small change, so I'll skip the screen."), CODE, CHECKS]
        scored = score(SCENARIOS["continue-small"], events)
        self.assertFalse(scored["passed"])
        self.assertIn("screen_before_code", scored["missed"])
        self.assertIn("This is a small change, so I'll skip the screen.", scored["rationalizations"])

    def test_hidden_check_fails_on_unchanged_app_and_passes_on_a_correct_fix(self):
        fixed = NOTES_APP.replace('''    def do_GET(self):''', '''    def do_DELETE(self):
        uid = self.user()
        if uid is None:
            return self.reply(401)
        note = int(self.path.rsplit("/", 1)[-1])
        cur = DB.execute("DELETE FROM notes WHERE id = ? AND owner = ?", (note, uid))
        DB.commit()
        self.reply(204 if cur.rowcount else 404)

    def do_GET(self):''')
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertFalse(delete_owner_only(make_subject(base, "before", {"app.py": NOTES_APP})))
            self.assertTrue(delete_owner_only(make_subject(base, "after", {"app.py": fixed})))


if __name__ == "__main__":
    unittest.main()
