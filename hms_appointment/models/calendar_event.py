from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    is_appointment = fields.Boolean(string="Medical Appointment", default=False)
    patient_id = fields.Many2one(
        "res.partner",
        string="Patient",
        domain=[("is_patient", "=", True)],
        index=True,
    )
    doctor_id = fields.Many2one(
        "hr.employee",
        string="Doctor",
        domain=[("is_doctor", "=", True)],
        index=True,
    )
    appointment_type_id = fields.Many2one(
        "hms.appointment.type",
        string="Appointment Type",
    )
    appointment_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("checked_in", "Checked In"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Appointment Status",
        default="draft",
    )

    @api.constrains("is_appointment", "patient_id", "doctor_id")
    def _check_appointment_requires_patient_and_doctor(self):
        for event in self:
            if event.is_appointment:
                if not event.patient_id:
                    raise ValidationError("A medical appointment requires a patient.")
                if not event.doctor_id:
                    raise ValidationError("A medical appointment requires a doctor.")

    @api.onchange("appointment_type_id")
    def _onchange_appointment_type_id(self):
        if self.appointment_type_id and self.appointment_type_id.default_duration:
            self.duration = self.appointment_type_id.default_duration

    # -- Attendee sync ----------------------------------------------------
    # Keep partner_ids in sync with patient/doctor so appointments appear
    # in the doctor's native Odoo / mobile calendar.

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_appointment_attendees()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "patient_id" in vals or "doctor_id" in vals:
            self._sync_appointment_attendees()
        return res

    def _sync_appointment_attendees(self):
        for event in self.filtered("is_appointment"):
            partners = self.env["res.partner"]
            if event.patient_id:
                partners |= event.patient_id
            if event.doctor_id and event.doctor_id.user_id:
                partners |= event.doctor_id.user_id.partner_id
            missing = partners - event.partner_ids
            if missing:
                event.partner_ids = [(4, p.id) for p in missing]

    # -- State transitions ------------------------------------------------

    def action_confirm(self):
        self.write({"appointment_state": "confirmed"})

    def action_check_in(self):
        self.write({"appointment_state": "checked_in"})

    def action_done(self):
        self.write({"appointment_state": "done"})

    def action_cancel(self):
        self.write({"appointment_state": "cancelled"})

    def action_draft(self):
        self.write({"appointment_state": "draft"})
