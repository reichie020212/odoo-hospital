# Hospital Management — Website (`hms_website`)

Public-facing hospital website built on Odoo's CMS. Displays doctor profiles, medical services, and hospital contact information. Integrates with the patient portal via login buttons.

## What it provides

### Pages

- **`/hospital`** — Home page with hero section, services preview, doctor cards, and CTA.
- **`/hospital/doctors`** — Full listing of published doctors with photo, specialization, job title, and bio.
- **`/hospital/services`** — Published medical services with descriptions and duration.
- **`/hospital/contact`** — Hospital address, phone, email, and operating hours from `res.company`.

### Models

- **`hr.employee`** (extended): `website_bio` (HTML), `website_published` (Boolean).
- **`hms.appointment.type`** (extended): `website_description` (HTML), `website_published` (Boolean).

### Security

- All pages use `auth="public"` — accessible without login.
- Controllers fetch data via `sudo()` with only safe fields exposed (name, image, specialization, bio). Internal HR fields are never sent to templates.
- `website_published` flag gates visibility — unpublished doctors/services are hidden from public pages.

### Menus

Website navigation menu under "Hospital" with sub-items: Our Doctors, Services, Contact. "Patient Portal" link in the main menu.

## Dependencies

`website`, `hms_base`, `hms_appointment` — Odoo 19 Community.

## Install

```bash
odoo-bin -d <db> -i hms_website --stop-after-init
```

After install, visit `/hospital` to see the public website. To publish doctors and services, edit each record in the backend and check "Published on Website."

## Known limitations

- No appointment booking form on the website — the "Book Appointment" CTA redirects to the portal login.
- Uses Odoo's default theme. Customize via the Website Builder's drag-and-drop editor.
- No SEO structured data (Schema.org MedicalOrganization) — can be added as a template override.
