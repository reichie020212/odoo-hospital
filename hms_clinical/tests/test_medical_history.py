from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMedicalHistory(TransactionCase):
    """Tests for the medical-history smart buttons on res.partner and hr.employee."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "History Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. History", "is_doctor": True})

    def test_consultation_count_on_partner(self):
        self.assertEqual(self.patient.consultation_count, 0)
        self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        self.patient.invalidate_recordset()
        self.assertEqual(self.patient.consultation_count, 1)

    def test_action_view_consultations(self):
        self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        action = self.patient.action_view_consultations()
        self.assertEqual(action["res_model"], "hms.consultation")
        self.assertIn(("patient_id", "=", self.patient.id), action["domain"])

    def test_patient_count_on_employee(self):
        """patient_count should count distinct patients seen by a doctor."""
        patient2 = self.env["res.partner"].create({"name": "Patient 2", "is_patient": True})
        self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        self.env["hms.consultation"].create({"patient_id": patient2.id, "doctor_id": self.doctor.id})
        # Same patient again — should not double-count.
        self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        self.doctor.invalidate_recordset()
        self.assertEqual(self.doctor.patient_count, 2)

    def test_action_view_patients(self):
        self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        action = self.doctor.action_view_patients()
        self.assertEqual(action["res_model"], "res.partner")
        self.assertIn(self.patient.id, action["domain"][0][2])
