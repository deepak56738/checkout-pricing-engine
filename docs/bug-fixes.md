# Regression case notes

These cases document the pricing defects captured by the regression suite.
Each fix is protected by a focused test so the same behavior cannot silently
return during future refactoring.

## BUG-101 — half-cent currency rounding

**Observed:** a 10% coupon on a $0.05 line produced a $0.00 discount.

**Expected:** customer-facing currency uses round-half-up, so $0.005 becomes
$0.01.

**Root cause:** `Decimal.quantize()` was using its default half-even rounding
mode. Half-even is useful for aggregate statistics but did not match the store's
published currency rule.

**Regression:** `test_half_cent_discount_rounds_away_from_zero`

## BUG-102 — coupon maximum ignored

**Observed:** a 20% coupon with a $25 cap discounted a $500 order by $100.

**Expected:** the discount must be the lowest of the calculated percentage,
the configured maximum, and the merchandise subtotal.

**Root cause:** the calculator validated `max_discount` but never applied it.

**Regression:** `test_coupon_discount_never_exceeds_configured_cap`

## BUG-103 — coupon removed free shipping

**Observed:** an $80 cart qualified for free shipping, then lost it when a 25%
coupon reduced the payable merchandise amount to $60.

**Expected:** the free-shipping threshold is based on the pre-discount
merchandise subtotal.

**Root cause:** the threshold comparison used the discounted subtotal.

**Regression:** `test_free_shipping_uses_pre_discount_merchandise_subtotal`

