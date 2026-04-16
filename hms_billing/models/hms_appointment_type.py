from odoo import fields, models


class HmsAppointmentType(models.Model):
    _inherit = "hms.appointment.type"

    product_id = fields.Many2one(
        "product.product",
        string="Billing Product",
        domain=[("type", "=", "service")],
        help="Service product used when billing this appointment type.",
    )
