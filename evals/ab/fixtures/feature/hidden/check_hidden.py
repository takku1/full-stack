"""Hidden acceptance checks; copied in only after the session ends."""
import json
import os
import subprocess
import sys
import tempfile

PY = sys.executable
failures = []


def cli(*args):
    return subprocess.run([PY, "inventory.py", *args], capture_output=True, text=True)


# Exact output of the unmodified starter.
expected_text = "Bolt      120  A-100\nHex nut    75  B-220\nWasher      0  C-310\n"
text = cli("list")
if text.returncode != 0 or text.stdout != expected_text:
    failures.append(f"default text output changed: {text.stdout!r}")

data = json.load(open("items.json", encoding="utf-8"))
as_json = cli("list", "--json")
try:
    if as_json.returncode != 0 or json.loads(as_json.stdout) != data:
        failures.append(f"--json output does not equal the items in order: {as_json.stdout!r}")
except json.JSONDecodeError:
    failures.append(f"--json output is not JSON: {as_json.stdout!r}")

with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
    handle.write("[]")
empty = cli("list", "--json", "--file", handle.name)
os.unlink(handle.name)
try:
    if empty.returncode != 0 or json.loads(empty.stdout) != []:
        failures.append(f"--json on an empty file should print []: {empty.stdout!r}")
except json.JSONDecodeError:
    failures.append(f"--json on an empty file is not JSON: {empty.stdout!r}")

suite = subprocess.run([PY, "-m", "unittest", "-q"], capture_output=True, text=True)
if suite.returncode != 0:
    failures.append("existing unittest suite fails")

print("\n".join(failures) or "all hidden checks passed")
sys.exit(1 if failures else 0)
