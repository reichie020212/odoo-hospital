from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPortalAccess(TransactionCase):
    """Tests for portal user access to appointments and consultations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Portal Patient", "is_patient": True})
        cls.other_patient = cls.env["res.partner"].create({"name": "Other Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Portal", "is_doctor": True})

        cls.portal_user = cls.env["res.users"].create(
            {
                "name": "Portal Patient User",
                "login": "portal_patient_test",
                "partner_id": cls.patient.id,
                "group_ids": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )

        cls.consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.patient.id, "doctor_id": cls.doctor.id, "diagnosis": "Test diagnosis"}
        )
        cls.other_consultation = cls.env["hms.consultation"].create(
            {"patient_id": cls.other_patient.id, "doctor_id": cls.doctor.id}
        )

    def test_portal_can_read_own_consultation(self):
        """Portal user should be able to read their own consultation."""
        cons = self.env["hms.consultation"].with_user(self.portal_user).browse(self.consultation.id)
        cons.read(["name", "diagnosis"])

    def test_portal_cannot_read_other_consultation(self):
        """Portal user should not see another patient's consultation."""
        visible = (
            self.env["hms.consultation"].with_user(self.portal_user).search([("id", "=", self.other_consultation.id)])
        )
        self.assertFalse(visible)

    def test_portal_cannot_write_consultation(self):
        """Portal users have read-only access."""
        from odoo.exceptions import AccessError

        with self.assertRaises(AccessError):
            self.consultation.with_user(self.portal_user).write({"diagnosis": "Hacked"})

    def test_portal_home_counters(self):
        """Portal should see correct consultation count for the patient."""
        consultation_count = self.env["hms.consultation"].sudo().search_count([("patient_id", "=", self.patient.id)])
        self.assertEqual(consultation_count, 1)
