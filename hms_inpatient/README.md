# Hospital Management — Inpatient (`hms_inpatient`)

Ward and bed management with admissions, discharge, and automated daily room-charge billing via a CRON job.

## What it provides

### Models

- **`hms.ward`** (new) — `name`, `floor`, `gender_restriction` (mixed/male/female), `bed_ids` (O2M), `bed_count`/`available_count` (computed), `active`.
- **`hms.bed`** (new) — `name`, `ward_id`, `bed_type` (standard/semi\_private/private/icu), `state` (available/occupied/cleaning/maintenance), `product_id` (service product for daily room charge), `active`.
- **`hms.admission`** (new) — inherits `mail.thread`, `mail.activity.mixin`.
  - `name` (sequence `ADM/YYYY/MM/####`), `patient_id`, `doctor_id`, `bed_id`, `ward_id` (related, stored).
  - `consultation_id` (optional link), `admission_date`, `discharge_date`, `diagnosis`, `notes`.
  - `state`: draft / admitted / discharged / cancelled.
  - `sale_order_id` — draft SO created on admission for accumulating room charges.
  - `last_charge_date` — idempotency guard for the daily CRON.
  - `action_admit` — marks bed occupied, creates draft SO.
  - `action_discharge` — frees bed, sets discharge date.
  - `_cron_daily_room_charges` — adds one SO line per active admission per day.

### Views & menus

- **Hospital > Admissions** — list + form with status bar, chatter, Room Charges smart button.
- **Hospital > Configuration > Wards** — list/form with inline bed management and occupancy stats.
- **Hospital > Configuration > Beds** — list/form with state badges, search by ward/type/state.

### Security

- HMS users: read wards/beds, read/write/create admissions.
- HMS managers: full CRUD on all three models.

### Data

- Room charge products: Standard ($100), Private ($250), ICU ($500).
- Sample wards: General Ward, ICU.
- Sample beds: G-101, G-102, ICU-01.
- Daily CRON: `HMS: Daily Room Charges` (runs once per day).

## Dependencies

`hms_clinical`, `hms_billing` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_inpatient --stop-after-init
```

## Known limitations

- Doctor visit fees for inpatients are handled manually: create a consultation (via `hms_clinical`) and bill it via `hms_billing`. No automatic per-visit billing from the admission.
- The CRON creates one SO line per day; it does not handle partial-day charges (check-in at 11 PM still bills a full day).
- Bed transfers (moving a patient to a different bed mid-admission) are not supported — discharge and re-admit.
