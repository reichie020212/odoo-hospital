from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductMedicine(TransactionCase):
    """Tests for the is_medicine flag on product.product."""

    def test_is_medicine_flag(self):
        product = self.env["product.product"].create({"name": "Ibuprofen", "type": "product", "is_medicine": True})
        self.assertTrue(product.is_medicine)

    def test_medicine_action_filters(self):
        self.env["product.product"].create({"name": "Med A", "type": "product", "is_medicine": True})
        self.env["product.product"].create({"name": "Non-Med B", "type": "product", "is_medicine": False})
        medicines = self.env["product.product"].search([("is_medicine", "=", True)])
        non_meds = self.env["product.product"].search([("is_medicine", "=", False)])
        self.assertTrue(any(p.name == "Med A" for p in medicines))
        self.assertFalse(any(p.name == "Non-Med B" for p in medicines))
        self.assertTrue(any(p.name == "Non-Med B" for p in non_meds))

    def test_pharmacy_data_loaded(self):
        """Pharmacy location and dispensing picking type should exist after install."""
        loc = self.env.ref("hms_pharmacy.location_pharmacy", raise_if_not_found=False)
        self.assertTrue(loc, "Pharmacy stock location should exist.")
        pt = self.env.ref("hms_pharmacy.picking_type_dispensing", raise_if_not_found=False)
        self.assertTrue(pt, "Dispensing picking type should exist.")
