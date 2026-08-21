# Checkout Pricing Engine

A small, production-style Python package for calculating checkout totals with
percentage coupons, tax, shipping fees, and free-shipping thresholds.

The repository focuses on testing the failure modes that usually hide in
pricing code: currency rounding, discount limits, and threshold boundaries.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Example

```python
from decimal import Decimal

from checkout_pricing import CartItem, PercentCoupon, PricingPolicy
from checkout_pricing import calculate_checkout

cart = [
    CartItem(sku="TSHIRT-BLK-M", unit_price=Decimal("24.99"), quantity=2),
    CartItem(sku="MUG-WHT", unit_price=Decimal("12.50"), quantity=1),
]
coupon = PercentCoupon(code="SAVE10", percent=Decimal("10"))
policy = PricingPolicy(
    tax_rate=Decimal("8.25"),
    shipping_fee=Decimal("6.99"),
    free_shipping_threshold=Decimal("75.00"),
)

summary = calculate_checkout(cart, policy=policy, coupon=coupon)
print(summary.total)
```

## Quality checks

```bash
ruff check .
mypy src
pytest --cov --cov-report=term-missing
```

The project uses `Decimal` throughout the public model so binary floating-point
errors cannot leak into order totals.

