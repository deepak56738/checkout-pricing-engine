from decimal import Decimal

import pytest

from checkout_pricing import PricingPolicy


@pytest.fixture
def standard_policy() -> PricingPolicy:
    return PricingPolicy(
        tax_rate=Decimal("8.25"),
        shipping_fee=Decimal("6.99"),
        free_shipping_threshold=Decimal("75.00"),
    )

