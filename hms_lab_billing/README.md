# Hospital Management — Lab Billing (`hms_lab_billing`)

Bridge module between `hms_lab` and `hms_billing`. Adds a "Bill" button on completed lab requests that creates a draft `sale.order` with one line per billable test type.

Auto-installs when both `hms_lab` and `hms_billing` are present.

## What it provides

- **`hms.lab.test.type`** (extended): `product_id` (M2O service product) — the billing product for this test.
- **`hms.lab.request`** (extended): `sale_order_id`, `billing_state` (computed), `action_create_lab_bill` — creates draft SO from billable test types (expands panels). "Billed" ribbon prevents double-billing.
- Lab test type form: `product_id` field added.
- Lab request form: "Bill" header button (visible when `state=done` and not yet billed).

## Dependencies

`hms_lab`, `hms_billing` — auto-install bridge.

## Install

Installs automatically when both `hms_lab` and `hms_billing` are present.
