from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsVital(TransactionCase):
    """Tests for the hms.vital model and BMI computation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Vital Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Vital", "is_doctor": True})
        cls.consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.patient.id, "doctor_id": cls.doctor.id}
        )

    def _create_vital(self, **overrides):
        vals = {"consultation_id": self.consultation.id}
        vals.update(overrides)
        return self.env["hms.vital"].create(vals)

    def test_create_vital(self):
        vital = self._create_vital(bp_systolic=120, bp_diastolic=80, heart_rate=72)
        self.assertEqual(vital.bp_systolic, 120)
        self.assertEqual(vital.bp_diastolic, 80)
        self.assertEqual(vital.heart_rate, 72)

    def test_bmi_computation(self):
        """BMI = weight / (height_m^2). 70 kg, 175 cm → 22.86."""
        vital = self._create_vital(weight=70.0, height=175.0)
        self.assertAlmostEqual(vital.bmi, 22.9, places=1)

    def test_bmi_zero_when_missing_weight(self):
        vital = self._create_vital(weight=0.0, height=175.0)
        self.assertEqual(vital.bmi, 0.0)

    def test_bmi_zero_when_missing_height(self):
        vital = self._create_vital(weight=70.0, height=0.0)
        self.assertEqual(vital.bmi, 0.0)

    def test_bmi_stored_and_updates(self):
        """BMI is stored; changing weight should recompute."""
        vital = self._create_vital(weight=70.0, height=175.0)
        original_bmi = vital.bmi
        vital.weight = 90.0
        self.assertNotEqual(vital.bmi, original_bmi)
        self.assertAlmostEqual(vital.bmi, 29.4, places=1)

    def test_cascade_delete(self):
        vital = self._create_vital(bp_systolic=120)
        vital_id = vital.id
        self.consultation.unlink()
        self.assertFalse(self.env["hms.vital"].browse(vital_id).exists())
