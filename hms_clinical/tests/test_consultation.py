from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsConsultation(TransactionCase):
    """Tests for the hms.consultation model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Test Patient", "is_patient": True})
        cls.doctor_user = cls.env["res.users"].create({"name": "Dr. User", "login": "dr_cons_test"})
        cls.doctor = cls.env["hr.employee"].create(
            {"name": "Dr. Test", "is_doctor": True, "user_id": cls.doctor_user.id}
        )

    def _create_consultation(self, **overrides):
        vals = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
        }
        vals.update(overrides)
        return self.env["hms.consultation"].create(vals)

    def test_create_assigns_sequence(self):
        cons = self._create_consultation()
        self.assertNotEqual(cons.name, "New")
        self.assertTrue(cons.name.startswith("CONS/"), f"Expected CONS/ prefix, got {cons.name}")

    def test_sequence_increments(self):
        c1 = self._create_consultation()
        c2 = self._create_consultation()
        self.assertNotEqual(c1.name, c2.name)

    def test_default_state_is_draft(self):
        cons = self._create_consultation()
        self.assertEqual(cons.state, "draft")

    def test_state_transitions(self):
        cons = self._create_consultation()
        cons.action_start()
        self.assertEqual(cons.state, "in_progress")
        cons.action_done()
        self.assertEqual(cons.state, "done")

    def test_cancel_and_reset(self):
        cons = self._create_consultation()
        cons.action_cancel()
        self.assertEqual(cons.state, "cancelled")
        cons.action_draft()
        self.assertEqual(cons.state, "draft")

    def test_default_doctor_from_current_user(self):
        """When the current user is a doctor, doctor_id defaults to their employee."""
        cons = self.env["hms.consultation"].with_user(self.doctor_user).create({"patient_id": self.patient.id})
        self.assertEqual(cons.doctor_id, self.doctor)

    def test_date_defaults_to_now(self):
        cons = self._create_consultation()
        self.assertTrue(cons.date, "Date should be auto-filled.")
