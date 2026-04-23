from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsLabTestType(TransactionCase):
    """Tests for hms.lab.test.type model and seed data."""

    def test_create_individual_test(self):
        tt = self.env["hms.lab.test.type"].create(
            {"name": "Creatinine", "code": "CREA", "unit": "mg/dL", "normal_range_min": 0.7, "normal_range_max": 1.3}
        )
        self.assertFalse(tt.is_panel)
        self.assertEqual(tt.unit, "mg/dL")

    def test_create_panel(self):
        panel = self.env["hms.lab.test.type"].create({"name": "Lipid Panel", "is_panel": True})
        child = self.env["hms.lab.test.type"].create(
            {"name": "LDL Cholesterol", "parent_id": panel.id, "unit": "mg/dL"}
        )
        self.assertIn(child, panel.child_ids)

    def test_archive_hides(self):
        tt = self.env["hms.lab.test.type"].create({"name": "ToArchive"})
        tt.active = False
        visible = self.env["hms.lab.test.type"].search([("name", "=", "ToArchive")])
        self.assertFalse(visible)

    def test_seed_data_loaded(self):
        cbc = self.env.ref("hms_lab.test_type_cbc", raise_if_not_found=False)
        self.assertTrue(cbc)
        self.assertTrue(cbc.is_panel)
        self.assertTrue(len(cbc.child_ids) >= 3)

        glucose = self.env.ref("hms_lab.test_type_blood_glucose", raise_if_not_found=False)
        self.assertTrue(glucose)
        self.assertFalse(glucose.is_panel)
