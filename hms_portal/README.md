# Hospital Management — Patient Portal (`hms_portal`)

View-only patient portal. Patients log in and see their appointments, consultations (with vitals and prescriptions). No create or modify capabilities.

## What it provides

### Portal pages

- **My Appointments** (`/my/appointments`) — table of the patient's medical appointments with date, doctor, type, and status badge. Click through to a detail page.
- **My Consultations** (`/my/consultations`) — table of consultations with reference, date, doctor, diagnosis excerpt, and status. Detail page shows vitals and prescription lines.
- **Portal homepage** — appointment and consultation counters added to the standard Odoo portal home.

### Security

- Record rules restrict portal users (`base.group_portal`) to records where `patient_id = user.partner_id`.
- Model-level read access granted for: `calendar.event`, `hms.consultation`, `hms.vital`, `hms.prescription.line`, `hms.appointment.type`.
- Controllers use `sudo()` for querying, with manual partner-ID checks on detail pages as a defence-in-depth layer.

## Dependencies

`portal`, `hms_appointment`, `hms_clinical` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_portal --stop-after-init
```

After install, create a portal user for a patient: go to **Settings > Users**, create a user with the patient's `res.partner` as the linked partner, and assign the **Portal** access rights. The patient can then log in at `/my`.

## Known limitations

- View-only: patients cannot request, reschedule, or cancel appointments from the portal.
- Lab results are not shown (requires `hms_lab` as a dependency — can be added as a separate portal extension).
- Invoice viewing depends on `account`'s built-in portal, which is already available when `hms_billing` is installed.
- No pagination on list pages yet — all records are displayed. For high-volume deployments, add Odoo's `portal_pager`.
