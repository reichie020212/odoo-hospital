from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsWebsite(TransactionCase):
    """Tests for the hms_website model extensions."""

    def test_doctor_website_published(self):
        doctor = self.env["hr.employee"].create({"name": "Dr. Web", "is_doctor": True, "website_published": True})
        self.assertTrue(doctor.website_published)
        published = self.env["hr.employee"].search([("is_doctor", "=", True), ("website_published", "=", True)])
        self.assertIn(doctor, published)

    def test_doctor_not_published_by_default(self):
        doctor = self.env["hr.employee"].create({"name": "Dr. Hidden", "is_doctor": True})
        self.assertFalse(doctor.website_published)

    def test_service_website_published(self):
        service = self.env["hms.appointment.type"].create(
            {
                "name": "Web Service",
                "website_published": True,
                "website_description": "<p>Test</p>",
            }
        )
        self.assertTrue(service.website_published)

    def test_service_not_published_by_default(self):
        service = self.env["hms.appointment.type"].create({"name": "Hidden Service"})
        self.assertFalse(service.website_published)
