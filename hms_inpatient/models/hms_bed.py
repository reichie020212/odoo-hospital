from odoo import fields, models


class HmsBed(models.Model):
    _name = "hms.bed"
    _description = "Hospital Bed"
    _order = "ward_id, name"

    name = fields.Char(required=True)
    ward_id = fields.Many2one("hms.ward", string="Ward", required=True, ondelete="restrict")
    bed_type = fields.Selection(
        [
            ("standard", "Standard"),
            ("semi_private", "Semi-Private"),
            ("private", "Private"),
            ("icu", "ICU"),
        ],
        default="standard",
    )
    state = fields.Selection(
        [
            ("available", "Available"),
            ("occupied", "Occupied"),
            ("cleaning", "Cleaning"),
            ("maintenance", "Maintenance"),
        ],
        default="available",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Room Charge Product",
        domain=[("type", "=", "service")],
        help="Service product billed daily while this bed is occupied.",
    )
    active = fields.Boolean(default=True)
