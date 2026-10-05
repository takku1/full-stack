# bugfix / Y

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"`. The existing three tests pass, and a direct call confirmed the zero case.

The bug was the `if not n:` guard in `counts.py`, which treated 0 as empty. I changed it to `if n is None:`. That keeps `format_count(None)` returning `""` as before, and positive counts take the same code paths as before.

I didn't add a test for zero, since you asked for a local change. A one-line case in `test_counts.py`'s small-counts test would cover it if you want one.

## Files changed

- `counts.py`

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

```

## Hidden acceptance checks

exit 0

```
all hidden checks passed
```