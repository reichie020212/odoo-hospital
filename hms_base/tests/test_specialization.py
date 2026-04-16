from odoo.tests.common import TransactionCase, tagged
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


@tagged("post_install", "-at_install")
class TestHmsSpecialization(TransactionCase):
    """Tests for the hms.specialization model."""

    def test_create_specialization(self):
        spec = self.env["hms.specialization"].create(
            {
                "name": "Neurology",
                "code": "NEUR",
                "description": "Brain and nervous system.",
            }
        )
        self.assertEqual(spec.name, "Neurology")
        self.assertEqual(spec.code, "NEUR")
        self.assertTrue(spec.active, "New specializations should be active by default.")

    def test_unique_name_constraint(self):
        """Two specializations with the same name must violate the SQL unique constraint."""
        self.env["hms.specialization"].create({"name": "DuplicateTest"})
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self.env["hms.specialization"].create({"name": "DuplicateTest"})

    def test_archive_hides_from_default_search(self):
        """An archived specialization should not appear in default (active=True) search."""
        spec = self.env["hms.specialization"].create({"name": "ToArchive"})
        spec.active = False
        visible = self.env["hms.specialization"].search([("name", "=", "ToArchive")])
        self.assertFalse(visible, "Archived specializations should be hidden by default.")

    def test_seed_data_loaded(self):
        """The six seed specializations from hms_specialization_data.xml must exist after install."""
        expected = [
            "hms_base.specialization_general_medicine",
            "hms_base.specialization_pediatrics",
            "hms_base.specialization_cardiology",
            "hms_base.specialization_obgyn",
            "hms_base.specialization_orthopedics",
            "hms_base.specialization_dermatology",
        ]
        for xmlid in expected:
            rec = self.env.ref(xmlid, raise_if_not_found=False)
            self.assertTrue(rec, f"Seed specialization {xmlid} should exist.")
