from odoo import api, fields, models


class HmsInsurancePolicy(models.Model):
    _name = "hms.insurance.policy"
    _description = "Insurance Policy"
    _order = "valid_until desc, id desc"

    name = fields.Char(
        string="Policy Number",
        required=True,
    )
    patient_id = fields.Many2one(
        "res.partner",
        string="Patient",
        required=True,
        domain=[("is_patient", "=", True)],
        index=True,
    )
    insurance_company_id = fields.Many2one(
        "res.partner",
        string="Insurance Company",
        required=True,
        domain=[("is_insurance_company", "=", True)],
    )
    policy_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("corporate", "Corporate"),
        ],
        default="individual",
    )
    coverage_percentage = fields.Float(
        string="Coverage (%)",
        default=80.0,
        help="Percentage of the bill covered by the insurer. The remainder is the patient's co-pay.",
    )
    valid_from = fields.Date(required=True)
    valid_until = fields.Date(required=True)
    active = fields.Boolean(default=True)

    @api.model
    def get_active_policy(self, patient_id):
        """Return the first active, valid policy for a patient, or False."""
        today = fields.Date.context_today(self)
        return self.search(
            [
                ("patient_id", "=", patient_id),
                ("valid_from", "<=", today),
                ("valid_until", ">=", today),
                ("active", "=", True),
            ],
            limit=1,
        )
