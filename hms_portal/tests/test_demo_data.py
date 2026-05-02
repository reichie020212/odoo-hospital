from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPortalDemoData(TransactionCase):
    """Tests for hms_portal demo login (patient portal user)."""

    def _ref(self, xml_id):
        record = self.env.ref(xml_id, raise_if_not_found=False)
        if not record:
            self.skipTest("Demo data not loaded.")
        return record

    def test_demo_user_patient_exists(self):
        user = self._ref("hms_portal.demo_user_patient")
        self.assertEqual(user.login, "hms_patient")

    def test_demo_user_patient_is_portal_only(self):
        user = self._ref("hms_portal.demo_user_patient")
        self.assertTrue(user.has_group("base.group_portal"))
        self.assertFalse(user.has_group("base.group_user"), "Portal user must not be an internal user.")
        self.assertFalse(user.has_group("hms_base.group_hms_user"))
        self.assertFalse(user.has_group("hms_base.group_hms_manager"))
        self.assertFalse(user.has_group("base.group_system"))

    def test_demo_user_patient_is_linked_to_demo_patient(self):
        user = self._ref("hms_portal.demo_user_patient")
        partner = self._ref("hms_base.demo_patient_maria")
        self.assertEqual(user.partner_id, partner, "Portal user partner must be Maria Santos.")
        self.assertTrue(partner.is_patient)
