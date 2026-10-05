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


if __name__ == "__main__":
    unittest.main()
