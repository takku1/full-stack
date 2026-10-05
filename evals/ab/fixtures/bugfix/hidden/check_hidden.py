"""Hidden acceptance checks; copied in only after the session ends."""
import sys

sys.path.insert(0, ".")
from counts import format_count  # noqa: E402

cases = {0: "0", 1: "1", 999: "999", 1000: "1k", 1250: "1.2k", 1500: "1.5k",
         999_949: "999.9k", 3_000_000: "3M", 2_500_000: "2.5M"}
failures = [f"format_count({n}) = {format_count(n)!r}, expected {want!r}"
            for n, want in cases.items() if format_count(n) != want]
print("\n".join(failures) or "all hidden checks passed")
sys.exit(1 if failures else 0)
