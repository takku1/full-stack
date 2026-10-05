import unittest

from counts import format_count


class FormatCountTest(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_count(0), "0")

    def test_small(self):
        self.assertEqual(format_count(7), "7")
        self.assertEqual(format_count(999), "999")

    def test_thousands(self):
        self.assertEqual(format_count(1000), "1k")
        self.assertEqual(format_count(1250), "1.2k")

    def test_millions(self):
        self.assertEqual(format_count(3_000_000), "3M")


if __name__ == "__main__":
    unittest.main()
