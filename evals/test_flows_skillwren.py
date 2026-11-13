"""Check full-stack's flow files with SkillWren's fragment checker, and prove the order rules bite.

SkillWren (Z:\\skillwren, format 0.6+) checks `logic` blocks embedded in Markdown with
`skillwren check --fragment`: definite binding, dismissal safety, order rules (P1), and more.
Each flow must be clean, and each one-break mutant (an order rule's earlier step removed,
moved, or made conditional) must be rejected, so a clean result means something.
Skipped when SkillWren is not importable.
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skill" / "full-stack"
FLOWS = ["design.md", "implement.md", "assurance.md", "stack.md"]


def _have_skillwren():
    try:
        import skillwren.validator  # noqa: F401
        return True
    except Exception:  # noqa: BLE001
        return False


HAVE_SKILLWREN = _have_skillwren()


def check(*paths):
    result = subprocess.run([sys.executable, "-m", "skillwren", "check", "--fragment", *map(str, paths)],
                            capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


MUTANTS = {
    # name: (file, old text, new text, expected rule)
    "implement: assurance gate removed": (
        "implement.md",
        "  verify design has a complete assurance table from table_check\n"
        "    otherwise:\n"
        "      apply assurance repair with design as design\n"
        "      write design with design_docs\n"
        "      exec assurance table check from scripts as table_check\n"
        "      retry\n", "", "P1"),
    "implement: code written before the guard starts": (
        "implement.md",
        "  write implementation with subject\n  apply check plan",
        "  apply check plan", "P1"),
    "design: screen made conditional (field report 3, G1)": (
        "design.md",
        "  run assurance from flows/assurance.md with:\n    scope = scope\n",
        "  if scope looks risky:\n    run assurance from flows/assurance.md with:\n      scope = scope\n", "P1"),
    "stack: final check dropped": (
        "stack.md",
        "  exec stack check from scripts as consistency\n"
        "  verify the committed profile is consistent from consistency\n"
        "    otherwise:\n"
        "      apply stack repair with records as records\n"
        "      write records with stack_file\n"
        "      exec stack check from scripts as consistency\n"
        "      retry\n", "", "P1"),
    "assurance: table returned unchecked": (
        "assurance.md",
        "  exec assurance table check from scripts as table_check\n"
        "  verify the table has no gaps from table_check\n"
        "    otherwise:\n"
        "      apply table repair with table as table\n"
        "      write table with design_docs\n"
        "      exec assurance table check from scripts as table_check\n"
        "      retry\n", "", "P1"),
}


@unittest.skipUnless(HAVE_SKILLWREN, "SkillWren not importable; fragment checks skipped")
class FlowFragmentTest(unittest.TestCase):
    def test_every_flow_is_clean_without_warnings(self):
        code, out = check(*(SKILL / "flows" / f for f in FLOWS))
        self.assertEqual(code, 0, out)
        self.assertNotIn("warning", out, out)
        self.assertNotIn("error", out, out)

    def test_one_break_mutants_are_rejected(self):
        for name, (flow, old, new, rule) in MUTANTS.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp) / "full-stack"
                shutil.copytree(SKILL, skill, ignore=shutil.ignore_patterns("__pycache__"))
                path = skill / "flows" / flow
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.count(old), 1, f"{name}: mutation anchor not found once")
                path.write_text(text.replace(old, new), encoding="utf-8")
                code, out = check(path)
                self.assertNotEqual(code, 0, f"{name}: mutant passed\n{out}")
                self.assertIn(f"error {rule}", out, f"{name}\n{out}")

    def test_authorization_precedes_every_mutation(self):
        # Dismissal safety (M1): moving the ask after a write must fail.
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "full-stack"
            shutil.copytree(SKILL, skill, ignore=shutil.ignore_patterns("__pycache__"))
            path = skill / "flows" / "stack.md"
            text = path.read_text(encoding="utf-8")
            ask = ("  if candidates include a costly-to-reverse commitment not already authorized:\n"
                   "    show candidates\n"
                   "    ask user to authorize each costly-to-reverse commitment as authorization\n"
                   "    apply conditional mark with authorization as candidates\n\n")
            self.assertEqual(text.count(ask), 1)
            text = text.replace(ask, "").replace("  apply profile choice with profiles as profile\n",
                                                 "  apply profile choice with profiles as profile\n" + ask)
            path.write_text(text, encoding="utf-8")
            code, out = check(path)
            self.assertNotEqual(code, 0, out)
            self.assertIn("error M1", out)


if __name__ == "__main__":
    unittest.main()
