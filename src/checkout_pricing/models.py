"""Typed domain models used by the pricing calculator."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

DecimalInput = Decimal | int | str


def to_decimal(value: DecimalInput, *, field_name: str) -> Decimal:
    """Convert a supported numeric input to ``Decimal`` with a clear error."""
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid decimal value") from exc

    if not number.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return number


@dataclass(frozen=True, slots=True)
class CartItem:
    """A purchasable cart line."""

    sku: str
    unit_price: DecimalInput
    quantity: int

    def __post_init__(self) -> None:
        normalized_sku = self.sku.strip()
        if not normalized_sku:
            raise ValueError("sku must not be empty")
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise TypeError("quantity must be an integer")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        price = to_decimal(self.unit_price, field_name="unit_price")
        if price < 0:
            raise ValueError("unit_price must not be negative")

        object.__setattr__(self, "sku", normalized_sku)
        object.__setattr__(self, "unit_price", price)

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True, slots=True)
class PercentCoupon:
    """A percentage discount with optional eligibility and cap rules."""

    code: str
    percent: DecimalInput
    minimum_subtotal: DecimalInput = Decimal("0")
    max_discount: DecimalInput | None = None

    def __post_init__(self) -> None:
        code = self.code.strip().upper()
        if not code:
            raise ValueError("coupon code must not be empty")

        percent = to_decimal(self.percent, field_name="percent")
        minimum = to_decimal(self.minimum_subtotal, field_name="minimum_subtotal")
        maximum = (
            None
            if self.max_discount is None
            else to_decimal(self.max_discount, field_name="max_discount")
        )

        if not Decimal("0") < percent <= Decimal("100"):
            raise ValueError("percent must be greater than 0 and at most 100")
        if minimum < 0:
            raise ValueError("minimum_subtotal must not be negative")
        if maximum is not None and maximum < 0:
            raise ValueError("max_discount must not be negative")

        object.__setattr__(self, "code", code)
        object.__setattr__(self, "percent", percent)
        object.__setattr__(self, "minimum_subtotal", minimum)
        object.__setattr__(self, "max_discount", maximum)


@dataclass(frozen=True, slots=True)
class PricingPolicy:
    """Store-level tax and shipping rules."""

    tax_rate: DecimalInput = Decimal("0")
    shipping_fee: DecimalInput = Decimal("0")
    free_shipping_threshold: DecimalInput | None = None

    def __post_init__(self) -> None:
        tax_rate = to_decimal(self.tax_rate, field_name="tax_rate")
        shipping_fee = to_decimal(self.shipping_fee, field_name="shipping_fee")
        threshold = (
            None
            if self.free_shipping_threshold is None
            else to_decimal(
                self.free_shipping_threshold,
                field_name="free_shipping_threshold",
            )
        )

        if not Decimal("0") <= tax_rate <= Decimal("100"):
            raise ValueError("tax_rate must be between 0 and 100")
        if shipping_fee < 0:
            raise ValueError("shipping_fee must not be negative")
        if threshold is not None and threshold < 0:
            raise ValueError("free_shipping_threshold must not be negative")

        object.__setattr__(self, "tax_rate", tax_rate)
        object.__setattr__(self, "shipping_fee", shipping_fee)
        object.__setattr__(self, "free_shipping_threshold", threshold)


@dataclass(frozen=True, slots=True)
class CheckoutSummary:
    """Immutable breakdown returned after pricing a cart."""

    subtotal: Decimal
    discount: Decimal
    shipping: Decimal
    tax: Decimal
    total: Decimal
    item_count: int
    applied_coupon: str | None

