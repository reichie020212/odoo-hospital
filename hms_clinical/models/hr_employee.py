from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_patient_count(self):
        consultation_model = self.env["hms.consultation"]
        for employee in self:
            consultations = consultation_model.search([("doctor_id", "=", employee.id)])
            employee.patient_count = len(consultations.mapped("patient_id"))

    def action_view_patients(self):
        self.ensure_one()
        consultations = self.env["hms.consultation"].search([("doctor_id", "=", self.id)])
        patient_ids = consultations.mapped("patient_id").ids
        return {
            "type": "ir.actions.act_window",
            "name": "Patients",
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("id", "in", patient_ids)],
            "context": {"default_is_patient": True},
        }
