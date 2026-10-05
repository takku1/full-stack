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

    def test_archive_persists_and_ids_not_reused(self):
        first = store.add("a", self.path)
        store.complete(first["id"], self.path)
        store.archive(first["id"], self.path)
        data = store.load(self.path)
        self.assertEqual(data["tasks"], [])
        self.assertEqual([t["id"] for t in store.list_archived(self.path)], [first["id"]])
        self.assertNotEqual(store.add("b", self.path)["id"], first["id"])

    def test_archive_rejections_leave_data_unchanged(self):
        task = store.add("a", self.path)
        store.add("b", self.path)
        store.complete(task["id"], self.path)
        store.archive(task["id"], self.path)
        before = self.path.read_text(encoding="utf-8")
        for bad in (99, 2, task["id"]):  # unknown, incomplete, already archived
            with self.assertRaises(store.TaskError):
                store.archive(bad, self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_legacy_file_without_archived_key(self):
        self.path.write_text('{"next_id": 2, "tasks": [{"id": 1, "title": "x", "done": true}]}')
        self.assertEqual(store.list_archived(self.path), [])
        store.archive(1, self.path)
        self.assertEqual(store.load(self.path)["next_id"], 2)


if __name__ == "__main__":
    unittest.main()
