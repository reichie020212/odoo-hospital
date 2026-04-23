# Hospital Management — Insurance (`hms_insurance`)

Insurance policy management and co-pay split billing. When a patient has an active insurance policy, billing actions automatically add a negative "Insurance Discount" line to the sale order, reducing the patient's total to their co-pay.

## What it provides

### Models

- **`res.partner`** (extended): `is_insurance_company` flag, `insurance_policy_ids` (O2M).
- **`hms.insurance.policy`** (new): `name` (policy number), `patient_id`, `insurance_company_id`, `policy_type` (individual/corporate), `coverage_percentage` (default 80%), `valid_from`, `valid_until`, `active`. Helper method `get_active_policy(patient_id)` returns the first valid policy.
- **`hms.consultation`** (extended): `action_create_sale_order` is overridden to call `_apply_insurance_discount` after SO creation. Adds a negative line (`Insurance Discount` product) equal to `total * coverage_percentage / 100`.

### Views & menus

- **Hospital > Insurance Policies** — list/form with patient, insurer, coverage %, validity dates.
- **Patient form** — "Insurance" page showing linked policies (read-only list).
- **Partner form** — "Insurance Settings" page for non-patients with `is_insurance_company` toggle.

### Security

- HMS users: read policies.
- HMS managers: full CRUD on policies.

### Data

- Seed product: "Insurance Discount" (service, list price 0).

## Dependencies

`hms_billing` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_insurance --stop-after-init
```

## How it works

1. Create an insurance company (mark a `res.partner` as `is_insurance_company=True`).
2. Create a policy linking a patient to the insurer with a coverage percentage and validity period.
3. When the doctor clicks "Create Invoice Draft" on a completed consultation, the system checks for an active policy.
4. If found, a negative SO line is added: `-(total * coverage%)`. The patient's net bill = their co-pay.

## Known limitations

- The discount is a single negative line on the patient's SO. Insurer invoicing (collecting the insurer's share) is not automated — create a manual invoice or batch process for the insurer.
- Pre-authorization workflow (`hms.insurance.preauth`) is not yet implemented — all covered consultations are auto-discounted.
- Only applies to consultation billing (`action_create_sale_order` in `hms_billing`). Lab and pharmacy billing bridges would need separate overrides to apply insurance discounts.
