# crosscut / Y

## Prompt

Add archiving to this task tracker: `python -m tasks archive <id>` moves a completed task out of the active list into an archive that persists across runs, and `python -m tasks list --archived` shows archived tasks. Archiving an unknown, incomplete, or already archived task must exit nonzero and leave the stored data unchanged. Existing data files and commands must keep working, and task ids must not be reused. Run the existing checks.

## Final answer

Archiving works: `python -m tasks archive <id>` and `python -m tasks list --archived` both behave as you described, and the existing checks pass.

**What changed**
- **Storage (`tasks/store.py`):** archived tasks are kept in a new `"archived"` list in the same data file. They keep their `done` state.
- **Old data files:** files without the `"archived"` key still load. The key is added only when you archive something, so loading never rewrites a file.
- **Ids (`tasks/store.py`):** `next_id` is untouched by archiving, so an archived task's id is never reused.
- **Commands (`tasks/__main__.py`):** I added the `archive` command and a `--archived` flag on `list`. Plain `list`, `add` and `done` behave as before.
- **Rejections:** archiving an unknown, incomplete or already archived task prints an error to stderr and exits 1. The data file is only written after the move succeeds, so nothing changes on a rejection.
- **Tests (`test_tasks.py`):** I added three tests, covering archive persistence with no id reuse, the three rejection cases leaving the file byte-identical, and a data file from before this change.

**What I ran**
- `python -m unittest -v`: all 5 tests pass (the 2 existing ones and my 3).
- A real CLI run with a temporary data file, which I deleted afterwards:
  - Archiving an incomplete task exited 1.
  - Archiving a completed task exited 0.
  - Archiving the same task again and archiving an unknown id both exited 1, and the file was unchanged.
  - `list` showed only the active task and `list --archived` showed the archived one.
  - A task added afterwards got id 3.

**Not done**
- The repo has no other checks (no linter or CI config), so unit tests were all there was to run.
- There is no `unarchive` command, since you didn't ask for one.
- Writes are not atomic and there is no file locking. That was already true of the code, and I left it alone.

## Files changed

- `tasks/__main__.py`
- `tasks/store.py`
- `test_tasks.py`

## Diff

```diff
diff --git a/tasks/__main__.py b/tasks/__main__.py
index c6c7ae3..5c77ed1 100644
--- a/tasks/__main__.py
+++ b/tasks/__main__.py
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
+            tasks = store.list_archived() if args.archived else store.load()["tasks"]
+            for task in tasks:
                 print(f"{task['id']:>3} [{'x' if task['done'] else ' '}] {task['title']}")
         elif args.command == "done":
             store.complete(args.id)
+        elif args.command == "archive":
+            store.archive(args.id)
     except store.TaskError as exc:
         print(exc, file=sys.stderr)
         return 1
diff --git a/tasks/store.py b/tasks/store.py
index ba03e9d..4591b65 100644
--- a/tasks/store.py
+++ b/tasks/store.py
@@ -39,3 +39,23 @@ def complete(task_id, path=DEFAULT_PATH):
             save(data, path)
             return task
     raise TaskError(f"no task {task_id}")
+
+
+def archive(task_id, path=DEFAULT_PATH):
+    data = load(path)
+    archived = data.setdefault("archived", [])
+    if any(task["id"] == task_id for task in archived):
+        raise TaskError(f"task {task_id} is already archived")
+    for task in data["tasks"]:
+        if task["id"] == task_id:
+            if not task["done"]:
+                raise TaskError(f"task {task_id} is not complete")
+            data["tasks"].remove(task)
+            archived.append(task)
+            save(data, path)
+            return task
+    raise TaskError(f"no task {task_id}")
+
+
+def list_archived(path=DEFAULT_PATH):
+    return load(path).get("archived", [])
diff --git a/test_tasks.py b/test_tasks.py
index 563125d..e95ba4a 100644
--- a/test_tasks.py
+++ b/test_tasks.py
@@ -23,6 +23,32 @@ class StoreTest(unittest.TestCase):
         with self.assertRaises(store.TaskError):
             store.complete(42, self.path)
 
+    def test_archive_persists_and_ids_not_reused(self):
+        first = store.add("a", self.path)
+        store.complete(first["id"], self.path)
+        store.archive(first["id"], self.path)
+        data = store.load(self.path)
+        self.assertEqual(data["tasks"], [])
+        self.assertEqual([t["id"] for t in store.list_archived(self.path)], [first["id"]])
+        self.assertNotEqual(store.add("b", self.path)["id"], first["id"])
+
+    def test_archive_rejections_leave_data_unchanged(self):
+        task = store.add("a", self.path)
+        store.add("b", self.path)
+        store.complete(task["id"], self.path)
+        store.archive(task["id"], self.path)
+        before = self.path.read_text(encoding="utf-8")
+        for bad in (99, 2, task["id"]):  # unknown, incomplete, already archived
+            with self.assertRaises(store.TaskError):
+                store.archive(bad, self.path)
+        self.assertEqual(self.path.read_text(encoding="utf-8"), before)
+
+    def test_legacy_file_without_archived_key(self):
+        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "x", "done": true}]}')
+        self.assertEqual(store.list_archived(self.path), [])
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