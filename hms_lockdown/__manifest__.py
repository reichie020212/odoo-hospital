{
    "name": "Hospital Management — Lockdown",
    "version": "19.0.1.0.0",
    "summary": "Disable self-service password changes; only administrators can manage user passwords.",
    "description": """
Hospital Management — Lockdown
==============================

Restricts password management to Settings administrators (`base.group_system`):

* Blocks the user-preferences "Change My Password" flow for non-admins.
* Blocks any direct write to ``res.users.password`` performed by the user on
  themselves when they are not a Settings administrator.
* Disables the public "Reset password" / "Forgot password?" flow by setting the
  ``auth_signup.reset_password`` system parameter to ``False`` on install.

Settings administrators retain full ability to set or reset any user's password
from **Settings > Users**.
""",
    "category": "Hospital",
    "license": "LGPL-3",
    "author": "Hospital Management System",
    "depends": ["base", "auth_signup"],
    "data": [
        "data/disable_reset_password.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
