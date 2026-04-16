from odoo import api, fields, models


class HmsVital(models.Model):
    _name = "hms.vital"
    _description = "Vital Signs"
    _order = "id desc"

    consultation_id = fields.Many2one(
        "hms.consultation",
        string="Consultation",
        required=True,
        ondelete="cascade",
    )
    bp_systolic = fields.Integer(string="BP Systolic (mmHg)")
    bp_diastolic = fields.Integer(string="BP Diastolic (mmHg)")
    heart_rate = fields.Integer(string="Heart Rate (bpm)")
    temperature = fields.Float(string="Temperature (°C)", digits=(4, 1))
    spo2 = fields.Integer(string="SpO₂ (%)")
    weight = fields.Float(string="Weight (kg)", digits=(5, 2))
    height = fields.Float(string="Height (cm)", digits=(5, 1))
    bmi = fields.Float(
        string="BMI",
        compute="_compute_bmi",
        store=True,
        digits=(4, 1),
    )

    @api.depends("weight", "height")
    def _compute_bmi(self):
        for vital in self:
            if vital.weight and vital.height:
                height_m = vital.height / 100.0
                vital.bmi = vital.weight / (height_m**2)
            else:
                vital.bmi = 0.0
