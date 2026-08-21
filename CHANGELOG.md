# Changelog

All notable changes to this project are documented in this file.

## 1.0.0 - 2026-08-21

### Added

- Typed checkout pricing models for cart items, coupons, and store policy
- Unit and parameterized test coverage for calculation and validation rules
- Regression cases for three production-style pricing defects
- CI checks across Python 3.11, 3.12, and 3.13

### Fixed

- Use commercial round-half-up behavior for cent-level values
- Enforce the configured maximum for percentage coupons
- Preserve free-shipping eligibility after a coupon is applied
