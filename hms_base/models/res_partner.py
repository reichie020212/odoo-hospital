from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_patient = fields.Boolean(string="Is Patient", tracking=True)
    date_of_birth = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(
        string="Age",
        compute="_compute_age",
        help="Computed from date of birth; not stored so it stays current.",
    )
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
        tracking=True,
    )
    blood_group = fields.Selection(
        [
            ("a+", "A+"),
            ("a-", "A-"),
            ("b+", "B+"),
            ("b-", "B-"),
            ("ab+", "AB+"),
            ("ab-", "AB-"),
            ("o+", "O+"),
            ("o-", "O-"),
        ],
        string="Blood Group",
        tracking=True,
    )
    guardian_ids = fields.Many2many(
        "res.partner",
        relation="hms_patient_guardian_rel",
        column1="patient_id",
        column2="guardian_id",
        string="Guardians",
    )

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for partner in self:
            if partner.date_of_birth:
                partner.age = relativedelta(today, partner.date_of_birth).years
            else:
                partner.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        # TODO(hms_base): a partner flipped to is_patient=True *after* creation
        # does not get a sequence-backed ref. Document-only for MVP; revisit if
        # the upgrade path becomes a real workflow.
        for vals in vals_list:
            if vals.get("is_patient") and not vals.get("ref"):
                vals["ref"] = self.env["ir.sequence"].next_by_code("hms.patient.ref") or "/"
        return super().create(vals_list)
