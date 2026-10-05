import contextlib
import io
import json
import unittest

import inventory


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = inventory.main(list(argv))
    return code, out.getvalue()


class ListTest(unittest.TestCase):
    def test_text_listing(self):
        code, out = run("list")
        self.assertEqual(code, 0)
        self.assertIn("Hex nut", out)
        self.assertIn("C-310", out)

    def test_json_listing(self):
        code, out = run("list", "--json")
        self.assertEqual(code, 0)
        items = json.loads(out)
        self.assertEqual([i["sku"] for i in items], ["A-100", "B-220", "C-310"])
        self.assertEqual(items[1], {"sku": "B-220", "name": "Hex nut", "qty": 75})


if __name__ == "__main__":
    unittest.main()
