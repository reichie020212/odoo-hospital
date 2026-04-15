# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Hospital Management System custom module for **Odoo 19 Community Edition**.

This is an early-stage scaffold — at time of writing, no Odoo addon modules exist yet. The repo currently contains only Python tooling config and a placeholder `main.py`. Expect to create the first addon from scratch; do not assume module files already exist.

The parent directory is `~/odoo/custom_addons/`, meaning this repo is intended to live inside Odoo's custom addons path. Each Odoo module added here should be a sibling directory with its own `__manifest__.py` and `__init__.py`.

## Division of Labor (Gemini ↔ Claude)

Work on this project is split between Gemini and Claude:

**Gemini — The Architect & Strategist**
- High-level planning, Odoo model/schema design, solving tricky business-logic problems (e.g. hospital billing rules), and generating assets (icons, UI images).
- Produces a step-by-step **Blueprint** for Claude to execute.

**Claude Code — The Executor & Mechanic**
- Writes the boilerplate (Python models, XML views, `ir.model.access.csv`), creates files, runs tools, commits the code.
- Takes the Blueprint from Gemini and implements it flawlessly into the codebase. Does not unilaterally redesign the architecture — on execution-time roadblocks, re-consult Gemini via `/ask gemini` instead of improvising.

### Execution Rules (Claude, on this project)

1. **Follow the Blueprint.** Do not invent complex business logic, add fields, or change database schemas unless explicitly instructed. Implement plans exactly as provided. If the plan is ambiguous, contradicts existing code, or looks wrong, re-consult the Architect (`/ask gemini`) — don't improvise.
2. **Respect Odoo's layout.** Create/modify/delete files as needed, but strictly maintain the standard Odoo 19 structure: `models/` for Python, `views/` for XML, `security/` for `ir.model.access.csv` and record rules, `data/` for seed data. Wire new files through `__init__.py` and list XML/CSV assets in `__manifest__.py`.
3. **Tooling is mandatory.** After writing or modifying Python, run both `uv run ruff check . --fix` and `uv run ruff format .` before committing — in that order. Fix any remaining issues manually and re-run until clean. For XML changes, pre-commit's `check-xml` validates on commit; don't skip hooks.
4. **Git protocol.** Once a component is built and lints clean, stage and commit with a descriptive, semantic commit message using a conventional-commits prefix (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`). Always sign with both `-s` and `-S` (see the Git commits section below). No self-attribution.
5. **Fail fast.** If a shell command fails with a non-obvious error, or Odoo returns a traceback you cannot resolve in one focused attempt, stop and report the error to Red with the full output so the Architect can be consulted. Do not silently retry, disable checks (`--no-verify`, commenting out tests), or hack around the error.

**Workflow**
1. Red consults Gemini → receives a Blueprint.
2. Red hands the Blueprint to Claude → Claude executes it per the Execution Rules above.
3. On design-level blockers mid-execution, Claude re-consults Gemini (`/ask gemini`) before proceeding.

## Tech stack & tooling

- **Python**: 3.12 (pinned in `.python-version`, matching Odoo 19's target).
- **Framework**: Odoo 19 Community.
- **Package manager**: `uv` — `uv.lock` is committed, so use `uv sync` rather than `pip install`.
- **Linter/formatter**: `ruff` (configured in `pyproject.toml`, line length 120, `target-version = "py312"`).
- **Pre-commit**: trailing-whitespace, end-of-file-fixer, check-yaml, check-xml, check-added-large-files, ruff, ruff-format.

## Common commands

```bash
# Install dev dependencies into .venv
uv sync

# Run the placeholder entry point
uv run python main.py

# Lint / format directly
uv run ruff check .
uv run ruff format .

# Install pre-commit hooks (once per clone)
uv run pre-commit install

# Run all hooks against all files
uv run pre-commit run --all-files

# Run a specific hook against changed files
uv run pre-commit run ruff --files <path>
uv run pre-commit run ruff-format --files <path>
```

No tests exist yet and no test runner is configured — when adding tests for Odoo modules, they'll run via Odoo's own test harness (`odoo-bin -i <module> --test-enable --stop-after-init`), not pytest against this repo.

## Coding standards for Odoo modules

When adding an Odoo addon, follow the standard Odoo 19 layout:

- `models/` — Python business logic; inherit from `models.Model` or `models.TransientModel`.
- `views/` — XML for backend views (form, tree, kanban) and menus.
- `security/` — `ir.model.access.csv` and XML record rules.
- `data/` — XML for default data or sequences.
- `__manifest__.py`, `__init__.py`, and `README.md` at the module root.

Conventions:

1. **File naming** — Python files named after the model (`model_name.py`); XML view files named `model_name_views.xml`.
2. **No speculative JavaScript** — don't introduce OWL components or frontend JS unless explicitly asked.
3. **PEP8-compliant, 120-char lines** — pre-commit will catch formatting, but write clean code up front.
4. **Every module must have a `README.md`.** Create one at the module root (sibling of `__manifest__.py`) the moment a new module is scaffolded, and **keep it updated** whenever the module's purpose, models, views, security model, or external dependencies change. This README is committed and ships with the module — it is not optional and is distinct from the "no auto-README in `docs/plan/` or `docs/guide/`" rule above. Minimum sections: module name + one-line purpose, what it provides (models/views/menus added), dependencies, and any setup/configuration steps.

## Documentation conventions

All Markdown documentation lives under `docs/` and is split into two folders with **opposite commit policies**:

- `docs/plan/` — **Plans / Blueprints. NOT committed.** Whenever Claude or Gemini drafts a plan, blueprint, design sketch, investigation note, or any "what we're about to do" document, write it as a Markdown file under `docs/plan/`. Name the file after the thing being planned, in `kebab-case.md` (e.g. `patient-model.md`, `appointment-billing-rules.md`, `migrate-to-postgres-17.md`). This folder is gitignored — plans are working artifacts shared between Red, Claude, and Gemini, not project deliverables.
- `docs/guide/` — **Guides. Committed.** Anything intended for a reader/user (how-to-use, setup guides, module documentation, architecture overviews, runbooks) goes here as `kebab-case.md`. These files **must** be tracked by git and shipped with the repo.

Rules:
1. Never write a plan to the repo root or to `docs/guide/` by mistake — plans belong in `docs/plan/` and stay local.
2. Never put a guide in `docs/plan/` — it would be invisible to anyone who clones the repo.
3. If the right folder does not yet exist, create it (`mkdir -p docs/plan` or `mkdir -p docs/guide`) before writing the file.
4. Do not auto-create README.md / index.md inside these folders unless explicitly asked.

## Git commits

- **Always sign commits with both `-s` and `-S`** (e.g. `git commit -s -S -m "..."`). `-s` adds the `Signed-off-by` trailer; `-S` GPG-signs the commit. This applies to every commit in this repo, no exceptions.
- **Do not add yourself as a co-author.** No `Co-Authored-By: Claude ...` trailer, no "Generated with Claude Code" footer, no attribution of any kind in the commit message. The `Signed-off-by` line from `-s` belongs to Red, not to you.

## Known quirks

- A directory literally named `--force/` exists at the repo root. It contains a venv layout (`bin/`, `lib/`, `pyvenv.cfg`, `CACHEDIR.TAG`) and appears to be the result of an accidental `uv venv --force` where `--force` got interpreted as the target path. It is **not** ignored by `.gitignore`. Leave it alone unless Red asks to clean it up — don't delete on your own initiative.
- The canonical venv is `.venv/`, which `.gitignore` already covers.
