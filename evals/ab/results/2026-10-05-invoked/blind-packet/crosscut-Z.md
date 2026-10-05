# crosscut / Z

## Prompt

Add archiving to this task tracker: `python -m tasks archive <id>` moves a completed task out of the active list into an archive that persists across runs, and `python -m tasks list --archived` shows archived tasks. Archiving an unknown, incomplete, or already archived task must exit nonzero and leave the stored data unchanged. Existing data files and commands must keep working, and task ids must not be reused. Run the existing checks.

## Final answer

I added archiving, and the existing unit tests plus three new archive tests pass (5 in total). I couldn't run the CLI end to end because the shell blocked my smoke-test commands, so `python -m tasks archive <id>` and `list --archived` are untested from the command line.

- **Archive command:** `archive <id>` moves a completed task from the active list into a new `archived` list in the same data file. `list --archived` prints that list.
- **Failures:** archiving an unknown, incomplete, or already archived task raises an error and exits 1. These checks all run before anything is written, so the file stays unchanged. A new test confirms the file contents are identical afterward.
- **Existing data files:** files without an `archived` key still load, and it is created the first time you archive something. `add`, `list` and `done` are untouched. A new test archives from an old-format file.
- **Id reuse:** `next_id` is never lowered, so an archived task's id is not reused. A new test checks that the next task added gets the following id.

The changes are in `tasks/store.py`, `tasks/__main__.py` and `test_tasks.py`.

## Files changed

- `tasks/__main__.py`
- `tasks/store.py`
- `test_tasks.py`

## Diff

```diff
diff --git a/tasks/__main__.py b/tasks/__main__.py
index c6c7ae3..9da8f78 100644
--- a/tasks/__main__.py
+++ b/tasks/__main__.py
@@ -1,4 +1,4 @@
-"""python -m tasks add TITLE | list | done ID"""
+"""python -m tasks add TITLE | list [--archived] | done ID | archive ID"""
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
index ba03e9d..4daa037 100644
--- a/tasks/store.py
+++ b/tasks/store.py
@@ -1,4 +1,7 @@
-"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...]}."""
+"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...], "archived": [...]}.
+
+"archived" is optional in older files. next_id is never reduced, so ids of archived tasks are not reused.
+"""
 import json
 import os
 from pathlib import Path
@@ -12,9 +15,11 @@ class TaskError(Exception):
 
 def load(path=DEFAULT_PATH):
     if not Path(path).exists():
-        return {"next_id": 1, "tasks": []}
+        return {"next_id": 1, "tasks": [], "archived": []}
     with open(path, encoding="utf-8") as handle:
-        return json.load(handle)
+        data = json.load(handle)
+    data.setdefault("archived", [])  # files written before archiving existed
+    return data
 
 
 def save(data, path=DEFAULT_PATH):
@@ -39,3 +44,18 @@ def complete(task_id, path=DEFAULT_PATH):
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
index 563125d..0ad98f7 100644
--- a/test_tasks.py
+++ b/test_tasks.py
@@ -23,6 +23,31 @@ class StoreTest(unittest.TestCase):
         with self.assertRaises(store.TaskError):
             store.complete(42, self.path)
 
+    def test_archive(self):
+        task = store.add("old", self.path)
+        store.complete(task["id"], self.path)
+        store.archive(task["id"], self.path)
+        data = store.load(self.path)
+        self.assertEqual(data["tasks"], [])
+        self.assertEqual([t["id"] for t in data["archived"]], [task["id"]])
+        self.assertEqual(store.add("new", self.path)["id"], task["id"] + 1)
+
+    def test_archive_errors_leave_data_unchanged(self):
+        open_task = store.add("open", self.path)
+        done = store.add("done", self.path)
+        store.complete(done["id"], self.path)
+        store.archive(done["id"], self.path)
+        before = self.path.read_text(encoding="utf-8")
+        for task_id in (open_task["id"], done["id"], 99):
+            with self.assertRaises(store.TaskError):
+                store.archive(task_id, self.path)
+        self.assertEqual(self.path.read_text(encoding="utf-8"), before)
+
+    def test_legacy_file_without_archived(self):
+        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "t", "done": true}]}')
+        store.archive(1, self.path)
+        self.assertEqual(len(store.load(self.path)["archived"]), 1)
+
 
 if __name__ == "__main__":
     unittest.main()

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```