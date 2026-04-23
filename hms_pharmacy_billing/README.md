# Hospital Management — Pharmacy Billing (`hms_pharmacy_billing`)

Bridge module between `hms_pharmacy` and `hms_billing`. When a dispensing picking is validated, each dispensed product is automatically added as a sale order line to the consultation's existing SO (or a new draft SO is created).

Auto-installs when both `hms_pharmacy` and `hms_billing` are present.

## What it provides

- **`stock.picking`** (extended): `button_validate` override adds dispensed products to the consultation's `sale_order_id` as SO lines with the dispensed quantity.
- If the consultation doesn't have a linked SO yet, one is created automatically.

## Dependencies

`hms_pharmacy`, `hms_billing` — auto-install bridge.

## Install

Installs automatically when both `hms_pharmacy` and `hms_billing` are present.
