# Hospital Management — Appointments (`hms_appointment`)

Medical appointment scheduling on top of `calendar.event`. Appointments are isolated from regular meetings via the `is_appointment` flag, so staff calendars stay clean.

## What it provides

### Models

- **`calendar.event`** (inherited)
  - `is_appointment` — boolean flag distinguishing medical appointments from generic meetings.
  - `patient_id` → `res.partner` (domain `is_patient=True`).
  - `doctor_id` → `hr.employee` (domain `is_doctor=True`).
  - `appointment_type_id` → `hms.appointment.type`.
  - `appointment_state` — selection: draft / confirmed / checked_in / done / cancelled. Transition methods: `action_confirm`, `action_check_in`, `action_done`, `action_cancel`, `action_draft`.
  - Python constraint: when `is_appointment=True`, both `patient_id` and `doctor_id` are required.
  - Onchange: selecting an appointment type pre-fills `duration` from `default_duration`.

- **`hms.appointment.type`** (new)
  - `name` (required, translated), `default_duration` (float, hours), `active`.
  - `product_id` — placeholder, wired by `hms_billing` in Phase 4.

### Views & menus

- **Hospital > Appointments** — dedicated list, calendar (color-coded by status), and form with status bar + action buttons. Default domain filters to `is_appointment=True`.
- **Hospital > Configuration > Appointment Types** — list/form for managing types.
- Minimal extension on the stock `calendar.event` form: shows `is_appointment` toggle and medical fields at the bottom (for users who open a meeting from the Calendar module).

### Security

- `hms.appointment.type`: users read, managers CRUD (same pattern as specializations).
- `calendar.event` access inherited from the `calendar` module.

### Data

- Seed appointment types: General Consultation (30 min), Follow-up (15 min), Vaccination (15 min).

## Dependencies

`hms_base`, `calendar` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_appointment --stop-after-init
```

## Known limitations

- State transitions are simple write operations with no guards (e.g., skipping from draft to done is possible via API). Tighter transition rules can be added if needed.
- The stock calendar form extension uses `//form/sheet` as its xpath anchor. If a future Odoo 19 update removes or restructures the calendar form's `<sheet>`, the view may need adjustment.
