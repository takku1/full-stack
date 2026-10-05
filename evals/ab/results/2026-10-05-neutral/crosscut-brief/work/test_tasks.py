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
        a = store.add("a", self.path)
        b = store.add("b", self.path)
        store.complete(a["id"], self.path)
        store.archive(a["id"], self.path)
        data = store.load(self.path)
        self.assertEqual([t["id"] for t in data["tasks"]], [b["id"]])
        self.assertEqual([t["id"] for t in data["archived"]], [a["id"]])
        self.assertEqual(store.add("c", self.path)["id"], 3)

    def test_archive_rejections_leave_data_unchanged(self):
        a = store.add("a", self.path)
        b = store.add("b", self.path)
        store.complete(b["id"], self.path)
        store.archive(b["id"], self.path)
        before = self.path.read_text()
        for task_id in (a["id"], b["id"], 99):
            with self.assertRaises(store.TaskError):
                store.archive(task_id, self.path)
        self.assertEqual(self.path.read_text(), before)

    def test_legacy_file_without_archived(self):
        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "t", "done": true}]}')
        store.archive(1, self.path)
        self.assertEqual(store.load(self.path)["archived"][0]["id"], 1)


if __name__ == "__main__":
    unittest.main()
