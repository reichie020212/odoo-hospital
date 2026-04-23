# Hospital Management — Laboratory (`hms_lab`)

Lab test requests with panel expansion, result entry, abnormal-value flagging, and a four-state validation workflow. Doctors order tests from a consultation; lab technicians collect samples, enter results, and validate.

## What it provides

### Models

- **`hms.lab.test.type`** (new)
  - `name`, `code`, `unit`, `normal_range_min`, `normal_range_max`, `active`.
  - `is_panel` — when True, groups child test types (e.g. CBC → WBC, RBC, Platelets, Hematocrit).
  - `parent_id` / `child_ids` — self-referential hierarchy for panels.

- **`hms.lab.request`** (new) — inherits `mail.thread`, `mail.activity.mixin`.
  - `name` (sequence `LAB/YYYY/MM/####`), `patient_id`, `doctor_id`, `consultation_id`, `date`.
  - `state`: draft / collected / processing / done / cancelled.
  - `test_type_ids` (M2M) — ordered tests (panels or individual).
  - `result_ids` (O2M `hms.lab.result`).
  - `action_generate_results` — expands panels into individual result lines, skips duplicates.

- **`hms.lab.result`** (new)
  - `request_id`, `test_type_id` (individual tests only), `value`, `value_text`, `unit` (related), `normal_range_min/max` (related).
  - `is_abnormal` — stored computed boolean; True when value falls outside the test type's normal range.

- **`hms.consultation`** (extended)
  - `lab_request_ids` (O2M), `lab_request_count` (computed).
  - `action_create_lab_request` — creates a request pre-filled from the consultation.
  - Lab Request smart button + "Request Lab Tests" header button.

### Views & menus

- **Hospital > Lab Requests** — list + form with status bar, ordered-tests M2M tags, "Generate Result Lines" button, inline result entry with abnormal flag.
- **Hospital > Configuration > Lab Test Types** — list/form with panel child management.
- Consultation form: "Request Lab Tests" button + Lab Requests smart button.

### Security

- New group: **Lab Technician** (under Hospital category, implies `base.group_user`).
- Lab techs can read/write requests and results, read test types. Cannot create test types (manager only).
- HMS users (doctors) can read/write/create requests and results.

### Data

- Sequence `hms.lab.request` (`LAB/YYYY/MM/####`).
- Seed test types: Blood Glucose, Hemoglobin, Urine Analysis.
- Seed panel: CBC (WBC, RBC, Platelets, Hematocrit).

## Dependencies

`hms_clinical` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_lab --stop-after-init
```

## Known limitations

- Panel expansion is manual (click "Generate Result Lines"); not triggered automatically on save.
- No billing integration for lab tests yet — can be added by extending `hms_billing` to create SO lines from lab requests.
- The "Validate Results" (done) transition is not restricted to a separate "Head of Lab" group; any HMS user or lab tech can validate.
