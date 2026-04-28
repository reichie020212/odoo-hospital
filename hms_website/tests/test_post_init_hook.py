from odoo.addons import hms_website
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPostInitHook(TransactionCase):
    """Regression: the manifest references post_init_hook, so it must be importable
    from the module's top-level package and must set the homepage on install."""

    def test_hook_is_exposed_on_package(self):
        self.assertTrue(callable(getattr(hms_website, "post_init_hook", None)))

    def test_homepage_set_to_hospital(self):
        website = self.env["website"].search([], limit=1)
        self.assertTrue(website)
        self.assertEqual(website.homepage_url, "/hospital")
