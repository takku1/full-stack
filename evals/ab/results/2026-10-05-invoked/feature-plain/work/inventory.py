"""Tiny inventory CLI: python inventory.py list [--file PATH] [--json]"""
import argparse
import json
import sys


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def render(items):
    if not items:
        return "no items"
    width = max(len(item["name"]) for item in items)
    return "\n".join(f"{item['name']:<{width}}  {item['qty']:>4}  {item['sku']}" for item in items)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="inventory")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="list items")
    listing.add_argument("--file", default="items.json")
    listing.add_argument("--json", action="store_true", help="print items as a JSON array")
    args = parser.parse_args(argv)
    if args.command == "list":
        items = load(args.file)
        print(json.dumps(items) if args.json else render(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
