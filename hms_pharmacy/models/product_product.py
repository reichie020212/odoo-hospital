from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_medicine = fields.Boolean(string="Is Medicine", default=False)
