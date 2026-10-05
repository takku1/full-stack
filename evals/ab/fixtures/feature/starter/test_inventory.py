import contextlib
import io
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


if __name__ == "__main__":
    unittest.main()
