# feature / X

## Prompt

Add a `--json` flag to `python inventory.py list` that prints the items as a JSON array in file order with the same fields. Keep the default text output exactly as it is, add no dependencies, keep the change local, and run the existing checks.

## Final answer

`python inventory.py list --json` now prints the items as a JSON array in file order, with every field exactly as it appears in the file. The existing text-listing test and a new JSON test both pass. A manual run of plain `list` printed the same table as before.

- **Code change:** in `inventory.py`, `list` gets a `--json` flag, and the usage docstring mentions it. The JSON is indented two spaces.
- **Test:** `test_json_listing` in `test_inventory.py` checks the JSON output equals the contents of `items.json`.
- **Scope:** no new dependencies, and nothing else was touched.
- **Empty list:** with `--json` it would print `[]` rather than the text output's "no items". I didn't test that case.

I didn't commit anything.

## Files changed

- `inventory.py`
- `test_inventory.py`

## Diff

```diff
diff --git a/inventory.py b/inventory.py
index b6e69a5..29df46d 100644
--- a/inventory.py
+++ b/inventory.py
@@ -1,31 +1,33 @@
-"""Tiny inventory CLI: python inventory.py list [--file PATH]"""
-import argparse
-import json
-import sys
-
-
-def load(path):
-    with open(path, encoding="utf-8") as handle:
-        return json.load(handle)
-
-
-def render(items):
-    if not items:
-        return "no items"
-    width = max(len(item["name"]) for item in items)
-    return "\n".join(f"{item['name']:<{width}}  {item['qty']:>4}  {item['sku']}" for item in items)
-
-
-def main(argv=None):
-    parser = argparse.ArgumentParser(prog="inventory")
-    sub = parser.add_subparsers(dest="command", required=True)
-    listing = sub.add_parser("list", help="list items")
-    listing.add_argument("--file", default="items.json")
-    args = parser.parse_args(argv)
-    if args.command == "list":
-        print(render(load(args.file)))
-    return 0
-
-
-if __name__ == "__main__":
-    sys.exit(main())
+"""Tiny inventory CLI: python inventory.py list [--file PATH] [--json]"""
+import argparse
+import json
+import sys
+
+
+def load(path):
+    with open(path, encoding="utf-8") as handle:
+        return json.load(handle)
+
+
+def render(items):
+    if not items:
+        return "no items"
+    width = max(len(item["name"]) for item in items)
+    return "\n".join(f"{item['name']:<{width}}  {item['qty']:>4}  {item['sku']}" for item in items)
+
+
+def main(argv=None):
+    parser = argparse.ArgumentParser(prog="inventory")
+    sub = parser.add_subparsers(dest="command", required=True)
+    listing = sub.add_parser("list", help="list items")
+    listing.add_argument("--file", default="items.json")
+    listing.add_argument("--json", action="store_true", help="print items as a JSON array")
+    args = parser.parse_args(argv)
+    if args.command == "list":
+        items = load(args.file)
+        print(json.dumps(items, indent=2) if args.json else render(items))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/test_inventory.py b/test_inventory.py
index f39cfbf..8526efc 100644
--- a/test_inventory.py
+++ b/test_inventory.py
@@ -1,24 +1,31 @@
-import contextlib
-import io
-import unittest
-
-import inventory
-
-
-def run(*argv):
-    out = io.StringIO()
-    with contextlib.redirect_stdout(out):
-        code = inventory.main(list(argv))
-    return code, out.getvalue()
-
-
-class ListTest(unittest.TestCase):
-    def test_text_listing(self):
-        code, out = run("list")
-        self.assertEqual(code, 0)
-        self.assertIn("Hex nut", out)
-        self.assertIn("C-310", out)
-
-
-if __name__ == "__main__":
-    unittest.main()
+import contextlib
+import io
+import json
+import unittest
+
+import inventory
+
+
+def run(*argv):
+    out = io.StringIO()
+    with contextlib.redirect_stdout(out):
+        code = inventory.main(list(argv))
+    return code, out.getvalue()
+
+
+class ListTest(unittest.TestCase):
+    def test_text_listing(self):
+        code, out = run("list")
+        self.assertEqual(code, 0)
+        self.assertIn("Hex nut", out)
+        self.assertIn("C-310", out)
+
+    def test_json_listing(self):
+        code, out = run("list", "--json")
+        self.assertEqual(code, 0)
+        with open("items.json", encoding="utf-8") as handle:
+            self.assertEqual(json.loads(out), json.load(handle))
+
+
+if __name__ == "__main__":
+    unittest.main()

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```