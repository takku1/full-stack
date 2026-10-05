# feature / X

## Prompt

Add a `--json` flag to `python inventory.py list` that prints the items as a JSON array in file order with the same fields. Keep the default text output exactly as it is, add no dependencies, keep the change local, and run the existing checks.

## Final answer

`python inventory.py list --json` now prints the items as a JSON array in file order, with the same `sku`, `name` and `qty` fields. I ran `python -m unittest` and both tests pass, the existing text test and a new JSON one. I also ran both forms by hand, and the default text output is unchanged.

- **`inventory.py`:** I added the `--json` flag and updated the usage line in the module docstring. The change is 6 lines and adds no dependencies.
- **`test_inventory.py`:** I added `test_json_listing`. It checks the SKU order and one full item.

My first write converted both files from LF to CRLF line endings, which made the diff look like a full rewrite. I restored LF, so the diff is now just the intended lines.

## Files changed

- `inventory.py`
- `test_inventory.py`

## Diff

```diff
diff --git a/inventory.py b/inventory.py
index b6e69a5..a67df74 100644
--- a/inventory.py
+++ b/inventory.py
@@ -1,4 +1,4 @@
-"""Tiny inventory CLI: python inventory.py list [--file PATH]"""
+"""Tiny inventory CLI: python inventory.py list [--file PATH] [--json]"""
 import argparse
 import json
 import sys
@@ -21,9 +21,11 @@ def main(argv=None):
     sub = parser.add_subparsers(dest="command", required=True)
     listing = sub.add_parser("list", help="list items")
     listing.add_argument("--file", default="items.json")
+    listing.add_argument("--json", action="store_true", help="print items as a JSON array")
     args = parser.parse_args(argv)
     if args.command == "list":
-        print(render(load(args.file)))
+        items = load(args.file)
+        print(json.dumps(items) if args.json else render(items))
     return 0
 
 
diff --git a/test_inventory.py b/test_inventory.py
index f39cfbf..decdf55 100644
--- a/test_inventory.py
+++ b/test_inventory.py
@@ -1,5 +1,6 @@
 import contextlib
 import io
+import json
 import unittest
 
 import inventory
@@ -19,6 +20,13 @@ class ListTest(unittest.TestCase):
         self.assertIn("Hex nut", out)
         self.assertIn("C-310", out)
 
+    def test_json_listing(self):
+        code, out = run("list", "--json")
+        self.assertEqual(code, 0)
+        items = json.loads(out)
+        self.assertEqual([i["sku"] for i in items], ["A-100", "B-220", "C-310"])
+        self.assertEqual(items[1], {"sku": "B-220", "name": "Hex nut", "qty": 75})
+
 
 if __name__ == "__main__":
     unittest.main()

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```