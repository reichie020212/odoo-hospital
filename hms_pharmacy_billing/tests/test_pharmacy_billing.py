from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPharmacyBilling(TransactionCase):
    """Tests for the dispensing → sale.order billing bridge."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Pharm Bill Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. PharmBill", "is_doctor": True})
        cls.medicine = cls.env["product.product"].create(
            {"name": "Billing Medicine", "type": "product", "is_medicine": True, "list_price": 15.0}
        )
        cls.consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.patient.id, "doctor_id": cls.doctor.id}
        )
        cls.env["hms.prescription.line"].create(
            {
                "consultation_id": cls.consultation.id,
                "product_id": cls.medicine.id,
                "qty": 10,
                "dosage": "500mg",
            }
        )

    def test_dispense_adds_so_line(self):
        """Validating a dispensing picking should add a medicine line to the consultation's SO."""
        # Create SO via billing first
        from datetime import datetime, timedelta

        start = datetime.now()
        appt_type = self.env["hms.appointment.type"].create({"name": "BillType", "default_duration": 0.5})
        product_fee = self.env["product.product"].create({"name": "Consult Fee", "type": "service", "list_price": 50.0})
        appt_type.product_id = product_fee
        appointment = self.env["calendar.event"].create(
            {
                "name": "Test",
                "start": start,
                "stop": start + timedelta(hours=1),
                "is_appointment": True,
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "appointment_type_id": appt_type.id,
            }
        )
        self.consultation.appointment_id = appointment
        self.consultation.action_create_sale_order()
        so = self.consultation.sale_order_id
        initial_lines = len(so.order_line)

        # Dispense
        self.consultation.action_create_dispensing()
        picking = self.consultation.picking_ids[0]
        picking.move_ids.quantity = 10
        picking.move_ids.picked = True
        picking.button_validate()

        # SO should have the original consultation fee + dispensed medicine
        self.assertGreater(len(so.order_line), initial_lines)
        med_lines = so.order_line.filtered(lambda line: line.product_id == self.medicine)
        self.assertTrue(med_lines)

    def test_dispense_creates_so_if_missing(self):
        """If the consultation has no SO, dispensing should create one."""
        self.assertFalse(self.consultation.sale_order_id)
        self.consultation.action_create_dispensing()
        picking = self.consultation.picking_ids[0]
        picking.move_ids.quantity = 10
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertTrue(self.consultation.sale_order_id)
        self.assertEqual(len(self.consultation.sale_order_id.order_line), 1)
