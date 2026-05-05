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
| `hms_lockdown` | Security policy — only admins can manage user passwords; disables the public reset-password flow |

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

# Prod — same, against the prod stack (one-shot run; nginx not needed for init)
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -d hms_prod -i hms_insurance --with-demo --stop-after-init
```

Then start the stack normally with the Production commands below. Omit `--with-demo` (or use `--without-demo=all`) for a clean production database.

### Production

Production bakes all modules into a local image via `Dockerfile` and does not expose Postgres on the host. **Always include `docker-compose.nginx.yml`** in the production stack — once Odoo runs with `--workers >= 1` (the prod default is `--workers=2`), the bus module needs WebSocket traffic forwarded to the gevent worker on port `8072`. nginx in `docker-compose.nginx.yml` does that routing; without it, every `/websocket` request 500s with `RuntimeError: Couldn't bind the websocket`. The Odoo service in `docker-compose.prod.yml` is also started with `--proxy-mode` so it trusts the `X-Forwarded-*` headers nginx sets.

```bash
# edit .env with a real POSTGRES_PASSWORD first
docker compose \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    -f docker-compose.nginx.yml \
    up -d --build

docker compose \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    -f docker-compose.nginx.yml \
    logs -f odoo nginx
```

The nginx service publishes port `80`. Point your upstream (Cloudflare, load balancer, DNS A record) at port `80` on the prod host instead of `8069`. To run alongside another service already on port 80, edit `docker-compose.nginx.yml` and remap (e.g. `"8088:80"`).

To upgrade modules after code changes:

```bash
# 1. Rebuild the Odoo image (picks up new addon code)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build odoo

# 2. Stop the long-running Odoo service (db and nginx stay up)
docker compose \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    -f docker-compose.nginx.yml \
    stop odoo

# 3. Run the one-shot upgrade (no nginx needed for a CLI-only upgrade)
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -d <DB_NAME> -u <module_a>,<module_b> \
         --stop-after-init --no-http

# 4. Bring everything back up
docker compose \
    -f docker-compose.yml \
    -f docker-compose.prod.yml \
    -f docker-compose.nginx.yml \
    up -d
```

If the upstream proxy (Cloudflare, an external nginx, etc.) is already terminating TLS and routing `/websocket` correctly, you can drop `-f docker-compose.nginx.yml` and skip the bundled nginx. `--proxy-mode` from `docker-compose.prod.yml` is still correct in that case — it just trusts headers from your upstream proxy instead of from this nginx.

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

hms_lockdown ─► base + auth_signup (Odoo CE; no internal HMS dependencies)
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
