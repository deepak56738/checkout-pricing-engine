"""Checkout total calculation."""

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from checkout_pricing.models import (
    CartItem,
    CheckoutSummary,
    PercentCoupon,
    PricingPolicy,
)

CENT = Decimal("0.01")
HUNDRED = Decimal("100")


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_checkout(
    items: Iterable[CartItem],
    *,
    policy: PricingPolicy | None = None,
    coupon: PercentCoupon | None = None,
) -> CheckoutSummary:
    """Calculate an immutable checkout summary from cart lines and store rules."""
    cart = tuple(items)
    pricing_policy = policy or PricingPolicy()
    item_count = sum(item.quantity for item in cart)
    subtotal = _money(sum((item.line_total for item in cart), start=Decimal("0")))

    discount = Decimal("0.00")
    applied_coupon: str | None = None
    if coupon is not None and subtotal >= coupon.minimum_subtotal:
        calculated_discount = subtotal * coupon.percent / HUNDRED
        if coupon.max_discount is not None:
            calculated_discount = min(calculated_discount, coupon.max_discount)
        discount = _money(min(calculated_discount, subtotal))
        applied_coupon = coupon.code

    discounted_subtotal = _money(subtotal - discount)

    shipping = Decimal("0.00")
    if item_count:
        qualifies_for_free_shipping = (
            pricing_policy.free_shipping_threshold is not None
            and subtotal >= pricing_policy.free_shipping_threshold
        )
        if not qualifies_for_free_shipping:
            shipping = _money(pricing_policy.shipping_fee)

    tax = _money(discounted_subtotal * pricing_policy.tax_rate / HUNDRED)
    total = _money(discounted_subtotal + shipping + tax)

    return CheckoutSummary(
        subtotal=subtotal,
        discount=discount,
        shipping=shipping,
        tax=tax,
        total=total,
        item_count=item_count,
        applied_coupon=applied_coupon,
    )
