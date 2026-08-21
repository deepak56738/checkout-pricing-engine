from decimal import Decimal

from checkout_pricing import CartItem, PercentCoupon, calculate_checkout


def test_free_shipping_uses_pre_discount_merchandise_subtotal(
    standard_policy,
) -> None:
    """BUG-103: applying a coupon must not remove earned free shipping."""
    cart = [CartItem("BACKPACK", "80.00", 1)]
    coupon = PercentCoupon("SAVE25", "25")

    result = calculate_checkout(cart, policy=standard_policy, coupon=coupon)

    assert result.subtotal == Decimal("80.00")
    assert result.discount == Decimal("20.00")
    assert result.shipping == Decimal("0.00")


def test_subtotal_one_cent_below_threshold_still_pays_shipping(
    standard_policy,
) -> None:
    cart = [CartItem("BACKPACK", "74.99", 1)]

    result = calculate_checkout(cart, policy=standard_policy)

    assert result.shipping == Decimal("6.99")


def test_subtotal_equal_to_threshold_gets_free_shipping(standard_policy) -> None:
    cart = [CartItem("BACKPACK", "75.00", 1)]

    result = calculate_checkout(cart, policy=standard_policy)

    assert result.shipping == Decimal("0.00")

