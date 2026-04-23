from odoo import fields, models


class HmsPrescriptionLine(models.Model):
    _inherit = "hms.prescription.line"

    dispensing_state = fields.Selection(
        [
            ("pending", "Pending"),
            ("dispensed", "Dispensed"),
        ],
        string="Dispensing",
        default="pending",
        readonly=True,
        copy=False,
    )
    move_id = fields.Many2one(
        "stock.move",
        string="Stock Move",
        readonly=True,
        copy=False,
        help="The stock move that fulfilled this prescription line.",
    )
