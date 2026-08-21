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


@dataclass(frozen=True, slots=True, init=False)
class CartItem:
    """A purchasable cart line."""

    sku: str
    unit_price: Decimal
    quantity: int

    def __init__(self, sku: str, unit_price: DecimalInput, quantity: int) -> None:
        normalized_sku = sku.strip()
        if not normalized_sku:
            raise ValueError("sku must not be empty")
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("quantity must be an integer")
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        price = to_decimal(unit_price, field_name="unit_price")
        if price < 0:
            raise ValueError("unit_price must not be negative")

        object.__setattr__(self, "sku", normalized_sku)
        object.__setattr__(self, "unit_price", price)
        object.__setattr__(self, "quantity", quantity)

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True, slots=True, init=False)
class PercentCoupon:
    """A percentage discount with optional eligibility and cap rules."""

    code: str
    percent: Decimal
    minimum_subtotal: Decimal
    max_discount: Decimal | None

    def __init__(
        self,
        code: str,
        percent: DecimalInput,
        minimum_subtotal: DecimalInput = Decimal("0"),
        max_discount: DecimalInput | None = None,
    ) -> None:
        normalized_code = code.strip().upper()
        if not normalized_code:
            raise ValueError("coupon code must not be empty")

        normalized_percent = to_decimal(percent, field_name="percent")
        minimum = to_decimal(minimum_subtotal, field_name="minimum_subtotal")
        maximum = (
            None
            if max_discount is None
            else to_decimal(max_discount, field_name="max_discount")
        )

        if not Decimal("0") < normalized_percent <= Decimal("100"):
            raise ValueError("percent must be greater than 0 and at most 100")
        if minimum < 0:
            raise ValueError("minimum_subtotal must not be negative")
        if maximum is not None and maximum < 0:
            raise ValueError("max_discount must not be negative")

        object.__setattr__(self, "code", normalized_code)
        object.__setattr__(self, "percent", normalized_percent)
        object.__setattr__(self, "minimum_subtotal", minimum)
        object.__setattr__(self, "max_discount", maximum)


@dataclass(frozen=True, slots=True, init=False)
class PricingPolicy:
    """Store-level tax and shipping rules."""

    tax_rate: Decimal
    shipping_fee: Decimal
    free_shipping_threshold: Decimal | None

    def __init__(
        self,
        tax_rate: DecimalInput = Decimal("0"),
        shipping_fee: DecimalInput = Decimal("0"),
        free_shipping_threshold: DecimalInput | None = None,
    ) -> None:
        normalized_tax_rate = to_decimal(tax_rate, field_name="tax_rate")
        normalized_shipping_fee = to_decimal(
            shipping_fee,
            field_name="shipping_fee",
        )
        threshold = (
            None
            if free_shipping_threshold is None
            else to_decimal(
                free_shipping_threshold,
                field_name="free_shipping_threshold",
            )
        )

        if not Decimal("0") <= normalized_tax_rate <= Decimal("100"):
            raise ValueError("tax_rate must be between 0 and 100")
        if normalized_shipping_fee < 0:
            raise ValueError("shipping_fee must not be negative")
        if threshold is not None and threshold < 0:
            raise ValueError("free_shipping_threshold must not be negative")

        object.__setattr__(self, "tax_rate", normalized_tax_rate)
        object.__setattr__(self, "shipping_fee", normalized_shipping_fee)
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
