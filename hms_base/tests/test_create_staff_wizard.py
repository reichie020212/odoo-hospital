from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCreateStaffWizard(TransactionCase):
    """Tests for the one-step staff onboarding wizard (hms_base)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.specialization = cls.env["hms.specialization"].create(
            {
                "name": "Cardiology",
                "code": "CARD",
            }
        )
        cls.group_user = cls.env.ref("hms_base.group_hms_user")
        cls.group_manager = cls.env.ref("hms_base.group_hms_manager")

    def _create_wizard(self, **kwargs):
        vals = {
            "name": "Dr. Test",
            "email": "dr.test@example.com",
            "role": "doctor",
            "group_level": "user",
        }
        vals.update(kwargs)
        return self.env["hms.create.staff.wizard"].create(vals)

    def test_create_doctor(self):
        """Wizard creates an hr.employee + res.users for a doctor."""
        wizard = self._create_wizard(
            specialization_id=self.specialization.id,
            license_no="DOC-001",
            phone="+1234567890",
            job_title="Senior Cardiologist",
        )
        result = wizard.action_create()

        # Should redirect to the new employee form
        self.assertEqual(result["res_model"], "hr.employee")
        employee = self.env["hr.employee"].browse(result["res_id"])
        self.assertTrue(employee.exists())
        self.assertTrue(employee.is_doctor)
        self.assertFalse(employee.is_nurse)
        self.assertEqual(employee.specialization_id, self.specialization)
        self.assertEqual(employee.license_no, "DOC-001")

        # User should exist and be linked
        user = employee.user_id
        self.assertTrue(user.exists())
        self.assertEqual(user.login, "dr.test@example.com")
        self.assertIn(self.group_user, user.group_ids)

    def test_create_nurse(self):
        """Wizard creates an hr.employee + res.users for a nurse."""
        wizard = self._create_wizard(
            name="Nurse Joy",
            email="nurse.joy@example.com",
            role="nurse",
        )
        result = wizard.action_create()

        employee = self.env["hr.employee"].browse(result["res_id"])
        self.assertTrue(employee.is_nurse)
        self.assertFalse(employee.is_doctor)
        self.assertFalse(employee.specialization_id)

    def test_manager_group_level(self):
        """Setting group_level=manager assigns the HMS Manager group."""
        wizard = self._create_wizard(
            email="manager@example.com",
            group_level="manager",
        )
        result = wizard.action_create()

        employee = self.env["hr.employee"].browse(result["res_id"])
        user = employee.user_id
        self.assertIn(self.group_manager, user.group_ids)

    def test_duplicate_email_raises(self):
        """Wizard raises ValidationError if login already exists."""
        # Create a user first
        self.env["res.users"].create(
            {
                "name": "Existing User",
                "login": "taken@example.com",
            }
        )
        wizard = self._create_wizard(email="taken@example.com")
        with self.assertRaises(ValidationError):
            wizard.action_create()

    def test_specialization_ignored_for_nurse(self):
        """Even if specialization_id is set, it's ignored for nurses."""
        wizard = self._create_wizard(
            name="Nurse Spec",
            email="nurse.spec@example.com",
            role="nurse",
            specialization_id=self.specialization.id,
        )
        result = wizard.action_create()

        employee = self.env["hr.employee"].browse(result["res_id"])
        self.assertFalse(employee.specialization_id)

    def test_onchange_role_clears_specialization(self):
        """Switching role to nurse clears the specialization field."""
        wizard = self._create_wizard(
            specialization_id=self.specialization.id,
        )
        wizard.role = "nurse"
        wizard._onchange_role()
        self.assertFalse(wizard.specialization_id)
