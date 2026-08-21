from decimal import Decimal

from checkout_pricing import CartItem, PercentCoupon, calculate_checkout


def test_coupon_discount_never_exceeds_configured_cap() -> None:
    """BUG-102: percentage coupons must respect their maximum discount."""
    cart = [CartItem("LAPTOP", "500.00", 1)]
    coupon = PercentCoupon("SAVE20", "20", max_discount="25.00")

    result = calculate_checkout(cart, coupon=coupon)

    assert result.discount == Decimal("25.00")
    assert result.total == Decimal("475.00")


def test_coupon_can_discount_entire_subtotal_but_not_more() -> None:
    cart = [CartItem("CLEARANCE", "12.00", 1)]
    coupon = PercentCoupon("FREE", "100", max_discount="50.00")

    result = calculate_checkout(cart, coupon=coupon)

    assert result.discount == Decimal("12.00")
    assert result.total == Decimal("0.00")

