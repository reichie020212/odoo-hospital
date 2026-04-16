from odoo import fields, models


class HmsAppointmentType(models.Model):
    _name = "hms.appointment.type"
    _description = "Appointment Type"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    default_duration = fields.Float(
        string="Default Duration (hours)",
        default=0.5,
        help="Default duration in hours. Applied via onchange when this type is selected on an appointment.",
    )
    active = fields.Boolean(default=True)
    # product_id is wired by hms_billing (Phase 4).
