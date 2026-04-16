from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsPrescriptionLine(TransactionCase):
    """Tests for the hms.prescription.line model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Rx Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Rx", "is_doctor": True})
        cls.consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.patient.id, "doctor_id": cls.doctor.id}
        )
        cls.product = cls.env["product.product"].create({"name": "Paracetamol 500mg", "type": "consu"})

    def test_create_prescription_line(self):
        line = self.env["hms.prescription.line"].create(
            {
                "consultation_id": self.consultation.id,
                "product_id": self.product.id,
                "dosage": "500mg",
                "frequency": "Twice daily",
                "duration_days": 5,
                "instructions": "Take after meals.",
            }
        )
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.dosage, "500mg")
        self.assertEqual(line.duration_days, 5)

    def test_prescription_linked_to_consultation(self):
        self.env["hms.prescription.line"].create(
            {
                "consultation_id": self.consultation.id,
                "product_id": self.product.id,
                "dosage": "500mg",
            }
        )
        self.assertEqual(len(self.consultation.prescription_line_ids), 1)

    def test_cascade_delete(self):
        line = self.env["hms.prescription.line"].create(
            {
                "consultation_id": self.consultation.id,
                "product_id": self.product.id,
            }
        )
        line_id = line.id
        self.consultation.unlink()
        self.assertFalse(self.env["hms.prescription.line"].browse(line_id).exists())
