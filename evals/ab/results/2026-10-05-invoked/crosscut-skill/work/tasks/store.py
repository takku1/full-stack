"""JSON file storage for tasks. Data file format: {"next_id": int, "tasks": [...], "archived": [...]}.

"archived" is optional in older files. next_id never decreases, so ids are not reused.
"""
import json
import os
from pathlib import Path

DEFAULT_PATH = Path(os.environ.get("TASKS_FILE", "tasks.json"))


class TaskError(Exception):
    pass


def load(path=DEFAULT_PATH):
    if not Path(path).exists():
        return {"next_id": 1, "tasks": [], "archived": []}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("archived", [])  # files written before archiving lack it
    return data


def save(data, path=DEFAULT_PATH):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def add(title, path=DEFAULT_PATH):
    data = load(path)
    task = {"id": data["next_id"], "title": title, "done": False}
    data["tasks"].append(task)
    data["next_id"] += 1
    save(data, path)
    return task


def complete(task_id, path=DEFAULT_PATH):
    data = load(path)
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["done"] = True
            save(data, path)
            return task
    raise TaskError(f"no task {task_id}")


def archive(task_id, path=DEFAULT_PATH):
    data = load(path)
    if any(task["id"] == task_id for task in data["archived"]):
        raise TaskError(f"task {task_id} is already archived")
    for task in data["tasks"]:
        if task["id"] == task_id:
            if not task["done"]:
                raise TaskError(f"task {task_id} is not done")
            data["tasks"].remove(task)
            data["archived"].append(task)
            save(data, path)
            return task
    raise TaskError(f"no task {task_id}")
