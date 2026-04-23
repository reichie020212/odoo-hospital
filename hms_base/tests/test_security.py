from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsSecurity(TransactionCase):
    """Tests for Hospital security groups and access rules."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("hms_base.group_hms_user")
        cls.group_manager = cls.env.ref("hms_base.group_hms_manager")

        cls.hms_user = cls.env["res.users"].create(
            {
                "name": "HMS Test User",
                "login": "hms_test_user",
                "group_ids": [(6, 0, [cls.group_user.id])],
            }
        )
        cls.hms_manager = cls.env["res.users"].create(
            {
                "name": "HMS Test Manager",
                "login": "hms_test_manager",
                "group_ids": [(6, 0, [cls.group_manager.id])],
            }
        )

    def test_manager_implies_user(self):
        """Hospital Manager group must imply Hospital User."""
        self.assertIn(
            self.group_user,
            self.group_manager.implied_ids,
            "group_hms_manager should imply group_hms_user.",
        )

    def test_manager_has_user_group(self):
        """A user in group_hms_manager should also be in group_hms_user via implication."""
        self.assertTrue(
            self.hms_manager.has_group("hms_base.group_hms_user"),
            "Manager should inherit User group.",
        )

    def test_user_can_read_specializations(self):
        """HMS User should have read access to hms.specialization."""
        specs = self.env["hms.specialization"].with_user(self.hms_user).search([])
        self.assertIsNotNone(specs)

    def test_user_cannot_create_specialization(self):
        """HMS User should NOT be able to create specializations."""
        with self.assertRaises(AccessError):
            self.env["hms.specialization"].with_user(self.hms_user).create({"name": "Forbidden Spec"})

    def test_user_cannot_unlink_specialization(self):
        """HMS User should NOT be able to delete specializations."""
        spec = self.env["hms.specialization"].create({"name": "Protected"})
        with self.assertRaises(AccessError):
            spec.with_user(self.hms_user).unlink()

    def test_manager_can_crud_specialization(self):
        """HMS Manager should have full CRUD on hms.specialization."""
        spec = self.env["hms.specialization"].with_user(self.hms_manager).create({"name": "Manager Created"})
        self.assertTrue(spec.id)
        spec.with_user(self.hms_manager).write({"code": "MGR"})
        self.assertEqual(spec.code, "MGR")
        spec.with_user(self.hms_manager).unlink()
        self.assertFalse(spec.exists())
