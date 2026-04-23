from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    website_bio = fields.Html(
        string="Website Bio",
        sanitize=True,
        help="Public biography displayed on the hospital website.",
    )
    website_published = fields.Boolean(
        string="Published on Website",
        default=False,
        help="If checked, this doctor will appear on the public website.",
    )
