from pricing import total_cents


def checkout(prices, discount_percent=0):
    return {'total_cents': total_cents(prices, discount_percent)}
