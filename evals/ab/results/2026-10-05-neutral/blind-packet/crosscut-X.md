# crosscut / X

## Prompt

Add archiving to this task tracker: `python -m tasks archive <id>` moves a completed task out of the active list into an archive that persists across runs, and `python -m tasks list --archived` shows archived tasks. Archiving an unknown, incomplete, or already archived task must exit nonzero and leave the stored data unchanged. Existing data files and commands must keep working, and task ids must not be reused. Run the existing checks.

## Final answer

`python -m tasks archive <id>` and `python -m tasks list --archived` now work. The existing checks pass, and so do the three tests I added. I also ran the CLI by hand.

- **Archiving:** it moves a completed task from the active list into a separate `archived` list in the same data file, so it persists across runs.
- **Bad ids:** an unknown, incomplete, or already archived task prints an error and exits 1. Each of these checks happens before anything is written, so the file is unchanged. A test confirms the file contents are identical after those failures.
- **Existing data files:** files without an `archived` list still load, and the list is added the first time something is archived. A test covers a file in the old format.
- **Id reuse:** new ids still come from the stored `next_id` counter, which archiving doesn't touch. A test checks that a new task gets id 3 after the first is archived.
- **Manual run:** in a manual run, archiving a not-yet-done task failed with exit 1. After `done 1`, archiving succeeded, and a second archive failed. `list` showed only the active task and `list --archived` showed only the archived one.

I didn't use the `[skill]` skill. The change was small enough to do directly. The edits are in `tasks/store.py`, `tasks/__main__.py` and `test_tasks.py`.

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
index ba03e9d..8bd5cde 100644
--- a/tasks/store.py
+++ b/tasks/store.py
@@ -1,4 +1,5 @@
-"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...]}."""
+"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...], "archived": [...]}.
+"archived" is absent in older files. Ids come from next_id and are never reused."""
 import json
 import os
 from pathlib import Path
@@ -12,9 +13,11 @@ class TaskError(Exception):
 
 def load(path=DEFAULT_PATH):
     if not Path(path).exists():
-        return {"next_id": 1, "tasks": []}
+        return {"next_id": 1, "tasks": [], "archived": []}
     with open(path, encoding="utf-8") as handle:
-        return json.load(handle)
+        data = json.load(handle)
+    data.setdefault("archived", [])
+    return data
 
 
 def save(data, path=DEFAULT_PATH):
@@ -39,3 +42,18 @@ def complete(task_id, path=DEFAULT_PATH):
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
index 563125d..ea6b8b4 100644
--- a/test_tasks.py
+++ b/test_tasks.py
@@ -23,6 +23,35 @@ class StoreTest(unittest.TestCase):
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
+        b = store.add("b", self.path)
+        store.complete(b["id"], self.path)
+        store.archive(b["id"], self.path)
+        before = self.path.read_text(encoding="utf-8")
+        for task_id in (a["id"], b["id"], 99):
+            with self.assertRaises(store.TaskError):
+                store.archive(task_id, self.path)
+        self.assertEqual(self.path.read_text(encoding="utf-8"), before)
+
+    def test_legacy_file_without_archived(self):
+        self.path.write_text(
+            '{"next_id": 2, "tasks": [{"id": 1, "title": "x", "done": true}]}',
+            encoding="utf-8",
+        )
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