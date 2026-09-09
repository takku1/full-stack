from pricing import total_cents


def checkout(prices):
    return {'total_cents': total_cents(prices)}
