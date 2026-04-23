from odoo import fields, models


class HmsAppointmentType(models.Model):
    _inherit = "hms.appointment.type"

    website_description = fields.Html(
        string="Website Description",
        sanitize=True,
        help="Public description displayed on the hospital website.",
    )
    website_published = fields.Boolean(
        string="Published on Website",
        default=False,
        help="If checked, this service will appear on the public website.",
    )
