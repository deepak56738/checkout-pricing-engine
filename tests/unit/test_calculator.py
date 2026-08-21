from decimal import Decimal

import pytest

from checkout_pricing import (
    CartItem,
    PercentCoupon,
    PricingPolicy,
    calculate_checkout,
)


def test_calculates_checkout_breakdown_without_coupon() -> None:
    cart = [
        CartItem("NOTEBOOK", "19.99", 2),
        CartItem("PEN-SET", "5.50", 1),
    ]
    policy = PricingPolicy(
        tax_rate="8.25",
        shipping_fee="6.99",
        free_shipping_threshold="75",
    )

    result = calculate_checkout(cart, policy=policy)

    assert result.subtotal == Decimal("45.48")
    assert result.discount == Decimal("0.00")
    assert result.shipping == Decimal("6.99")
    assert result.tax == Decimal("3.75")
    assert result.total == Decimal("56.22")
    assert result.item_count == 3
    assert result.applied_coupon is None


def test_applies_eligible_coupon() -> None:
    cart = [CartItem("HEADPHONES", "100", 1)]
    coupon = PercentCoupon("save10", "10", minimum_subtotal="50")
    policy = PricingPolicy(
        tax_rate="8",
        shipping_fee="5",
        free_shipping_threshold="75",
    )

    result = calculate_checkout(cart, policy=policy, coupon=coupon)

    assert result.discount == Decimal("10.00")
    assert result.shipping == Decimal("0.00")
    assert result.tax == Decimal("7.20")
    assert result.total == Decimal("97.20")
    assert result.applied_coupon == "SAVE10"


def test_ignores_coupon_below_minimum_subtotal() -> None:
    cart = [CartItem("CABLE", "12.00", 1)]
    coupon = PercentCoupon("SAVE20", "20", minimum_subtotal="50")

    result = calculate_checkout(cart, coupon=coupon)

    assert result.discount == Decimal("0.00")
    assert result.applied_coupon is None


def test_empty_cart_has_no_shipping_charge() -> None:
    policy = PricingPolicy(shipping_fee="9.99")

    result = calculate_checkout([], policy=policy)

    assert result.total == Decimal("0.00")
    assert result.shipping == Decimal("0.00")
    assert result.item_count == 0


def test_accepts_single_pass_iterables() -> None:
    cart = (CartItem(f"SKU-{index}", "10", 1) for index in range(3))

    result = calculate_checkout(cart)

    assert result.subtotal == Decimal("30.00")
    assert result.item_count == 3


@pytest.mark.parametrize(
    ("price", "quantity", "expected"),
    [
        ("0", 1, "0.00"),
        ("1.25", 4, "5.00"),
        ("999.99", 2, "1999.98"),
    ],
)
def test_line_total_contributes_to_subtotal(
    price: str,
    quantity: int,
    expected: str,
) -> None:
    result = calculate_checkout([CartItem("SKU", price, quantity)])

    assert result.subtotal == Decimal(expected)


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_rejects_non_positive_quantity(quantity: int) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        CartItem("SKU", "10", quantity)


def test_rejects_boolean_quantity() -> None:
    with pytest.raises(TypeError, match="integer"):
        CartItem("SKU", "10", True)


def test_rejects_negative_unit_price() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        CartItem("SKU", "-0.01", 1)


@pytest.mark.parametrize("sku", ["", "   "])
def test_rejects_empty_sku(sku: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        CartItem(sku, "1", 1)


@pytest.mark.parametrize("percent", ["0", "100.01", "-5"])
def test_rejects_invalid_coupon_percentage(percent: str) -> None:
    with pytest.raises(ValueError, match="greater than 0 and at most 100"):
        PercentCoupon("SAVE", percent)


def test_rejects_invalid_policy_values() -> None:
    with pytest.raises(ValueError, match="tax_rate"):
        PricingPolicy(tax_rate="101")
    with pytest.raises(ValueError, match="shipping_fee"):
        PricingPolicy(shipping_fee="-1")
    with pytest.raises(ValueError, match="free_shipping_threshold"):
        PricingPolicy(free_shipping_threshold="-1")

