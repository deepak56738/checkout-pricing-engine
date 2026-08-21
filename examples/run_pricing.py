from checkout_pricing import (
    CartItem,
    PercentCoupon,
    PricingPolicy,
    calculate_checkout,
)

cart = [
    CartItem("TSHIRT-BLK-M", "24.99", 2),
    CartItem("MUG-WHT", "12.50", 1),
]
coupon = PercentCoupon("SAVE10", "10")
policy = PricingPolicy(
    tax_rate="8.25",
    shipping_fee="6.99",
    free_shipping_threshold="75.00",
)

summary = calculate_checkout(cart, policy=policy, coupon=coupon)

print(f"Subtotal: {summary.subtotal}")
print(f"Discount: {summary.discount}")
print(f"Shipping: {summary.shipping}")
print(f"Tax:      {summary.tax}")
print(f"Total:    {summary.total}")
