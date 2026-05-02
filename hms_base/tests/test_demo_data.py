from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsDemoData(TransactionCase):
    """Tests for hms_base demo data records."""

    def test_demo_user_tester_exists(self):
        """Demo non-admin user must be present when demo data is loaded."""
        user = self.env.ref("hms_base.demo_user_tester", raise_if_not_found=False)
        if not user:
            self.skipTest("Demo data not loaded.")
        self.assertEqual(user.login, "hms_demo")
        self.assertEqual(user.name, "Hospital Demo User")

    def test_demo_user_tester_is_hospital_user(self):
        """Demo user must belong to the Hospital User group."""
        user = self.env.ref("hms_base.demo_user_tester", raise_if_not_found=False)
        if not user:
            self.skipTest("Demo data not loaded.")
        self.assertTrue(user.has_group("hms_base.group_hms_user"))

    def test_demo_user_tester_is_not_manager(self):
        """Demo user must NOT belong to the Hospital Manager group."""
        user = self.env.ref("hms_base.demo_user_tester", raise_if_not_found=False)
        if not user:
            self.skipTest("Demo data not loaded.")
        self.assertFalse(user.has_group("hms_base.group_hms_manager"))

    def test_demo_user_tester_is_not_system_admin(self):
        """Demo user must NOT have the Settings/Administration access."""
        user = self.env.ref("hms_base.demo_user_tester", raise_if_not_found=False)
        if not user:
            self.skipTest("Demo data not loaded.")
        self.assertFalse(user.has_group("base.group_system"))
