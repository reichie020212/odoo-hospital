from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsAppointmentType(TransactionCase):
    """Tests for the hms.appointment.type model."""

    def test_create_appointment_type(self):
        at = self.env["hms.appointment.type"].create({"name": "Surgery", "default_duration": 2.0})
        self.assertEqual(at.name, "Surgery")
        self.assertEqual(at.default_duration, 2.0)
        self.assertTrue(at.active)

    def test_default_duration(self):
        """If no duration is given, it should default to 0.5 h."""
        at = self.env["hms.appointment.type"].create({"name": "Quick Check"})
        self.assertEqual(at.default_duration, 0.5)

    def test_archive_hides_from_search(self):
        at = self.env["hms.appointment.type"].create({"name": "ToArchive"})
        at.active = False
        visible = self.env["hms.appointment.type"].search([("name", "=", "ToArchive")])
        self.assertFalse(visible)

    def test_seed_data_loaded(self):
        """Seed appointment types should exist after install."""
        expected = [
            "hms_appointment.appointment_type_general",
            "hms_appointment.appointment_type_followup",
            "hms_appointment.appointment_type_vaccination",
        ]
        for xmlid in expected:
            rec = self.env.ref(xmlid, raise_if_not_found=False)
            self.assertTrue(rec, f"Seed appointment type {xmlid} should exist.")
