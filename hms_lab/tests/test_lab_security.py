from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLabSecurity(TransactionCase):
    """Tests for Lab Technician group access rights."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lab_tech = cls.env["res.users"].create(
            {
                "name": "Lab Tech",
                "login": "lab_tech_test",
                "group_ids": [(6, 0, [cls.env.ref("hms_lab.group_hms_lab_tech").id])],
            }
        )
        cls.patient = cls.env["res.partner"].create({"name": "Sec Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Sec", "is_doctor": True})

    def test_lab_tech_can_read_requests(self):
        req = self.env["hms.lab.request"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        req_as_tech = self.env["hms.lab.request"].with_user(self.lab_tech).browse(req.id)
        req_as_tech.read(["name", "state"])

    def test_lab_tech_can_write_results(self):
        req = self.env["hms.lab.request"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        test_type = self.env["hms.lab.test.type"].create({"name": "Tech Test", "unit": "U"})
        result = self.env["hms.lab.result"].create({"request_id": req.id, "test_type_id": test_type.id})
        result.with_user(self.lab_tech).write({"value": 42.0})
        self.assertEqual(result.value, 42.0)

    def test_lab_tech_cannot_create_test_types(self):
        with self.assertRaises(AccessError):
            self.env["hms.lab.test.type"].with_user(self.lab_tech).create({"name": "Forbidden"})

    def test_lab_tech_can_read_test_types(self):
        types = self.env["hms.lab.test.type"].with_user(self.lab_tech).search([])
        self.assertIsNotNone(types)
