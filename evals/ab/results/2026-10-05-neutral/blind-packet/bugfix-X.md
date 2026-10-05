# bugfix / X

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"` instead of an empty string. The fix is a two-line change in `counts.py`, and the 3 existing tests pass.

I left the `if not n: return ""` check in place after the new zero check. That way `None` (and any other falsy non-zero value) still returns `""` as before. Positive counts go through the same code as before.

I didn't add a test for zero, since you asked to keep the change local. `test_counts.py` has no zero case, so nothing currently guards this fix.

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