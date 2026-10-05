"""python -m tasks add TITLE | list | done ID"""
import argparse
import sys

from . import store


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tasks")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("add").add_argument("title")
    sub.add_parser("list")
    sub.add_parser("done").add_argument("id", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            print(store.add(args.title)["id"])
        elif args.command == "list":
            for task in store.load()["tasks"]:
                print(f"{task['id']:>3} [{'x' if task['done'] else ' '}] {task['title']}")
        elif args.command == "done":
            store.complete(args.id)
    except store.TaskError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
