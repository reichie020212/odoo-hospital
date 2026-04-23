# hms_pharmacy — Entity Relationship Diagram

```mermaid
erDiagram
    hms_consultation {
        int id PK
        varchar name
        int picking_ids "O2M stock.picking (added by hms_pharmacy)"
        int dispensing_count "computed"
    }

    hms_prescription_line {
        int id PK
        int consultation_id FK
        int product_id FK
        float qty "default 1.0 (added by hms_clinical)"
        selection dispensing_state "pending | dispensed (added by hms_pharmacy)"
        int move_id FK "stock.move (added by hms_pharmacy)"
    }

    stock_picking {
        int id PK
        int picking_type_id FK "Dispensing type"
        int partner_id FK "patient"
        int hms_consultation_id FK "copy=True for backorders"
        varchar origin "consultation ref"
        selection state "draft | confirmed | assigned | done | cancel"
    }

    stock_move {
        int id PK
        int picking_id FK
        int product_id FK
        float product_uom_qty
    }

    product_product {
        int id PK
        varchar name
        selection type "product | consu | service"
        boolean is_medicine "added by hms_pharmacy"
    }

    hms_consultation ||--o{ stock_picking : "picking_ids"
    hms_consultation ||--o{ hms_prescription_line : "prescription_line_ids"
    hms_prescription_line }o--o| stock_move : "move_id"
    stock_picking ||--o{ stock_move : "move_ids"
    stock_move }o--|| product_product : "product_id"
    hms_prescription_line }o--|| product_product : "product_id"
    stock_picking }o--|| hms_consultation : "hms_consultation_id"
```

## Dispensing workflow

```mermaid
flowchart LR
    A[Consultation state=done] -->|"Dispense button"| B[stock.picking created]
    B -->|"action_confirm + action_assign"| C[Picking assigned/waiting]
    C -->|"Pharmacist validates"| D[Picking state=done]
    D -->|"button_validate override"| E[prescription lines → dispensed]
```

## Notes

- `stock.picking`, `stock.move`, and `product.product` are stock Odoo CE models — only fields added by `hms_pharmacy` are shown.
- `hms_consultation_id` on `stock.picking` uses `copy=True` so backorder pickings retain the consultation link.
- The Pharmacy stock location uses FEFO removal strategy (via `product_expiry`) to consume nearest-expiry lots first.
- `hms.prescription.line.qty` is defined in `hms_clinical` (default 1.0) and used by `hms_pharmacy` for `product_uom_qty` on stock moves.
- Service products are skipped during dispensing — only storable (`product`) and consumable (`consu`) products generate stock moves.
