from odoo import _, models
from odoo.exceptions import UserError

_PASSWORD_KEYS = ("password", "new_password")
_DENY_MESSAGE = _(
    "Password changes are restricted to administrators. "
    "Please contact your system administrator if you need a new password."
)


class ResUsers(models.Model):
    _inherit = "res.users"

    def _hms_lockdown_is_password_admin(self):
        return self.env.user.has_group("base.group_system")

    def change_password(self, old_passwd, new_passwd):
        if not self._hms_lockdown_is_password_admin():
            raise UserError(_DENY_MESSAGE)
        return super().change_password(old_passwd, new_passwd)

    def write(self, vals):
        if any(key in vals for key in _PASSWORD_KEYS):
            if self.env.uid in self.ids and not self._hms_lockdown_is_password_admin():
                raise UserError(_DENY_MESSAGE)
        return super().write(vals)
