from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestManifestLoading(TransactionCase):
    """Regression: menus that reference wizard actions must resolve at install time."""

    def test_create_staff_menu_action_resolves(self):
        action = self.env.ref("hms_base.action_create_staff_wizard")
        menu = self.env.ref("hms_base.menu_hms_create_staff")
        self.assertEqual(menu.action.id, action.id)
        self.assertEqual(action.res_model, "hms.create.staff.wizard")
