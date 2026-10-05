# crosscut / Z

## Prompt

Add archiving to this task tracker: `python -m tasks archive <id>` moves a completed task out of the active list into an archive that persists across runs, and `python -m tasks list --archived` shows archived tasks. Archiving an unknown, incomplete, or already archived task must exit nonzero and leave the stored data unchanged. Existing data files and commands must keep working, and task ids must not be reused. Run the existing checks.

## Final answer

Archiving is implemented and the existing tests pass, but I couldn't run the CLI by hand. The sandbox blocked the shell commands I tried for it (the ones using `$?` and env vars). The CLI wiring (`archive` subcommand, `list --archived`) is therefore untested end to end.

Test results: `python -m unittest` ran 5 tests, all OK. That is the two existing tests plus three new ones. The new tests cover the store logic only, not the command line.

- **Storage:** the data file gets an `archived` list next to `tasks`. `next_id` is never lowered, so archived ids are not reused. Files from before this change have no `archived` key; `load()` adds an empty one, and old files keep working unchanged.
- **`store.archive(id)`:** moves a completed task from `tasks` to `archived` and saves. It raises `TaskError` for an unknown id, an incomplete task, or an already-archived task. All the checks happen before `save()`, so a failed archive writes nothing, and the CLI exits 1 for these errors as it already does for `done`.
- **CLI:** `python -m tasks archive <id>` and `python -m tasks list --archived`.
- **Tests:** `test_tasks.py` now covers a successful archive, id non-reuse, the three error cases leaving the file byte-identical, and loading an old-format file.

The changes are in `tasks/store.py`, `tasks/__main__.py` and `test_tasks.py`, and nothing is committed.

## Files changed

- `tasks/__main__.py`
- `tasks/store.py`
- `test_tasks.py`

## Diff

```diff
diff --git a/tasks/__main__.py b/tasks/__main__.py
index c6c7ae3..49a2a89 100644
--- a/tasks/__main__.py
+++ b/tasks/__main__.py
@@ -1,4 +1,4 @@
-"""python -m tasks add TITLE | list | done ID"""
+"""python -m tasks add TITLE | list | done ID | archive ID | list --archived"""
 import argparse
 import sys
 
@@ -9,17 +9,21 @@ def main(argv=None):
     parser = argparse.ArgumentParser(prog="tasks")
     sub = parser.add_subparsers(dest="command", required=True)
     sub.add_parser("add").add_argument("title")
-    sub.add_parser("list")
+    sub.add_parser("list").add_argument("--archived", action="store_true")
     sub.add_parser("done").add_argument("id", type=int)
+    sub.add_parser("archive").add_argument("id", type=int)
     args = parser.parse_args(argv)
     try:
         if args.command == "add":
             print(store.add(args.title)["id"])
         elif args.command == "list":
-            for task in store.load()["tasks"]:
+            data = store.load()
+            for task in data["archived" if args.archived else "tasks"]:
                 print(f"{task['id']:>3} [{'x' if task['done'] else ' '}] {task['title']}")
         elif args.command == "done":
             store.complete(args.id)
+        elif args.command == "archive":
+            store.archive(args.id)
     except store.TaskError as exc:
         print(exc, file=sys.stderr)
         return 1
diff --git a/tasks/store.py b/tasks/store.py
index ba03e9d..4a9d1c9 100644
--- a/tasks/store.py
+++ b/tasks/store.py
@@ -1,4 +1,8 @@
-"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...]}."""
+"""JSON file storage for tasks.
+
+Data file format: {"next_id": int, "tasks": [...], "archived": [...]}.
+"archived" is optional in older files. next_id never decreases, so ids are not reused.
+"""
 import json
 import os
 from pathlib import Path
@@ -12,9 +16,11 @@ class TaskError(Exception):
 
 def load(path=DEFAULT_PATH):
     if not Path(path).exists():
-        return {"next_id": 1, "tasks": []}
+        return {"next_id": 1, "tasks": [], "archived": []}
     with open(path, encoding="utf-8") as handle:
-        return json.load(handle)
+        data = json.load(handle)
+    data.setdefault("archived", [])  # absent in files written before archiving
+    return data
 
 
 def save(data, path=DEFAULT_PATH):
@@ -39,3 +45,18 @@ def complete(task_id, path=DEFAULT_PATH):
             save(data, path)
             return task
     raise TaskError(f"no task {task_id}")
+
+
+def archive(task_id, path=DEFAULT_PATH):
+    data = load(path)
+    if any(task["id"] == task_id for task in data["archived"]):
+        raise TaskError(f"task {task_id} is already archived")
+    for task in data["tasks"]:
+        if task["id"] == task_id:
+            if not task["done"]:
+                raise TaskError(f"task {task_id} is not complete")
+            data["tasks"].remove(task)
+            data["archived"].append(task)
+            save(data, path)
+            return task
+    raise TaskError(f"no task {task_id}")
diff --git a/test_tasks.py b/test_tasks.py
index 563125d..37643c5 100644
--- a/test_tasks.py
+++ b/test_tasks.py
@@ -23,6 +23,32 @@ class StoreTest(unittest.TestCase):
         with self.assertRaises(store.TaskError):
             store.complete(42, self.path)
 
+    def test_archive(self):
+        a = store.add("a", self.path)
+        b = store.add("b", self.path)
+        store.complete(a["id"], self.path)
+        store.archive(a["id"], self.path)
+        data = store.load(self.path)
+        self.assertEqual([t["id"] for t in data["tasks"]], [b["id"]])
+        self.assertEqual([t["id"] for t in data["archived"]], [a["id"]])
+        self.assertEqual(store.add("c", self.path)["id"], 3)
+
+    def test_archive_errors_leave_data_unchanged(self):
+        a = store.add("a", self.path)
+        store.add("b", self.path)
+        store.complete(a["id"], self.path)
+        store.archive(a["id"], self.path)
+        before = self.path.read_text()
+        for bad in (a["id"], 2, 99):  # archived, incomplete, unknown
+            with self.assertRaises(store.TaskError):
+                store.archive(bad, self.path)
+        self.assertEqual(self.path.read_text(), before)
+
+    def test_old_file_without_archived(self):
+        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "x", "done": true}]}')
+        store.archive(1, self.path)
+        self.assertEqual(store.load(self.path)["next_id"], 2)
+
 
 if __name__ == "__main__":
     unittest.main()

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```