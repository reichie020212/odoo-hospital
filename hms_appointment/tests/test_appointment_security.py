from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAppointmentSecurity(TransactionCase):
    """Tests for hms.appointment.type access rules."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hms_user = cls.env["res.users"].create(
            {
                "name": "Appt Test User",
                "login": "appt_test_user",
                "group_ids": [(6, 0, [cls.env.ref("hms_base.group_hms_user").id])],
            }
        )
        cls.hms_manager = cls.env["res.users"].create(
            {
                "name": "Appt Test Manager",
                "login": "appt_test_manager",
                "group_ids": [(6, 0, [cls.env.ref("hms_base.group_hms_manager").id])],
            }
        )

    def test_user_can_read_appointment_type(self):
        types = self.env["hms.appointment.type"].with_user(self.hms_user).search([])
        self.assertIsNotNone(types)

    def test_user_cannot_create_appointment_type(self):
        with self.assertRaises(AccessError):
            self.env["hms.appointment.type"].with_user(self.hms_user).create({"name": "Forbidden"})

    def test_manager_can_crud_appointment_type(self):
        at = self.env["hms.appointment.type"].with_user(self.hms_manager).create({"name": "Manager Type"})
        self.assertTrue(at.id)
        at.with_user(self.hms_manager).write({"default_duration": 1.5})
        self.assertEqual(at.default_duration, 1.5)
        at.with_user(self.hms_manager).unlink()
        self.assertFalse(at.exists())
