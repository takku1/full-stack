"""Compact display of item counts for list headers."""


def format_count(n):
    """Format a non-negative count: 950, 1.2k, 3M."""
    if n is None:
        return ""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return _trim(f"{n / 1000:.1f}") + "k"
    return _trim(f"{n / 1_000_000:.1f}") + "M"


def _trim(text):
    return text[:-2] if text.endswith(".0") else text
