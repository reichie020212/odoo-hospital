# hms_inpatient — Entity Relationship Diagram

```mermaid
erDiagram
    hms_ward {
        int id PK
        varchar name "required"
        varchar floor
        selection gender_restriction "mixed | male | female"
        int bed_count "computed"
        int available_count "computed"
        boolean active
    }

    hms_bed {
        int id PK
        varchar name "required"
        int ward_id FK "required"
        selection bed_type "standard | semi_private | private | icu"
        selection state "available | occupied | cleaning | maintenance"
        int product_id FK "room charge service product"
        boolean active
    }

    hms_admission {
        int id PK
        varchar name "ADM/YYYY/MM/#### (sequence)"
        int patient_id FK "required"
        int doctor_id FK "required"
        int bed_id FK "required"
        int ward_id FK "related, stored"
        int consultation_id FK "optional"
        datetime admission_date
        datetime discharge_date
        text diagnosis
        text notes
        selection state "draft | admitted | discharged | cancelled"
        int sale_order_id FK "draft SO for room charges"
        date last_charge_date "CRON idempotency guard"
    }

    sale_order {
        int id PK
        int partner_id FK "patient"
    }

    product_product {
        int id PK
        varchar name "room charge product"
    }

    res_partner {
        int id PK
        boolean is_patient
        selection gender
    }

    hr_employee {
        int id PK
        boolean is_doctor
    }

    hms_ward ||--o{ hms_bed : "bed_ids"
    hms_bed }o--o| product_product : "product_id"
    hms_admission }o--|| hms_bed : "bed_id"
    hms_admission }o--|| hms_ward : "ward_id (related)"
    hms_admission }o--|| res_partner : "patient_id"
    hms_admission }o--|| hr_employee : "doctor_id"
    hms_admission }o--o| sale_order : "sale_order_id"
```

## Admission workflow

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> admitted : action_admit
    admitted --> discharged : action_discharge
    draft --> cancelled : action_cancel
    admitted --> cancelled : action_cancel
    cancelled --> draft : action_draft
    discharged --> [*]

    state "admitted" as admitted
    note right of admitted
        Bed → occupied
        Draft SO created
        CRON adds daily charges
    end note

    state "discharged" as discharged
    note right of discharged
        Bed → cleaning
        discharge_date set
    end note
```

## Daily room-charge CRON

```mermaid
flowchart LR
    A[CRON runs daily] --> B{For each admitted admission}
    B --> C{last_charge_date < today?}
    C -->|Yes| D{Bed has product_id?}
    D -->|Yes| E[Add SO line for today]
    E --> F[Update last_charge_date]
    C -->|No| G[Skip - already charged]
    D -->|No| G
```

## Safety checks

- **Bed availability:** `action_admit` raises if bed state != `available`.
- **Gender restriction:** `action_admit` raises if patient gender doesn't match ward's `gender_restriction` (unless `mixed`).
- **CRON idempotency:** `last_charge_date` guard prevents duplicate charges if the CRON runs twice.

## Notes

- `sale.order`, `product.product`, `res.partner`, `hr.employee` are stock Odoo CE models; only fields relevant to inpatient are shown.
- Doctor visit fees are handled outside this module: create a consultation (hms_clinical) + bill it (hms_billing). No per-visit automation in hms_inpatient.
- Bed transfers mid-admission are not supported — discharge and re-admit to a new bed.
