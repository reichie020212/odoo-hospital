# hms_lab — Entity Relationship Diagram

```mermaid
erDiagram
    hms_lab_test_type {
        int id PK
        varchar name "required"
        varchar code
        boolean is_panel "groups child tests"
        int parent_id FK "parent panel"
        float normal_range_min
        float normal_range_max
        varchar unit
        boolean active
    }

    hms_lab_request {
        int id PK
        varchar name "LAB/YYYY/MM/#### (sequence)"
        int patient_id FK "required"
        int doctor_id FK "required"
        int consultation_id FK "optional"
        datetime date
        selection state "draft | collected | processing | done | cancelled"
    }

    hms_lab_result {
        int id PK
        int request_id FK "required, cascade"
        int test_type_id FK "required, individual only"
        float value
        varchar value_text "non-numeric results"
        varchar unit "related"
        float normal_range_min "related"
        float normal_range_max "related"
        boolean is_abnormal "computed, stored"
    }

    hms_consultation {
        int id PK
        int lab_request_count "computed (added by hms_lab)"
    }

    res_partner {
        int id PK
        boolean is_patient
    }

    hr_employee {
        int id PK
        boolean is_doctor
    }

    hms_lab_test_type ||--o{ hms_lab_test_type : "parent_id / child_ids"
    hms_lab_request }o--|| res_partner : "patient_id"
    hms_lab_request }o--|| hr_employee : "doctor_id"
    hms_lab_request }o--o| hms_consultation : "consultation_id"
    hms_lab_request }o--o{ hms_lab_test_type : "test_type_ids (M2M)"
    hms_lab_request ||--o{ hms_lab_result : "result_ids"
    hms_lab_result }o--|| hms_lab_test_type : "test_type_id"
```

## Request workflow

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> collected : action_collect
    collected --> processing : action_process
    processing --> done : action_done
    draft --> cancelled : action_cancel
    collected --> cancelled : action_cancel
    processing --> cancelled : action_cancel
    cancelled --> draft : action_draft
    done --> [*]
```

## Panel expansion

```mermaid
flowchart LR
    A["Doctor orders CBC (panel)"] -->|"Generate Results"| B["WBC result line"]
    A --> B2["RBC result line"]
    A --> B3["Platelets result line"]
    A --> B4["Hematocrit result line"]
    B -->|"Tech enters value"| C["is_abnormal computed"]
```

## Notes

- `hms.lab.test.type` is self-referential: panels (`is_panel=True`) have `child_ids`; individual tests may have a `parent_id`.
- `action_generate_results` is state-gated to draft/collected only. It expands panels and skips duplicates.
- `is_abnormal` is a stored compute: True when `value` falls outside `[normal_range_min, normal_range_max]`. Qualitative results (`value_text`) require manual toggle.
- `hms.lab.result` records cascade-delete with their parent `hms.lab.request`.
