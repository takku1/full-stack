import unittest
from app import checkout


class CheckoutTests(unittest.TestCase):
    def test_existing_checkout(self):
        self.assertEqual(checkout([100, 250]), {'total_cents': 350})


if __name__ == '__main__':
    unittest.main()
