from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestClinicalSecurity(TransactionCase):
    """Tests for hms.consultation record rules (read-all / write-own / unlink-manager)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Sec Patient", "is_patient": True})

        # Doctor A — has a linked user.
        cls.user_a = cls.env["res.users"].create(
            {
                "name": "Dr. A",
                "login": "dr_a_sec",
                "group_ids": [(6, 0, [cls.env.ref("hms_base.group_hms_user").id])],
            }
        )
        cls.doctor_a = cls.env["hr.employee"].create({"name": "Dr. A", "is_doctor": True, "user_id": cls.user_a.id})

        # Doctor B — different user.
        cls.user_b = cls.env["res.users"].create(
            {
                "name": "Dr. B",
                "login": "dr_b_sec",
                "group_ids": [(6, 0, [cls.env.ref("hms_base.group_hms_user").id])],
            }
        )
        cls.doctor_b = cls.env["hr.employee"].create({"name": "Dr. B", "is_doctor": True, "user_id": cls.user_b.id})

        # Manager user.
        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "HMS Manager",
                "login": "hms_mgr_sec",
                "group_ids": [(6, 0, [cls.env.ref("hms_base.group_hms_manager").id])],
            }
        )

        # Consultation owned by Doctor A.
        cls.cons_a = cls.env["hms.consultation"].create({"patient_id": cls.patient.id, "doctor_id": cls.doctor_a.id})

    def test_doctor_can_read_all_consultations(self):
        """Doctor B should be able to read Doctor A's consultation (clinical continuity)."""
        cons = self.env["hms.consultation"].with_user(self.user_b).browse(self.cons_a.id)
        cons.read(["name", "diagnosis"])  # should not raise

    def test_doctor_can_write_own_consultation(self):
        self.cons_a.with_user(self.user_a).write({"diagnosis": "Common cold"})
        self.assertEqual(self.cons_a.diagnosis, "Common cold")

    def test_doctor_cannot_write_other_consultation(self):
        with self.assertRaises(AccessError):
            self.cons_a.with_user(self.user_b).write({"diagnosis": "Hack attempt"})

    def test_doctor_cannot_unlink_consultation(self):
        with self.assertRaises(AccessError):
            self.cons_a.with_user(self.user_a).unlink()

    def test_manager_can_write_any_consultation(self):
        self.cons_a.with_user(self.manager_user).write({"diagnosis": "Manager edit"})
        self.assertEqual(self.cons_a.diagnosis, "Manager edit")

    def test_manager_can_unlink_consultation(self):
        cons = self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor_a.id})
        cons.with_user(self.manager_user).unlink()
        self.assertFalse(cons.exists())
