from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsLockdown(TransactionCase):
    """Verify that non-admin users cannot self-change passwords, while
    Settings administrators retain full control."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_group = cls.env.ref("base.group_user")
        cls.system_group = cls.env.ref("base.group_system")

        cls.regular_user = cls.env["res.users"].create(
            {
                "name": "Regular Lockdown User",
                "login": "lockdown_regular",
                "password": "lockdown_regular_pwd",
                "group_ids": [(6, 0, [cls.user_group.id])],
            }
        )
        cls.password_admin = cls.env["res.users"].create(
            {
                "name": "Lockdown Admin",
                "login": "lockdown_admin",
                "password": "lockdown_admin_pwd",
                "group_ids": [(6, 0, [cls.user_group.id, cls.system_group.id])],
            }
        )

    def test_non_admin_change_password_blocked(self):
        with self.assertRaises(UserError):
            self.regular_user.with_user(self.regular_user).change_password("lockdown_regular_pwd", "new_pwd")

    def test_non_admin_self_write_password_blocked(self):
        with self.assertRaises(UserError):
            self.regular_user.with_user(self.regular_user).write({"password": "new_pwd"})

    def test_non_admin_self_write_other_fields_still_works(self):
        """Lockdown only targets the password field; other self-edits remain allowed."""
        self.regular_user.with_user(self.regular_user).write({"signature": "Hello"})
        self.assertEqual(self.regular_user.signature, "Hello")

    def test_admin_can_set_other_user_password(self):
        self.regular_user.with_user(self.password_admin).write({"password": "admin_set_pwd"})

    def test_admin_can_change_own_password(self):
        self.password_admin.with_user(self.password_admin).change_password(
            "lockdown_admin_pwd", "lockdown_admin_pwd_new"
        )

    def test_reset_password_param_disabled(self):
        value = self.env["ir.config_parameter"].sudo().get_param("auth_signup.reset_password")
        self.assertEqual(value, "False")
