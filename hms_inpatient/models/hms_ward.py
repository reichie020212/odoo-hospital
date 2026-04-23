from odoo import api, fields, models


class HmsWard(models.Model):
    _name = "hms.ward"
    _description = "Hospital Ward"
    _order = "name"

    name = fields.Char(required=True)
    floor = fields.Char(string="Floor / Building")
    gender_restriction = fields.Selection(
        [
            ("mixed", "Mixed"),
            ("male", "Male Only"),
            ("female", "Female Only"),
        ],
        default="mixed",
    )
    bed_ids = fields.One2many("hms.bed", "ward_id", string="Beds")
    bed_count = fields.Integer(compute="_compute_bed_stats")
    available_count = fields.Integer(string="Available Beds", compute="_compute_bed_stats")
    active = fields.Boolean(default=True)

    @api.depends("bed_ids", "bed_ids.state")
    def _compute_bed_stats(self):
        for ward in self:
            ward.bed_count = len(ward.bed_ids)
            ward.available_count = len(ward.bed_ids.filtered(lambda bed: bed.state == "available"))

    def action_view_beds(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"{self.name} — Beds",
            "res_model": "hms.bed",
            "view_mode": "list,form",
            "domain": [("ward_id", "=", self.id)],
            "context": {"default_ward_id": self.id},
        }
