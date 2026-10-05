"""python -m tasks add TITLE | list [--archived] | done ID | archive ID"""
import argparse
import sys

from . import store


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tasks")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("add").add_argument("title")
    sub.add_parser("list").add_argument("--archived", action="store_true")
    sub.add_parser("done").add_argument("id", type=int)
    sub.add_parser("archive").add_argument("id", type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "add":
            print(store.add(args.title)["id"])
        elif args.command == "list":
            data = store.load()
            for task in data["archived" if args.archived else "tasks"]:
                print(f"{task['id']:>3} [{'x' if task['done'] else ' '}] {task['title']}")
        elif args.command == "done":
            store.complete(args.id)
        elif args.command == "archive":
            store.archive(args.id)
    except store.TaskError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
