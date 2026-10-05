# bugfix / Z

## Prompt

Fix `format_count(0)` returning an empty string. Return "0" for zero and preserve existing positive-count formatting. Keep this change local and run the existing checks.

## Final answer

`format_count(0)` now returns `"0"`. The three existing tests pass, and I confirmed `format_count(0)` gives `"0"` with a quick one-off call.

The cause was `if not n: return ""` in `counts.py`, which treated `0` the same as "no value". I changed it to `if n is None: return ""`, so `None` still returns `""` as before. Positive counts go through the same code and format as before.

I didn't add a test for zero, since you asked to keep the change local. A one-line `assertEqual(format_count(0), "0")` in `test_counts.py` would cover it if you want it.

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