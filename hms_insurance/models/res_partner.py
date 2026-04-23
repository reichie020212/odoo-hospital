from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_insurance_company = fields.Boolean(string="Is Insurance Company")
    insurance_policy_ids = fields.One2many("hms.insurance.policy", "patient_id", string="Insurance Policies")
