from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDispensing(TransactionCase):
    """Tests for the prescription → stock.picking dispensing workflow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Rx Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Rx", "is_doctor": True})

        cls.medicine = cls.env["product.product"].create(
            {"name": "Amoxicillin 500mg", "type": "product", "is_medicine": True}
        )
        cls.service_product = cls.env["product.product"].create({"name": "Lab Fee", "type": "service"})

        cls.consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.patient.id, "doctor_id": cls.doctor.id}
        )
        cls.env["hms.prescription.line"].create(
            {
                "consultation_id": cls.consultation.id,
                "product_id": cls.medicine.id,
                "dosage": "500mg",
                "frequency": "3x daily",
                "duration_days": 7,
            }
        )

    def test_create_dispensing_picking(self):
        """action_create_dispensing should create a picking with one move."""
        self.consultation.action_create_dispensing()
        self.assertEqual(self.consultation.dispensing_count, 1)
        picking = self.consultation.picking_ids[0]
        self.assertEqual(picking.picking_type_id, self.env.ref("hms_pharmacy.picking_type_dispensing"))
        self.assertEqual(len(picking.move_ids), 1)
        self.assertEqual(picking.move_ids.product_id, self.medicine)

    def test_dispensing_links_move_to_line(self):
        """Each prescription line should be linked to its stock move."""
        self.consultation.action_create_dispensing()
        line = self.consultation.prescription_line_ids[0]
        self.assertTrue(line.move_id)
        self.assertEqual(line.move_id.product_id, self.medicine)

    def test_validate_picking_marks_dispensed(self):
        """Validating the picking should set dispensing_state to 'dispensed'."""
        self.consultation.action_create_dispensing()
        picking = self.consultation.picking_ids[0]
        # Force availability and validate
        picking.move_ids.quantity = 1
        picking.move_ids.picked = True
        picking.button_validate()
        line = self.consultation.prescription_line_ids[0]
        self.assertEqual(line.dispensing_state, "dispensed")

    def test_double_dispense_raises(self):
        """Cannot dispense again when all lines are already dispensed."""
        self.consultation.action_create_dispensing()
        picking = self.consultation.picking_ids[0]
        picking.move_ids.quantity = 1
        picking.move_ids.picked = True
        picking.button_validate()
        with self.assertRaises(UserError):
            self.consultation.action_create_dispensing()

    def test_service_products_skipped(self):
        """Service products should not appear in the dispensing picking."""
        self.env["hms.prescription.line"].create(
            {
                "consultation_id": self.consultation.id,
                "product_id": self.service_product.id,
                "dosage": "N/A",
            }
        )
        self.consultation.action_create_dispensing()
        picking = self.consultation.picking_ids[0]
        product_ids = picking.move_ids.mapped("product_id")
        self.assertNotIn(self.service_product, product_ids)
        self.assertIn(self.medicine, product_ids)

    def test_no_pending_lines_raises(self):
        """If no dispensable lines exist, action should raise."""
        # Remove storable line, add only service
        self.consultation.prescription_line_ids.unlink()
        self.env["hms.prescription.line"].create(
            {
                "consultation_id": self.consultation.id,
                "product_id": self.service_product.id,
            }
        )
        with self.assertRaises(UserError):
            self.consultation.action_create_dispensing()

    def test_action_view_dispensing(self):
        self.consultation.action_create_dispensing()
        action = self.consultation.action_view_dispensing()
        self.assertEqual(action["res_model"], "stock.picking")
