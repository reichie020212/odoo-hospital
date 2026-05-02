from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsDemoData(TransactionCase):
    """Tests for hms_base demo login accounts."""

    def _ref(self, xml_id):
        record = self.env.ref(xml_id, raise_if_not_found=False)
        if not record:
            self.skipTest("Demo data not loaded.")
        return record

    # --- Generic non-admin tester -------------------------------------------------

    def test_demo_user_tester_exists(self):
        user = self._ref("hms_base.demo_user_tester")
        self.assertEqual(user.login, "hms_demo")
        self.assertEqual(user.name, "Hospital Demo User")

    def test_demo_user_tester_is_hospital_user(self):
        user = self._ref("hms_base.demo_user_tester")
        self.assertTrue(user.has_group("hms_base.group_hms_user"))

    def test_demo_user_tester_is_not_manager(self):
        user = self._ref("hms_base.demo_user_tester")
        self.assertFalse(user.has_group("hms_base.group_hms_manager"))

    def test_demo_user_tester_is_not_system_admin(self):
        user = self._ref("hms_base.demo_user_tester")
        self.assertFalse(user.has_group("base.group_system"))

    # --- Doctor login -------------------------------------------------------------

    def test_demo_user_doctor_exists_and_is_hospital_user(self):
        user = self._ref("hms_base.demo_user_doctor")
        self.assertEqual(user.login, "hms_doctor")
        self.assertTrue(user.has_group("hms_base.group_hms_user"))
        self.assertFalse(user.has_group("hms_base.group_hms_manager"))

    def test_demo_user_doctor_linked_to_demo_doctor_lee(self):
        user = self._ref("hms_base.demo_user_doctor")
        employee = self._ref("hms_base.demo_doctor_lee")
        self.assertEqual(employee.user_id, user, "demo_doctor_lee.user_id must point to demo_user_doctor.")
        self.assertTrue(employee.is_doctor)

    # --- Nurse login --------------------------------------------------------------

    def test_demo_user_nurse_exists_and_is_hospital_user(self):
        user = self._ref("hms_base.demo_user_nurse")
        self.assertEqual(user.login, "hms_nurse")
        self.assertTrue(user.has_group("hms_base.group_hms_user"))
        self.assertFalse(user.has_group("hms_base.group_hms_manager"))

    def test_demo_user_nurse_linked_to_demo_nurse_reyes(self):
        user = self._ref("hms_base.demo_user_nurse")
        employee = self._ref("hms_base.demo_nurse_reyes")
        self.assertEqual(employee.user_id, user, "demo_nurse_reyes.user_id must point to demo_user_nurse.")
        self.assertTrue(employee.is_nurse)

    # --- Manager login ------------------------------------------------------------

    def test_demo_user_manager_is_hospital_manager(self):
        user = self._ref("hms_base.demo_user_manager")
        self.assertEqual(user.login, "hms_manager")
        self.assertTrue(user.has_group("hms_base.group_hms_manager"))
        self.assertTrue(
            user.has_group("hms_base.group_hms_user"),
            "Manager group must imply User group.",
        )
        self.assertFalse(
            user.has_group("base.group_system"),
            "Hospital Manager is application-level — not a system administrator.",
        )
