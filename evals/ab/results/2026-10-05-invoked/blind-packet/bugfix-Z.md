# bugfix / Z

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"`. The fix is a two-line change in `counts.py`: an `if n == 0: return "0"` check ahead of the old `if not n:` check. The three existing tests in `test_counts.py` pass.

I kept the old `if not n:` check, so `None` still returns `""`, as it did before, and positive counts format as before. I didn't add a test for the zero case. `test_counts.py` has no zero test, which is how the bug went unnoticed. I can add one if you want.

## Files changed

- `counts.py`

## Diff

```diff
diff --git a/counts.py b/counts.py
index 7eb6ca2..32e1f5e 100644
--- a/counts.py
+++ b/counts.py
@@ -3,6 +3,8 @@
 
 def format_count(n):
     """Format a non-negative count: 950, 1.2k, 3M."""
+    if n == 0:
+        return "0"
     if not n:
         return ""
     if n < 1000:

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```