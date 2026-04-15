from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_doctor = fields.Boolean(string="Is Doctor")
    is_nurse = fields.Boolean(string="Is Nurse")
    specialization_id = fields.Many2one(
        "hms.specialization",
        string="Specialization",
    )
    license_no = fields.Char(string="License Number")
    patient_count = fields.Integer(
        string="Patients",
        compute="_compute_patient_count",
        help="Number of distinct patients this employee has seen. Wired by hms_clinical.",
    )

    def _compute_patient_count(self):
        # Placeholder. Overridden by hms_clinical once hms.consultation exists.
        for employee in self:
            employee.patient_count = 0

    def action_view_patients(self):
        # Placeholder. Overridden by hms_clinical to return a real action.
        self.ensure_one()
        return {"type": "ir.actions.act_window_close"}
