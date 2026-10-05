# bugfix / Y

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"` instead of an empty string. The test suite passes (`python -m unittest -v`, 4 tests).

- **Cause:** `counts.py` used `if not n: return ""`, which treated `0` the same as "no value". I changed it to `if n is None: return ""`. A `None` input still gives `""`, as before. Positive counts take the same code path as before.
- **Test:** I added `test_zero` to `test_counts.py`. The existing tests for 7, 999, 1k, 1.2k and 3M still pass.
- **Scope:** Only those two files changed. `format_count` has no other callers in this directory, so nothing else was affected.
- **Not handled:** The docstring says the input is a non-negative count, so I didn't handle other falsy values. For example, `format_count(0.0)` would return `"0.0"`.

Nothing is unfinished or blocked.

## Files changed

- `counts.py`
- `test_counts.py`

## Diff

```diff
diff --git a/counts.py b/counts.py
index 7eb6ca2..93850d9 100644
--- a/counts.py
+++ b/counts.py
@@ -3,7 +3,7 @@
 
 def format_count(n):
     """Format a non-negative count: 950, 1.2k, 3M."""
-    if not n:
+    if n is None:
         return ""
     if n < 1000:
         return str(n)
diff --git a/test_counts.py b/test_counts.py
index af0f385..5b9f2ba 100644
--- a/test_counts.py
+++ b/test_counts.py
@@ -4,6 +4,9 @@ from counts import format_count
 
 
 class FormatCountTest(unittest.TestCase):
+    def test_zero(self):
+        self.assertEqual(format_count(0), "0")
+
     def test_small(self):
         self.assertEqual(format_count(7), "7")
         self.assertEqual(format_count(999), "999")

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```