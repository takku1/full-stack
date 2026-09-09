MAX_DISCOUNT_PERCENT = 50


def total_cents(prices, discount_percent=0):
    if isinstance(discount_percent, bool) or not isinstance(discount_percent, int):
        raise TypeError('discount_percent must be an integer')
    if not 0 <= discount_percent <= MAX_DISCOUNT_PERCENT:
        raise ValueError(f'discount_percent must be between 0 and {MAX_DISCOUNT_PERCENT}')
    total = 0
    for price in prices:
        if isinstance(price, bool) or not isinstance(price, int):
            raise TypeError('prices must contain integer cents')
        if price < 0:
            raise ValueError('prices must be nonnegative')
        total += price
    return total * (100 - discount_percent) // 100
