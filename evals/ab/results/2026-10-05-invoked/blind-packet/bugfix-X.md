# bugfix / X

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"`, and the existing tests pass along with a new zero test.

**The fix:** in `counts.py`, the guard `if not n:` treated `0` as empty. I changed it to `if n is None:`. `None` still returns `""` as before, and every positive-count path is untouched.

**Test:** I added `test_zero` to `test_counts.py`.

**Checks:** `python -m unittest -v` ran 4 tests, all OK, and was recorded through the run guard. The guard reported 2 files changed, both inside the write set, with no scope violations. The run is closed.

**Ready/conditional/blocked:** this single fix was ready and is done. There was no work tracker, so nothing was registered and no design file was written.

**Your call:** I kept `None` → `""` because that was the existing behavior. If you'd rather `None` also return `"0"` or raise an error, that is a separate change.

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