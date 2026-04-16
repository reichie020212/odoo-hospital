# Hospital Management — Clinical / EMR (`hms_clinical`)

The EMR core. Introduces consultations with chatter and activities, standard vital-sign recording, and prescription lines for medication orders. Also wires the patient-count smart button on employees and adds a Medical History page on the patient form.

## What it provides

### Models

- **`hms.consultation`** (new) — inherits `mail.thread`, `mail.activity.mixin`.
  - `name` (sequence `CONS/YYYY/MM/####`), `patient_id`, `doctor_id` (defaults to current user's employee if they're a doctor), `appointment_id`, `date`.
  - Clinical text fields: `chief_complaint`, `history`, `examination`, `diagnosis`, `treatment_plan`.
  - `state`: draft / in\_progress / done / cancelled with action methods.
  - One2many: `vital_ids`, `prescription_line_ids`.

- **`hms.vital`** (new) — one2many from consultation.
  - `bp_systolic`, `bp_diastolic`, `heart_rate`, `temperature` (°C), `spo2` (%), `weight` (kg), `height` (cm), `bmi` (computed, stored).

- **`hms.prescription.line`** (new) — one2many from consultation.
  - `product_id` → `product.product`, `dosage`, `frequency`, `duration_days`, `instructions`.
  - No stock integration (deferred to `hms_pharmacy`).

- **`res.partner`** (extended) — `consultation_ids` (o2m), `consultation_count` (computed), `action_view_consultations` smart button.

- **`hr.employee`** (extended) — `_compute_patient_count` now counts distinct patients from consultations; `action_view_patients` opens a filtered partner list.

### Views & menus

- **Hospital > Patients** — `res.partner` filtered by `is_patient=True`.
- **Hospital > Consultations** — list / kanban / form with status bar, chatter, inline vitals and prescription trees.
- **Medical History** page on the patient form (read-only consultation list).
- **Consultations** smart button on patient records.

### Security

- `ir.model.access.csv`: users read/write/create consultations, vitals, and prescription lines; managers also unlink.
- Record rules on `hms.consultation`:
  - **Read:** all HMS users can read all consultations (clinical continuity).
  - **Write/Create:** doctors can only modify their own consultations.
  - **Unlink:** managers only.

### Data

- Sequence `hms.consultation` (`CONS/YYYY/MM/####`).

## Dependencies

`hms_appointment`, `product` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_clinical --stop-after-init
```

## Known limitations

- State transitions are simple write operations with no guards preventing state skipping via API.
- Prescription lines reference `product.product` but no stock moves are created. Stock integration is deferred to `hms_pharmacy`.
