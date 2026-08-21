# Checkout Pricing Engine

[![CI](https://github.com/deepak56738/checkout-pricing-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/deepak56738/checkout-pricing-engine/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![tests-pytest](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](https://docs.pytest.org/)
[![license-MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-style Python package for calculating checkout totals with
percentage coupons, tax, shipping fees, and free-shipping thresholds.

The project demonstrates how focused tests can reproduce and permanently guard
against subtle pricing defects. Its regression suite covers commercial currency
rounding, coupon caps, and exact shipping-threshold boundaries.

## What this project demonstrates

- Typed, immutable domain models built around `Decimal`
- Unit, parameterized, boundary, and regression tests with `pytest`
- Three documented bug reproductions with focused fixes
- Branch coverage enforced at 95% or higher
- Static analysis with Ruff and strict mypy
- Continuous integration across Python 3.11, 3.12, and 3.13
- Modern `src/` package layout and reproducible dependencies with `uv.lock`

## Pricing rules

The calculator follows explicit business rules so each result is predictable:

1. Merchandise subtotal is calculated before coupons.
2. Eligible percentage coupons respect both their configured cap and the cart
   subtotal.
3. Currency values use round-half-up at the cent boundary.
4. Tax applies to discounted merchandise, not shipping.
5. Free shipping is earned from the pre-discount merchandise subtotal.
6. Empty carts never receive a shipping charge.

## Regression cases

| Case | Failure reproduced | Expected behavior |
| --- | --- | --- |
| BUG-101 | A half-cent coupon discount became `$0.00` | `$0.005` rounds to `$0.01` |
| BUG-102 | A coupon ignored its `$25` maximum | Discount never exceeds its cap |
| BUG-103 | Applying a coupon removed free shipping | Pre-discount subtotal controls eligibility |

The investigation and root-cause notes are in
[`docs/bug-fixes.md`](docs/bug-fixes.md).

## Project structure

```text
checkout-pricing-engine/
├── src/checkout_pricing/       # Domain models and pricing calculation
├── tests/unit/                 # Core behavior and validation tests
├── tests/regression/           # One focused suite per historical defect
├── docs/bug-fixes.md           # Reproduction and root-cause notes
├── examples/run_pricing.py     # Small runnable example
└── .github/workflows/ci.yml    # Quality and test pipeline
```

## Quick start

### With uv

```bash
uv sync --extra dev
uv run pytest
```

### With pip

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

## Example

```python
from checkout_pricing import CartItem, PercentCoupon, PricingPolicy
from checkout_pricing import calculate_checkout

cart = [
    CartItem(sku="TSHIRT-BLK-M", unit_price="24.99", quantity=2),
    CartItem(sku="MUG-WHT", unit_price="12.50", quantity=1),
]
coupon = PercentCoupon(code="SAVE10", percent="10")
policy = PricingPolicy(
    tax_rate="8.25",
    shipping_fee="6.99",
    free_shipping_threshold="75.00",
)

summary = calculate_checkout(cart, policy=policy, coupon=coupon)
print(summary.total)
```

Run the complete example with:

```bash
uv run python examples/run_pricing.py
```

## Quality checks

```bash
make check
```

Or run each check separately:

```bash
uv run ruff check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
```

## License

Released under the [MIT License](LICENSE).

