from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    consultation_ids = fields.One2many("hms.consultation", "patient_id", string="Consultations")
    consultation_count = fields.Integer(
        string="Consultations",
        compute="_compute_consultation_count",
    )

    def _compute_consultation_count(self):
        for partner in self:
            partner.consultation_count = len(partner.consultation_ids)

    def action_view_consultations(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Consultations",
            "res_model": "hms.consultation",
            "view_mode": "list,form",
            "domain": [("patient_id", "=", self.id)],
        }
