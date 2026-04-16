# hms_billing — Entity Relationship Diagram

```mermaid
erDiagram
    hms_consultation {
        int id PK
        varchar name
        int patient_id FK
        int doctor_id FK
        int appointment_id FK
        selection state "draft | in_progress | done | cancelled"
        int sale_order_id FK "readonly, copy=False (added by hms_billing)"
        selection billing_state "not_billed | billed (computed, stored)"
        int invoice_count "computed"
    }

    sale_order {
        int id PK
        int partner_id FK "patient"
        varchar origin "consultation ref"
    }

    sale_order_line {
        int id PK
        int order_id FK
        int product_id FK "service product"
        float product_uom_qty
    }

    account_move {
        int id PK
        varchar name "invoice number"
    }

    hms_appointment_type {
        int id PK
        varchar name
        float default_duration
        int product_id FK "service product (added by hms_billing)"
    }

    product_product {
        int id PK
        varchar name
        selection type "service"
    }

    hms_consultation ||--o| sale_order : "sale_order_id"
    hms_consultation }o--o{ account_move : "invoice_ids (via SO)"
    sale_order ||--o{ sale_order_line : "order_line"
    sale_order_line }o--|| product_product : "product_id"
    sale_order ||--o{ account_move : "invoice_ids"
    hms_appointment_type }o--o| product_product : "product_id"
```

## Billing workflow

```mermaid
flowchart LR
    A[Consultation state=done] -->|"Create Invoice Draft"| B[Draft sale.order]
    B -->|"User confirms SO"| C[Confirmed SO]
    C -->|"Create Invoice from SO"| D[account.move draft]
    D -->|"Post invoice"| E[Posted invoice]
```

## Relationships

| From | To | Type | Field | Description |
|:-----|:---|:-----|:------|:------------|
| `hms.consultation` | `sale.order` | Many2one | `sale_order_id` | The draft SO created for this consultation |
| `hms.consultation` | `account.move` | Many2many | `invoice_ids` | Computed from `sale_order_id.invoice_ids` |
| `sale.order` | `res.partner` | Many2one | `partner_id` | The patient being billed |
| `sale.order.line` | `product.product` | Many2one | `product_id` | The billing product (service) |
| `hms.appointment.type` | `product.product` | Many2one | `product_id` | The default billing product for this type |

## Notes

- `sale.order`, `sale.order.line`, and `account.move` are stock Odoo CE models — not created by this module, only referenced.
- `hms.consultation` and `hms.appointment.type` fields shown here are only those **added by `hms_billing`**; see [`hms-clinical-erd.md`](hms-clinical-erd.md) and [`hms-appointment-erd.md`](hms-appointment-erd.md) for their full field lists.
- The billing flow is manual: `action_create_sale_order` creates a draft SO, but the user must confirm the SO and create/post the invoice via standard Odoo workflows.
