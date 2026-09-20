def spread_pct(bid: float | None, ask: float | None) -> float | None:
    if bid is None or ask is None or bid <= 0:
        return None
    return ((ask - bid) / bid) * 100


def depth_within_percent(
    levels: list[tuple[float, float]],
    reference_price: float,
    percent: float,
    side: str,
) -> float:
    if not reference_price or reference_price <= 0:
        return 0.0

    if side == "bid":
        min_price = reference_price * (1 - percent / 100)
        return sum(price * qty for price, qty in levels if price >= min_price)

    max_price = reference_price * (1 + percent / 100)
    return sum(price * qty for price, qty in levels if price <= max_price)
