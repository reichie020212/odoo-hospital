# hms_clinical — Entity Relationship Diagram

```mermaid
erDiagram
    hms_consultation {
        int id PK
        varchar name "CONS/YYYY/MM/#### (sequence)"
        int patient_id FK "required"
        int doctor_id FK "required"
        int appointment_id FK "optional"
        datetime date "default now"
        text chief_complaint
        text history
        text examination
        text diagnosis
        text treatment_plan
        selection state "draft | in_progress | done | cancelled"
    }

    hms_vital {
        int id PK
        int consultation_id FK "required, cascade"
        int bp_systolic "mmHg"
        int bp_diastolic "mmHg"
        int heart_rate "bpm"
        float temperature "degrees C"
        int spo2 "percent"
        float weight "kg"
        float height "cm"
        float bmi "computed, stored"
    }

    hms_prescription_line {
        int id PK
        int consultation_id FK "required, cascade"
        int product_id FK "required"
        varchar dosage
        varchar frequency
        int duration_days
        text instructions
    }

    res_partner {
        int id PK
        varchar name
        boolean is_patient
        int consultation_count "computed"
    }

    hr_employee {
        int id PK
        varchar name
        boolean is_doctor
        int patient_count "computed from consultations"
    }

    product_product {
        int id PK
        varchar name
    }

    calendar_event {
        int id PK
        boolean is_appointment
    }

    hms_consultation ||--o{ hms_vital : "vital_ids"
    hms_consultation ||--o{ hms_prescription_line : "prescription_line_ids"
    hms_consultation }o--|| res_partner : "patient_id"
    hms_consultation }o--|| hr_employee : "doctor_id"
    hms_consultation }o--o| calendar_event : "appointment_id"
    hms_prescription_line }o--|| product_product : "product_id"
```

## Relationships

| From | To | Type | Field | Description |
|:-----|:---|:-----|:------|:------------|
| `hms.consultation` | `res.partner` | Many2one | `patient_id` | The patient (required) |
| `hms.consultation` | `hr.employee` | Many2one | `doctor_id` | The attending doctor (required, defaults to current user's employee) |
| `hms.consultation` | `calendar.event` | Many2one | `appointment_id` | Optional link to the originating appointment |
| `hms.consultation` | `hms.vital` | One2many | `vital_ids` | Vital signs recorded during this consultation |
| `hms.consultation` | `hms.prescription.line` | One2many | `prescription_line_ids` | Medications prescribed |
| `hms.prescription.line` | `product.product` | Many2one | `product_id` | The medicine / product prescribed |
| `res.partner` | `hms.consultation` | One2many | `consultation_ids` | All consultations for this patient (inverse of `patient_id`) |

## State machine

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> in_progress : action_start
    in_progress --> done : action_done
    draft --> cancelled : action_cancel
    in_progress --> cancelled : action_cancel
    cancelled --> draft : action_draft
    done --> [*]
```

## Record rules (hms.consultation)

| Rule | Group | Read | Write | Create | Unlink | Domain |
|:-----|:------|:----:|:-----:|:------:|:------:|:-------|
| Read all | `group_hms_user` | Y | - | - | - | `[(1,'=',1)]` |
| Write own | `group_hms_user` | - | Y | Y | - | `[('doctor_id.user_id','=',user.id)]` |
| No unlink | `group_hms_user` | - | - | - | Y | `[(0,'=',1)]` (always false) |
| Full access | `group_hms_manager` | Y | Y | Y | Y | `[(1,'=',1)]` |

## Notes

- `hms.consultation` inherits `mail.thread` and `mail.activity.mixin` for chatter and activity tracking.
- `hms.vital.bmi` is a stored computed field (`weight / (height_m^2)`); returns 0 when weight or height is missing.
- `hms.prescription.line` references `product.product` but creates no stock moves — stock integration is deferred to `hms_pharmacy`.
- `res.partner` and `hr.employee` are shown with only the fields added/extended by `hms_clinical`; see [`hms-base-erd.md`](hms-base-erd.md) for their full `hms_base` extensions.
