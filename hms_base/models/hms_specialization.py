from odoo import fields, models


class HmsSpecialization(models.Model):
    _name = "hms.specialization"
    _description = "Medical Specialization"
    _order = "name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    description = fields.Text()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "hms_specialization_name_unique",
            "UNIQUE(name)",
            "Specialization name must be unique.",
        ),
    ]
