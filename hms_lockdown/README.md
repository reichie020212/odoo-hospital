# Hospital Management — Lockdown (`hms_lockdown`)

Security-policy module that disables self-service password changes. Only Settings administrators (`base.group_system`) can set or change passwords from this point forward.

## What it provides

### Policy enforcement on `res.users`

- **`change_password(old, new)`** — overridden. Raises `UserError` whenever the calling user is not in `base.group_system`. This blocks the "Change My Password" flow exposed in the user preferences dropdown.
- **`write(vals)`** — overridden. When `password` (or `new_password`) appears in the write values **and** the current user is updating their own record **and** they are not in `base.group_system`, raises `UserError`. This catches every direct write path (programmatic, RPC, etc.).

The override is intentionally narrow:
- Admin-driven password resets via **Settings > Users** still work — admins are in `base.group_system`.
- Internal flows that run as `OdooBot` / installer continue to work — those run with `base.group_system` as well.
- Non-self updates (admin changing user-B's password) are unaffected because the self-update guard (`self.env.uid in self.ids`) doesn't trip.

### Public reset-password flow disabled

`data/disable_reset_password.xml` sets the system parameter `auth_signup.reset_password` to `False` on install. This:
- Removes the **"Reset Password"** link from the login screen.
- Returns *access denied* on `/web/reset_password`.

The record is `noupdate="1"`, so the parameter is only set on first install. A Settings admin can re-enable the public reset flow at any time via **Settings > Technical > Parameters > System Parameters** by flipping the value back to `True`.

## Models

This module **adds no new models**. It only inherits and extends `res.users`.

## Security

No new groups, ACLs, or record rules. The module relies on the existing `base.group_system` group as the gate.

## Dependencies

- `base` — for `res.users`.
- `auth_signup` — supplies the `auth_signup.reset_password` system parameter.

## Install

```bash
odoo-bin -d <db> -i hms_lockdown --stop-after-init
```

## Operator notes

- **Recovering a forgotten password.** With this module installed, end users cannot recover their own password. A Settings administrator must reset it from **Settings > Users**. Document this in your runbook before installing on production.
- **Re-enabling self-service.** Uninstall the module *or* set `auth_signup.reset_password` back to `True` and remove the model overrides (uninstall is cleaner). Uninstall does **not** automatically restore the `auth_signup.reset_password` parameter — flip it back manually.
- **Demo data.** None — this is a policy module, not a data module. The existing `hms_base` and `hms_portal` demo logins demonstrate the policy after install.

## Known limitations

- The "Send Password Reset Email" admin button on the user form (`action_reset_password`) still sends a signup email. The email arrives, but the link inside lands on `/web/reset_password` which is now blocked. Consider hiding that button if it confuses operators.
- This module does not enforce password complexity — it only restricts *who* can change a password. Pair with Odoo's password-policy hooks if complexity rules are needed.
