from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHrEmployeeClinical(TransactionCase):
    """Tests for the clinical-staff extensions on hr.employee (hms_base)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.specialization = cls.env["hms.specialization"].create(
            {
                "name": "Test Specialty",
                "code": "TST",
            }
        )

    def test_doctor_flags_and_specialization(self):
        employee = self.env["hr.employee"].create(
            {
                "name": "Dr. House",
                "is_doctor": True,
                "specialization_id": self.specialization.id,
                "license_no": "MED-12345",
            }
        )
        self.assertTrue(employee.is_doctor)
        self.assertFalse(employee.is_nurse)
        self.assertEqual(employee.specialization_id, self.specialization)
        self.assertEqual(employee.license_no, "MED-12345")

    def test_nurse_flag(self):
        employee = self.env["hr.employee"].create(
            {
                "name": "Nurse Joy",
                "is_nurse": True,
            }
        )
        self.assertTrue(employee.is_nurse)
        self.assertFalse(employee.is_doctor)

    def test_dual_role(self):
        """An employee can be both a doctor and a nurse if needed."""
        employee = self.env["hr.employee"].create(
            {
                "name": "Dr. Nurse",
                "is_doctor": True,
                "is_nurse": True,
                "specialization_id": self.specialization.id,
            }
        )
        self.assertTrue(employee.is_doctor)
        self.assertTrue(employee.is_nurse)

    def test_patient_count_placeholder_returns_zero(self):
        """patient_count should return 0 until hms_clinical wires the real compute."""
        employee = self.env["hr.employee"].create(
            {
                "name": "Dr. Placeholder",
                "is_doctor": True,
            }
        )
        self.assertEqual(employee.patient_count, 0)

    def test_action_view_patients_placeholder(self):
        """The placeholder action should return a close-window dict without errors."""
        employee = self.env["hr.employee"].create(
            {
                "name": "Dr. Action",
                "is_doctor": True,
            }
        )
        result = employee.action_view_patients()
        self.assertEqual(result.get("type"), "ir.actions.act_window_close")
