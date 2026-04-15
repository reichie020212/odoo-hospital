# Hospital Management — Base (`hms_base`)

Foundation module for the Hospital Management System. Extends `res.partner` with patient demographics and `hr.employee` with clinical-staff flags, introduces the `hms.specialization` master model, and defines the Hospital application security groups.

## What it provides

### Models

- **`res.partner`** (inherited)
  - `is_patient` — flag distinguishing patients from other contacts.
  - `date_of_birth`, `age` (non-stored computed), `gender`, `blood_group`.
  - `guardian_ids` — many2many to `res.partner`, linking a patient to guardians.
  - On create, the native `ref` field is populated from the `hms.patient.ref` sequence (`P/YYYY/#####`) whenever `is_patient=True`.

- **`hr.employee`** (inherited)
  - `is_doctor`, `is_nurse`.
  - `specialization_id` → `hms.specialization`.
  - `license_no`.
  - `patient_count` smart button — **placeholder** returning 0 until `hms_clinical` overrides the compute to count real consultations.

- **`hms.specialization`** (new)
  - `name` (required, translated, unique), `code`, `description`, `active`.

### Views & menus

- Medical page on the partner form, gated by `is_patient`, and a "Patients" filter on the partner search.
- Medical page on the employee form with Doctor/Nurse toggles and specialization; `Doctors` / `Nurses` filters on the employee search.
- **Hospital** top-level application menu.
- **Hospital → Configuration → Specializations** (visible to Hospital Manager only).

### Security

- Module category: **Hospital**.
- Groups:
  - `group_hms_user` — clinical staff; implies `base.group_user`.
  - `group_hms_manager` — implies `group_hms_user`; granted to the admin user on install.
- `ir.model.access.csv`: users read specializations; managers have full CRUD.

### Data

- Sequence `hms.patient.ref` (`P/YYYY/#####`).
- Seed specializations: General Medicine, Pediatrics, Cardiology, Obstetrics & Gynecology, Orthopedics, Dermatology.

## Dependencies

`contacts`, `hr`, `mail` — all Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_base --stop-after-init
```

After install, assign **Hospital / User** or **Hospital / Manager** to clinical users via **Settings → Users & Companies → Users**.

## Known limitations

- `patient_count` smart button returns 0 until `hms_clinical` is installed.
- A partner flagged `is_patient=True` *after* creation (via write) does not auto-receive a sequence-backed `ref`. Set `ref` manually, or flag the patient at creation time.
