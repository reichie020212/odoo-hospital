from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsBillingDemoData(TransactionCase):
    """Verify hms_billing extends the near-admin demo user with Sales/Accounting admin rights."""

    def _ref(self, xml_id):
        record = self.env.ref(xml_id, raise_if_not_found=False)
        if not record:
            self.skipTest("Demo data not loaded.")
        return record

    def test_demo_user_admin_has_sales_manager(self):
        user = self._ref("hms_base.demo_user_admin")
        self.assertTrue(user.has_group("sales_team.group_sale_manager"))

    def test_demo_user_admin_has_account_manager(self):
        user = self._ref("hms_base.demo_user_admin")
        self.assertTrue(user.has_group("account.group_account_manager"))

    def test_demo_user_admin_still_has_no_settings_access(self):
        user = self._ref("hms_base.demo_user_admin")
        self.assertFalse(user.has_group("base.group_system"))
        self.assertFalse(user.has_group("base.group_erp_manager"))
