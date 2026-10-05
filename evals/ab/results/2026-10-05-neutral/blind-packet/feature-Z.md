# feature / Z

## Prompt

Add a `--json` flag to `python inventory.py list` that prints the items as a JSON array in file order with the same fields. Keep the default text output exactly as it is, add no dependencies, keep the change local, and run the existing checks.

## Final answer

`python inventory.py list --json` now prints the items as a JSON array in file order. It prints each item as it appears in `items.json`, so the fields are the same. The default text output is untouched. The existing checks pass.

I ran `python -m unittest -v`, which runs both the original text-listing test and a new one. I did not run the CLI by hand with or without `--json`.

- **`inventory.py`:** I added the `--json` flag to the `list` subcommand and updated the usage line in the docstring. It adds no dependencies and nothing else changed.
- **`test_inventory.py`:** I added `test_json_listing`, which checks that the `--json` output parses to exactly the contents of `items.json`.

The output is compact JSON on one line, not indented.

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
index f39cfbf..8233883 100644
--- a/test_inventory.py
+++ b/test_inventory.py
@@ -1,5 +1,6 @@
 import contextlib
 import io
+import json
 import unittest
 
 import inventory
@@ -19,6 +20,12 @@ class ListTest(unittest.TestCase):
         self.assertIn("Hex nut", out)
         self.assertIn("C-310", out)
 
+    def test_json_listing(self):
+        code, out = run("list", "--json")
+        self.assertEqual(code, 0)
+        with open("items.json", encoding="utf-8") as handle:
+            self.assertEqual(json.loads(out), json.load(handle))
+
 
 if __name__ == "__main__":
     unittest.main()

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```