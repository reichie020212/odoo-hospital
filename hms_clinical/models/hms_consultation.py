from odoo import api, fields, models


class HmsConsultation(models.Model):
    _name = "hms.consultation"
    _description = "Medical Consultation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default="New",
        copy=False,
        readonly=True,
    )
    patient_id = fields.Many2one(
        "res.partner",
        string="Patient",
        required=True,
        domain=[("is_patient", "=", True)],
        tracking=True,
    )
    doctor_id = fields.Many2one(
        "hr.employee",
        string="Doctor",
        required=True,
        domain=[("is_doctor", "=", True)],
        tracking=True,
        default=lambda self: self._default_doctor_id(),
    )
    appointment_id = fields.Many2one(
        "calendar.event",
        string="Appointment",
        domain=[("is_appointment", "=", True)],
    )
    date = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    chief_complaint = fields.Text(string="Chief Complaint")
    history = fields.Text(string="History of Present Illness")
    examination = fields.Text(string="Examination Findings")
    diagnosis = fields.Text(string="Diagnosis", tracking=True)
    treatment_plan = fields.Text(string="Treatment Plan")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    vital_ids = fields.One2many("hms.vital", "consultation_id", string="Vitals")
    prescription_line_ids = fields.One2many("hms.prescription.line", "consultation_id", string="Prescription Lines")

    def _default_doctor_id(self):
        employee = self.env.user.employee_id
        if employee and employee.is_doctor:
            return employee.id
        return False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("hms.consultation") or "New"
        return super().create(vals_list)

    # -- State transitions ------------------------------------------------

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})
