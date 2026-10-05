"""Hidden acceptance checks for archiving; each command runs in a new process."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

failures = []
scratch = Path(tempfile.mkdtemp())
data_file = scratch / "tasks.json"
env = {**os.environ, "TASKS_FILE": str(data_file)}


def cli(*args):
    return subprocess.run([sys.executable, "-m", "tasks", *args], capture_output=True, text=True, env=env)


def expect(cond, message):
    if not cond:
        failures.append(message)


# A data file written by the current version must keep working.
legacy = {"next_id": 4, "tasks": [
    {"id": 1, "title": "old done", "done": True},
    {"id": 2, "title": "old open", "done": False},
    {"id": 3, "title": "another done", "done": True}]}
data_file.write_text(json.dumps(legacy, indent=2), encoding="utf-8")

listing = cli("list")
expect(listing.returncode == 0 and "old open" in listing.stdout, f"legacy file no longer lists: {listing.stdout!r} {listing.stderr!r}")

archived = cli("archive", "1")
expect(archived.returncode == 0, f"archive of a completed task failed: {archived.stderr!r}")
active = cli("list").stdout
expect("old done" not in active and "old open" in active, f"archived task still active or active task lost: {active!r}")
shown = cli("list", "--archived")
expect(shown.returncode == 0 and "old done" in shown.stdout and "old open" not in shown.stdout,
       f"list --archived wrong: {shown.stdout!r} {shown.stderr!r}")

before = data_file.read_bytes()
incomplete = cli("archive", "2")
expect(incomplete.returncode != 0, "archiving an incomplete task succeeded")
expect(data_file.read_bytes() == before, "archiving an incomplete task changed the data file")
unknown = cli("archive", "99")
expect(unknown.returncode != 0, "archiving an unknown task succeeded")
expect(data_file.read_bytes() == before, "archiving an unknown task changed the data file")
again = cli("archive", "1")
expect(again.returncode != 0 and data_file.read_bytes() == before, "archiving an already archived task succeeded or changed data")

new_id = cli("add", "fresh").stdout.strip()
expect(new_id == "4", f"ids changed after archiving: got {new_id!r}, expected '4'")
cli("done", "3")
cli("archive", "3")
shown = cli("list", "--archived").stdout
expect("old done" in shown and "another done" in shown, f"archive lost entries across runs: {shown!r}")

suite = subprocess.run([sys.executable, "-m", "unittest", "-q"], capture_output=True, text=True)
expect(suite.returncode == 0, "existing unittest suite fails")

print("\n".join(failures) or "all hidden checks passed")
sys.exit(1 if failures else 0)
