"""Measure instruction cost; optional development dependency: tiktoken.

Run from any directory. Counts are not model billing or quality measurements.
"""

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="HEAD")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("TIKTOKEN_CACHE_DIR", str(root / ".tokenizer-cache"))
    import tiktoken

    encoder = tiktoken.get_encoding("o200k_base")
    prefix = "skill/full-stack/"
    baseline = subprocess.check_output(
        ["git", "rev-parse", args.baseline], cwd=root, text=True
    ).strip()
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", baseline, prefix], cwd=root, text=True
    ).splitlines()
    old = {
        p: subprocess.check_output(["git", "show", f"{baseline}:{p}"], cwd=root).decode("utf-8-sig")
        for p in paths if p.endswith(".md")
    }
    new = {
        p.relative_to(root).as_posix(): p.read_text(encoding="utf-8-sig")
        for p in (root / prefix).rglob("*.md")
    }

    def count(text):
        return len(encoder.encode(text.replace("\r\n", "\n")))

    files = {
        p: {"before": count(old[p]) if p in old else 0,
            "after": count(new[p]) if p in new else 0}
        for p in sorted(old.keys() | new.keys())
    }
    entry = prefix + "SKILL.md"
    print(json.dumps({
        "baseline_commit": baseline,
        "tokenizer": "o200k_base",
        "tiktoken_version": importlib.metadata.version("tiktoken"),
        "normalization": "UTF-8 without BOM; LF newlines; full Markdown including frontmatter",
        "files": files,
        "entrypoint_reduction_percent": round(100 * (1 - files[entry]["after"] / files[entry]["before"]), 2),
        "all_markdown": {axis: sum(row[axis] for row in files.values()) for axis in ("before", "after")},
        "implementation_route_after": files[entry]["after"] + files[prefix + "references/implementation.md"]["after"],
        "limits": "Counts omit host wrappers, tools, task artifacts, rereads, and reasoning. Reference loading varies by task. No equivalent 0.1 implementation route exists."
    }, indent=2))


if __name__ == "__main__":
    main()
