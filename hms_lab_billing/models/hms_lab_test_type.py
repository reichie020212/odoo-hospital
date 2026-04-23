from odoo import fields, models


class HmsLabTestType(models.Model):
    _inherit = "hms.lab.test.type"

    product_id = fields.Many2one(
        "product.product",
        string="Billing Product",
        domain=[("type", "=", "service")],
        help="Service product used to bill this test type.",
    )
