# Hospital Management — Pharmacy (`hms_pharmacy`)

Prescription dispensing via `stock.picking` with FEFO expiry tracking. A "Dispense" button on a completed consultation creates an outgoing picking from the Pharmacy stock location. When the pharmacist validates the picking, the prescription lines are marked as dispensed.

## What it provides

### Models

- **`product.product`** (extended) — `is_medicine` boolean flag for filtering.
- **`hms.prescription.line`** (extended)
  - `dispensing_state` (pending / dispensed, readonly).
  - `move_id` (M2O `stock.move`) — the stock move that fulfilled this line.
- **`hms.consultation`** (extended)
  - `picking_ids` (O2M `stock.picking`), `dispensing_count` (computed).
  - `action_create_dispensing` — creates an outgoing picking from pending storable prescription lines. Raises if nothing to dispense.
  - `action_view_dispensing` — smart-button navigation.
- **`stock.picking`** (extended)
  - `hms_consultation_id` (M2O `hms.consultation`).
  - `button_validate` override: marks linked prescription lines as `dispensed` after successful validation.

### Views & menus

- Consultation form: "Dispense" header button (visible when `state=done`), Dispensing smart button, `dispensing_state` badge on inline prescription list.
- **Hospital > Configuration > Medicines** — `product.product` filtered by `is_medicine=True`.

### Security

- New group: **Pharmacy User** (under Hospital category, implies `stock.group_stock_user`).
- Pharmacy users can read consultations and read/write prescription lines (to view dispensing state).

### Data

- **Pharmacy** stock location (child of main warehouse, FEFO removal strategy).
- **Dispensing** picking type (outgoing, Pharmacy → Customers, sequence `DISP`).

## Dependencies

`hms_clinical`, `stock`, `product_expiry` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_pharmacy --stop-after-init
```

After install, ensure medicines are created as storable products (`type=product`) with lot tracking enabled for expiry to take effect.

## Known limitations

- Dispensing always creates a quantity of 1 per prescription line. Multi-quantity dispensing (e.g. 30 tablets) would require an additional `quantity` field on `hms.prescription.line`.
- Ward-level satellite pharmacies (inter-warehouse transfers) are not supported — single central pharmacy only.
- The FEFO removal strategy requires medicines to have lot tracking enabled and `expiry_date` set on each lot.
