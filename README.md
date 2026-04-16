# odoo-hospital

## Running with Docker

This repo ships a Docker Compose stack that runs Odoo 19 CE with the HMS
modules. The base `docker-compose.yml` plus `docker-compose.override.yml`
(auto-loaded) gives you a dev environment; `docker-compose.prod.yml` is an
opt-in production override.

### One-time setup

```bash
cp .env.example .env
# For dev the default is fine; for prod, edit .env and set a strong POSTGRES_PASSWORD.
```

### Development

The repo is bind-mounted into the container at `/mnt/extra-addons/odoo-hospital`
and Odoo runs with `--dev=all`, so Python changes hot-reload and XML changes
show up after a module upgrade.

```bash
docker compose up -d              # start in the background
docker compose logs -f odoo       # tail Odoo logs
docker compose down               # stop (keeps volumes)
docker compose down -v            # stop and wipe DB + filestore
```

Then open http://localhost:8069 and create a database. Install `hms_base`
first; `hms_appointment`, `hms_clinical`, and `hms_billing` depend on it.

Postgres is exposed on `localhost:5433` (user `odoo`, password from `.env`)
for `psql` access — the host port is remapped off 5432 so it does not
conflict with a local Postgres that may already be running.

### Production

Production bakes the HMS modules into a local image via `Dockerfile` and
does not expose Postgres on the host.

```bash
# edit .env with a real POSTGRES_PASSWORD first
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f odoo
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

To upgrade a module after code changes, rebuild the image and run an upgrade:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build odoo
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm odoo \
    odoo -c /etc/odoo/odoo.conf -u hms_base --stop-after-init
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Before exposing a prod instance publicly, override the dev-friendly
defaults in `odoo.conf` — set a strong `admin_passwd` and flip `list_db`
to `False`.
