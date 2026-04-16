from odoo import fields, models


class HmsPrescriptionLine(models.Model):
    _name = "hms.prescription.line"
    _description = "Prescription Line"

    consultation_id = fields.Many2one(
        "hms.consultation",
        string="Consultation",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Medicine / Product",
        required=True,
    )
    dosage = fields.Char(string="Dosage")
    frequency = fields.Char(string="Frequency")
    duration_days = fields.Integer(string="Duration (days)")
    instructions = fields.Text(string="Instructions")
