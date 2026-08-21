from decimal import Decimal

import pytest

from checkout_pricing import CartItem, PercentCoupon, PricingPolicy


def test_models_normalize_public_inputs() -> None:
    item = CartItem("  sku-101  ", 12, 2)
    coupon = PercentCoupon("  save15  ", 15, 25, 10)
    policy = PricingPolicy(8, 5, 50)

    assert item.sku == "sku-101"
    assert item.unit_price == Decimal("12")
    assert item.line_total == Decimal("24")
    assert coupon.code == "SAVE15"
    assert coupon.percent == Decimal("15")
    assert coupon.minimum_subtotal == Decimal("25")
    assert coupon.max_discount == Decimal("10")
    assert policy.tax_rate == Decimal("8")
    assert policy.shipping_fee == Decimal("5")
    assert policy.free_shipping_threshold == Decimal("50")


def test_default_policy_has_zero_charges_and_no_threshold() -> None:
    policy = PricingPolicy()

    assert policy.tax_rate == Decimal("0")
    assert policy.shipping_fee == Decimal("0")
    assert policy.free_shipping_threshold is None


@pytest.mark.parametrize("value", ["not-a-number", "--1"])
def test_rejects_malformed_decimal_input(value: str) -> None:
    with pytest.raises(ValueError, match="valid decimal value"):
        CartItem("SKU", value, 1)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_rejects_non_finite_decimal_input(value: str) -> None:
    with pytest.raises(ValueError, match="must be finite"):
        CartItem("SKU", value, 1)


def test_rejects_non_integer_quantity() -> None:
    with pytest.raises(TypeError, match="quantity must be an integer"):
        CartItem("SKU", "10", 1.5)  # type: ignore[arg-type]


def test_rejects_empty_coupon_code() -> None:
    with pytest.raises(ValueError, match="coupon code must not be empty"):
        PercentCoupon("  ", "10")


def test_rejects_negative_coupon_minimum() -> None:
    with pytest.raises(ValueError, match="minimum_subtotal"):
        PercentCoupon("SAVE", "10", minimum_subtotal="-0.01")


def test_rejects_negative_coupon_cap() -> None:
    with pytest.raises(ValueError, match="max_discount"):
        PercentCoupon("SAVE", "10", max_discount="-0.01")
