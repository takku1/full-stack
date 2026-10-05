import os
import tempfile
import unittest
from pathlib import Path

from tasks import store


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "tasks.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_add_and_complete(self):
        task = store.add("write tests", self.path)
        store.complete(task["id"], self.path)
        self.assertTrue(store.load(self.path)["tasks"][0]["done"])

    def test_complete_unknown(self):
        with self.assertRaises(store.TaskError):
            store.complete(42, self.path)

    def test_archive(self):
        task = store.add("old", self.path)
        store.complete(task["id"], self.path)
        store.archive(task["id"], self.path)
        data = store.load(self.path)
        self.assertEqual(data["tasks"], [])
        self.assertEqual([t["id"] for t in data["archived"]], [task["id"]])
        self.assertEqual(store.add("new", self.path)["id"], task["id"] + 1)

    def test_archive_errors_leave_data_unchanged(self):
        open_task = store.add("open", self.path)
        done = store.add("done", self.path)
        store.complete(done["id"], self.path)
        store.archive(done["id"], self.path)
        before = self.path.read_text(encoding="utf-8")
        for task_id in (open_task["id"], done["id"], 99):
            with self.assertRaises(store.TaskError):
                store.archive(task_id, self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_legacy_file_without_archived(self):
        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "t", "done": true}]}')
        store.archive(1, self.path)
        self.assertEqual(len(store.load(self.path)["archived"]), 1)


if __name__ == "__main__":
    unittest.main()
