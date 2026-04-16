# Hospital Management — Billing (`hms_billing`)

Direct-pay invoicing from consultations. A one-click button on a completed consultation creates a draft `sale.order` for the patient, using the service product defined on the appointment type. A "Billed" ribbon prevents double-invoicing.

## What it provides

### Models

- **`hms.consultation`** (extended)
  - `sale_order_id` (M2O `sale.order`, readonly, copy=False).
  - `invoice_ids`, `invoice_count` (computed from `sale_order_id.invoice_ids`).
  - `billing_state` (computed, stored: not\_billed / billed).
  - `action_create_sale_order` — creates a draft SO with one order line; raises if already billed or if the appointment type has no billing product.
  - `action_view_sale_order`, `action_view_invoices` — smart-button navigation.

- **`hms.appointment.type`** (extended)
  - `product_id` (M2O `product.product`, domain `type=service`) — the service product used for billing this appointment type.

### Views

- Consultation form: "Create Invoice Draft" header button (visible only when `state=done` and `billing_state=not_billed`), "Billed" ribbon, Sale Order + Invoices smart buttons.
- Consultation list: `billing_state` badge column.
- Appointment Type form/list: `product_id` field added.

### Security

- HMS users (`group_hms_user`) are granted read/write/create on `sale.order` and `sale.order.line` via explicit `ir.model.access.csv` entries so `action_create_sale_order` doesn't fail with AccessError.

### Data

- Seed service product: "General Consultation Fee" (list price 50.0).
- The "General Consultation" appointment type (from `hms_appointment`) is linked to this product.

## Dependencies

`hms_clinical`, `sale` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_billing --stop-after-init
```

## Design decisions

**Sale access for HMS users:** This module grants HMS users direct model-level access to `sale.order` and `sale.order.line` (read/write/create, no delete). This is the minimum needed for the "Create Invoice Draft" button to work. HMS users will **not** see the Sales application menu unless they are also assigned the Salesman group in Settings. This is intentional — billing is triggered from the Hospital module, not from the Sales module. If full Sales access is needed, a system administrator can assign the Salesman group to HMS users manually.

## Scope exclusions (MVP)

- No insurance partners, co-pay splits, or TPA workflows.
- No pharmacy/stock integration on prescription lines.
- No auto-posting of invoices — the user confirms the draft SO manually via the standard Odoo flow.

## Known limitations

- Billing requires a consultation linked to an appointment whose type has a `product_id`. Consultations created without an appointment link cannot be billed via this button.
