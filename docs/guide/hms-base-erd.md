# hms_base — Entity Relationship Diagram

```mermaid
erDiagram
    res_partner {
        int id PK
        varchar name
        varchar ref "Patient ID (sequence P/YYYY/#####)"
        boolean is_patient
        date date_of_birth
        int age "computed, non-stored"
        selection gender "male | female | other"
        selection blood_group "a+ | a- | b+ | b- | ab+ | ab- | o+ | o-"
    }

    hr_employee {
        int id PK
        varchar name
        boolean is_doctor
        boolean is_nurse
        int specialization_id FK
        varchar license_no
        int patient_count "computed, placeholder"
    }

    hms_specialization {
        int id PK
        varchar name UK "required, unique"
        varchar code
        text description
        boolean active "default true"
    }

    hms_patient_guardian_rel {
        int patient_id FK
        int guardian_id FK
    }

    res_partner ||--o{ hms_patient_guardian_rel : "patient"
    res_partner ||--o{ hms_patient_guardian_rel : "guardian"
    hr_employee }o--o| hms_specialization : "specialization_id"
```

## Relationships

| From | To | Type | Field | Description |
|:-----|:---|:-----|:------|:------------|
| `hr.employee` | `hms.specialization` | Many2one | `specialization_id` | A doctor/nurse's medical specialty |
| `res.partner` | `res.partner` | Many2many (self) | `guardian_ids` | Links a patient to their guardian(s) via `hms_patient_guardian_rel` |

## Notes

- `res.partner` and `hr.employee` are **inherited** Odoo CE models — the fields shown above are only the ones added by `hms_base`. Core fields (`name`, `email`, `phone`, etc.) are omitted.
- `age` is a non-stored computed field (`@api.depends("date_of_birth")`); it never goes stale.
- `patient_count` on `hr.employee` is a placeholder returning 0; it gets wired by `hms_clinical` in a later phase.
- The native `res.partner.ref` field is reused for patient identifiers, populated from the `hms.patient.ref` sequence on create when `is_patient=True`.
