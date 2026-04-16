# hms_appointment — Entity Relationship Diagram

```mermaid
erDiagram
    calendar_event {
        int id PK
        varchar name "Subject"
        datetime start
        datetime stop
        float duration
        text description
        boolean is_appointment "gates medical fields"
        int patient_id FK "required when is_appointment"
        int doctor_id FK "required when is_appointment"
        int appointment_type_id FK
        selection appointment_state "draft | confirmed | checked_in | done | cancelled"
    }

    res_partner {
        int id PK
        varchar name
        boolean is_patient
    }

    hr_employee {
        int id PK
        varchar name
        boolean is_doctor
        int user_id FK "linked Odoo user"
    }

    hms_appointment_type {
        int id PK
        varchar name "required"
        float default_duration "hours, default 0.5"
        boolean active "default true"
        int product_id FK "service product (added by hms_billing)"
    }

    calendar_event }o--|| res_partner : "patient_id"
    calendar_event }o--|| hr_employee : "doctor_id"
    calendar_event }o--o| hms_appointment_type : "appointment_type_id"
    calendar_event }o--o{ res_partner : "partner_ids (attendees)"
```

## Relationships

| From | To | Type | Field | Description |
|:-----|:---|:-----|:------|:------------|
| `calendar.event` | `res.partner` | Many2one | `patient_id` | The patient this appointment is for (required when `is_appointment=True`) |
| `calendar.event` | `hr.employee` | Many2one | `doctor_id` | The doctor conducting the appointment (required when `is_appointment=True`) |
| `calendar.event` | `hms.appointment.type` | Many2one | `appointment_type_id` | Pre-fills default duration via onchange |
| `calendar.event` | `res.partner` | Many2many | `partner_ids` | Calendar attendees — patient and doctor's user partner are auto-synced here on create/write |

## State machine

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> confirmed : action_confirm
    confirmed --> checked_in : action_check_in
    checked_in --> done : action_done
    draft --> cancelled : action_cancel
    confirmed --> cancelled : action_cancel
    checked_in --> cancelled : action_cancel
    cancelled --> draft : action_draft
    done --> [*]
```

## Notes

- `calendar.event` is an **inherited** Odoo CE model — only the fields added by `hms_appointment` are shown. Core fields (`start`, `stop`, `duration`, `partner_ids`, etc.) exist in the base `calendar` module.
- `res.partner` and `hr.employee` are shown with the subset of fields relevant to appointments; see [`hms-base-erd.md`](hms-base-erd.md) for their full `hms_base` extensions.
- The `is_appointment` boolean isolates medical appointments from regular calendar meetings. Dedicated views filter on `is_appointment=True`.
- Attendee sync: on create/write, `patient_id` and `doctor_id.user_id.partner_id` are auto-added to `partner_ids` so doctors see appointments in their native Odoo/mobile calendar.
- `hms_appointment_type.product_id` is not yet present — it will be wired by `hms_billing` in Phase 4.
