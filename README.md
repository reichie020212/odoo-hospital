# Odoo Hospital Management System

A comprehensive Hospital Management System built as custom addons for **Odoo 19 Community Edition**. Covers the full patient lifecycle: registration, appointments, consultations (EMR), lab diagnostics, pharmacy dispensing, inpatient ward management, billing with insurance co-pay, and a patient self-service portal.

## Modules

| Module | Purpose |
| :--- | :--- |
| `hms_base` | Patient/staff extensions on `res.partner` and `hr.employee`, specializations, security groups |
| `hms_appointment` | Medical appointment scheduling on `calendar.event` with 5-state workflow |
| `hms_clinical` | EMR core — consultations, vitals, prescriptions, medical history |
| `hms_billing` | Direct-pay invoicing from consultations via `sale.order` |
| `hms_pharmacy` | Prescription dispensing via `stock.picking` with FEFO expiry tracking |
| `hms_lab` | Lab test requests with panel expansion, results, abnormal-value detection |
| `hms_inpatient` | Ward/bed management, admissions, discharge, daily room-charge CRON |
| `hms_portal` | View-only patient portal (appointments, consultations, vitals) |
| `hms_website` | Public hospital website with doctor profiles, services, and contact page |
| `hms_lab_billing` | Bridge: lab tests → sale.order *(auto-installs)* |
| `hms_pharmacy_billing` | Bridge: dispensed medicines → sale.order *(auto-installs)* |
| `hms_insurance` | Insurance policies, co-pay split billing |

## Quick start with Docker

### One-time setup

```bash
cp .env.example .env
# For dev the default is fine; for prod, edit .env and set a strong POSTGRES_PASSWORD.
```

### Development

The repo is bind-mounted into the container and Odoo runs with `--dev=all`, so Python changes hot-reload and XML changes show up after a module upgrade.

```bash
docker compose up -d              # start in the background
docker compose logs -f odoo       # tail Odoo logs
docker compose down               # stop (keeps volumes)
docker compose down -v            # stop and wipe DB + filestore
```

Open http://localhost:8069, create a database, and install modules. Installing `hms_insurance` pulls in the entire dependency chain — all modules install transitively.

Postgres is exposed on `localhost:5433` (user `odoo`, password from `.env`) so it doesn't conflict with a local Postgres.

### Demo data

Demo data is **not** loaded by default. To install (or upgrade) modules with demo data — realistic sample patients, appointments, consultations, prescriptions, lab requests, etc., useful for evaluation and screenshots — pass `--with-demo` to `odoo-bin`:

```bash
# Dev — fresh DB with demo data (install all modules transitively via hms_insurance)
docker compose run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -d hms_dev -i hms_insurance --with-demo --stop-after-init

# Prod — same, against the prod stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -d hms_prod -i hms_insurance --with-demo --stop-after-init
```

Then start the stack normally with `docker compose up -d`. Omit `--with-demo` (or use `--without-demo=all`) for a clean production database.

### Production

Production bakes all modules into a local image via `Dockerfile` and does not expose Postgres on the host.

```bash
# edit .env with a real POSTGRES_PASSWORD first
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f odoo
```

To upgrade modules after code changes:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build odoo
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -u hms_base --stop-after-init
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Before exposing publicly, set a strong `admin_passwd` and flip `list_db` to `False` in `odoo.conf`.

## Module dependency graph

```
hms_insurance ──► hms_billing ──► hms_clinical ──► hms_appointment ──► hms_base
                                      │                                    │
hms_pharmacy ──────────────────────────┘                                   │
hms_lab ───────────────────────────────┘                                   │
hms_inpatient ─► hms_billing ──────────┘                                   │
hms_portal ────► hms_appointment ──────────────────────────────────────────┘
hms_website ───► hms_appointment ──────────────────────────────────────────┘  (also depends on `website`)

hms_lab_billing ─► hms_lab + hms_billing          (auto-install bridge)
hms_pharmacy_billing ─► hms_pharmacy + hms_billing (auto-install bridge)
```

## Tech stack

- **Python** 3.12 · **Odoo** 19 CE · **PostgreSQL** 16
- **Linter/formatter:** ruff (120-char lines, `py312`)
- **Pre-commit:** trailing-whitespace, check-xml, ruff, ruff-format, secret detection
- **Tests:** 140+ Odoo `TransactionCase` tests across all modules

## Documentation

- Each module has a `README.md` at its root describing models, views, security, and install steps.
- Mermaid ERDs live in `docs/guide/` (committed).
- Plans and blueprints live in `docs/plan/` (gitignored — local working artifacts).

## License

LGPL-3.0 — see [LICENSE](LICENSE).
