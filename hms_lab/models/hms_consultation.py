from odoo import api, fields, models


class HmsConsultation(models.Model):
    _inherit = "hms.consultation"

    lab_request_ids = fields.One2many("hms.lab.request", "consultation_id", string="Lab Requests")
    lab_request_count = fields.Integer(
        string="Lab Requests",
        compute="_compute_lab_request_count",
    )

    @api.depends("lab_request_ids")
    def _compute_lab_request_count(self):
        for cons in self:
            cons.lab_request_count = len(cons.lab_request_ids)

    def action_create_lab_request(self):
        """Create a lab request pre-filled from this consultation."""
        self.ensure_one()
        request = self.env["hms.lab.request"].create(
            {
                "patient_id": self.patient_id.id,
                "doctor_id": self.doctor_id.id,
                "consultation_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "hms.lab.request",
            "res_id": request.id,
            "view_mode": "form",
        }

    def action_view_lab_requests(self):
        self.ensure_one()
        if self.lab_request_count == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "hms.lab.request",
                "res_id": self.lab_request_ids.id,
                "view_mode": "form",
            }
        return {
            "type": "ir.actions.act_window",
            "res_model": "hms.lab.request",
            "view_mode": "list,form",
            "domain": [("id", "in", self.lab_request_ids.ids)],
        }
