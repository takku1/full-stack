import unittest
from app import checkout
from pricing import total_cents


class CheckoutTests(unittest.TestCase):
    def test_existing_checkout(self):
        self.assertEqual(checkout([100, 250]), {'total_cents': 350})

    def test_zero_empty_and_zero_prices(self):
        for prices in ([], [0], [100, 250]):
            self.assertEqual(checkout(prices, discount_percent=0), {'total_cents': sum(prices)})

    def test_discount_boundaries(self):
        self.assertEqual(checkout([100, 250], 1), {'total_cents': 346})
        self.assertEqual(checkout([100, 250], discount_percent=30), {'total_cents': 245})
        self.assertEqual(checkout([], 30), {'total_cents': 0})

    def test_floor_after_sum(self):
        self.assertEqual(checkout([1, 1], 30), {'total_cents': 1})
        self.assertEqual(checkout([101], 10), {'total_cents': 90})

    def test_large_integer_precision(self):
        self.assertEqual(checkout([10**30 + 1], 10), {'total_cents': 9 * 10**29})

    def test_discount_errors(self):
        for discount in (-1, 31, 50, 51, 100):
            with self.subTest(discount=discount), self.assertRaises(ValueError):
                checkout([100], discount)
        for discount in (True, False, 1.0, '10', None):
            with self.subTest(discount=discount), self.assertRaises(TypeError):
                checkout([100], discount)

    def test_price_errors(self):
        for price in (True, False, 1.0, '100', None):
            with self.subTest(price=price), self.assertRaises(TypeError):
                checkout([100, price], 10)
        with self.assertRaises(ValueError):
            checkout([100, -1], 10)

    def test_iterable_and_no_mutation(self):
        prices = [100, 250]
        self.assertEqual(checkout(iter(prices), 10), {'total_cents': 315})
        self.assertEqual(prices, [100, 250])

    def test_existing_pricing_call(self):
        self.assertEqual(total_cents([100, 250]), 350)


if __name__ == '__main__':
    unittest.main()
