from datetime import date

from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResPartnerPatient(TransactionCase):
    """Tests for the patient extensions on res.partner (hms_base)."""

    def test_create_patient_assigns_sequence_ref(self):
        """Creating a partner with is_patient=True auto-assigns a ref from the hms.patient.ref sequence."""
        patient = self.env["res.partner"].create(
            {
                "name": "John Doe",
                "is_patient": True,
            }
        )
        self.assertTrue(patient.ref, "Patient ref should be set automatically on create.")
        self.assertTrue(
            patient.ref.startswith("P/"),
            f"Patient ref '{patient.ref}' should start with 'P/'.",
        )

    def test_create_patient_preserves_existing_ref(self):
        """If a ref is already provided at creation the sequence should not overwrite it."""
        patient = self.env["res.partner"].create(
            {
                "name": "Jane Doe",
                "is_patient": True,
                "ref": "CUSTOM-001",
            }
        )
        self.assertEqual(patient.ref, "CUSTOM-001")

    def test_create_non_patient_no_sequence_ref(self):
        """A non-patient partner should not receive a patient-sequence ref."""
        partner = self.env["res.partner"].create(
            {
                "name": "Supplier Corp",
                "is_patient": False,
            }
        )
        self.assertFalse(partner.ref)

    def test_sequence_increments(self):
        """Each new patient should receive a distinct, incrementing ref."""
        p1 = self.env["res.partner"].create({"name": "Patient A", "is_patient": True})
        p2 = self.env["res.partner"].create({"name": "Patient B", "is_patient": True})
        self.assertNotEqual(p1.ref, p2.ref, "Two patients should get different refs.")

    def test_age_computation_with_dob(self):
        """Age should be correctly derived from date_of_birth."""
        dob = date.today() - relativedelta(years=25)
        patient = self.env["res.partner"].create(
            {
                "name": "Test Age",
                "is_patient": True,
                "date_of_birth": dob,
            }
        )
        self.assertEqual(patient.age, 25)

    def test_age_computation_without_dob(self):
        """Age should be 0 when date_of_birth is not set."""
        patient = self.env["res.partner"].create(
            {
                "name": "No DOB",
                "is_patient": True,
            }
        )
        self.assertEqual(patient.age, 0)

    def test_age_not_stored(self):
        """Age is a non-stored computed field — changing DOB must reflect immediately."""
        patient = self.env["res.partner"].create(
            {
                "name": "Age Refresh",
                "is_patient": True,
                "date_of_birth": date.today() - relativedelta(years=40),
            }
        )
        self.assertEqual(patient.age, 40)
        patient.date_of_birth = date.today() - relativedelta(years=10)
        self.assertEqual(patient.age, 10)

    def test_guardian_relationship(self):
        """Patients can be linked to guardian partners via the M2M."""
        guardian = self.env["res.partner"].create({"name": "Parent Guardian"})
        patient = self.env["res.partner"].create(
            {
                "name": "Child Patient",
                "is_patient": True,
                "guardian_ids": [(4, guardian.id)],
            }
        )
        self.assertIn(guardian, patient.guardian_ids)

    def test_blood_group_selection(self):
        """All eight blood-group values should be accepted."""
        for bg in ("a+", "a-", "b+", "b-", "ab+", "ab-", "o+", "o-"):
            patient = self.env["res.partner"].create(
                {
                    "name": f"BG {bg}",
                    "is_patient": True,
                    "blood_group": bg,
                }
            )
            self.assertEqual(patient.blood_group, bg)
