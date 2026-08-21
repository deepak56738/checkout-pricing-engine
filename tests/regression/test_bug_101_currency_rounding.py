from decimal import Decimal

from checkout_pricing import CartItem, PercentCoupon, calculate_checkout


def test_half_cent_discount_rounds_away_from_zero() -> None:
    """BUG-101: a half-cent discount must use commercial currency rounding."""
    cart = [CartItem("LOW-COST-ITEM", "0.05", 1)]
    coupon = PercentCoupon("SAVE10", "10")

    result = calculate_checkout(cart, coupon=coupon)

    assert result.discount == Decimal("0.01")
    assert result.total == Decimal("0.04")

