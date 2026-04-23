from odoo import fields, models


class HmsLabTestType(models.Model):
    _name = "hms.lab.test.type"
    _description = "Lab Test Type"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    is_panel = fields.Boolean(
        default=False,
        help="A panel groups multiple individual tests (e.g. CBC).",
    )
    parent_id = fields.Many2one(
        "hms.lab.test.type",
        string="Parent Panel",
        domain=[("is_panel", "=", True)],
        ondelete="set null",
    )
    child_ids = fields.One2many("hms.lab.test.type", "parent_id", string="Panel Tests")
    normal_range_min = fields.Float(string="Normal Min")
    normal_range_max = fields.Float(string="Normal Max")
    unit = fields.Char(string="Unit", help="e.g. mg/dL, mmol/L, cells/μL")
    active = fields.Boolean(default=True)
