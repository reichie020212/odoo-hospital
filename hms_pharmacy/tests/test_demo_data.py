from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsPharmacyDemoData(TransactionCase):
    """Verify hms_pharmacy extends the near-admin demo user with Inventory admin rights."""

    def _ref(self, xml_id):
        record = self.env.ref(xml_id, raise_if_not_found=False)
        if not record:
            self.skipTest("Demo data not loaded.")
        return record

    def test_demo_user_admin_has_stock_manager(self):
        user = self._ref("hms_base.demo_user_admin")
        self.assertTrue(user.has_group("stock.group_stock_manager"))

    def test_demo_user_admin_still_has_no_settings_access(self):
        user = self._ref("hms_base.demo_user_admin")
        self.assertFalse(user.has_group("base.group_system"))
        self.assertFalse(user.has_group("base.group_erp_manager"))
