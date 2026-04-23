from odoo import api, fields, models


class HmsLabResult(models.Model):
    _name = "hms.lab.result"
    _description = "Lab Result"
    _order = "id"

    request_id = fields.Many2one(
        "hms.lab.request",
        string="Lab Request",
        required=True,
        ondelete="cascade",
    )
    test_type_id = fields.Many2one(
        "hms.lab.test.type",
        string="Test",
        required=True,
        domain=[("is_panel", "=", False)],
    )
    value = fields.Float(string="Result Value")
    value_text = fields.Char(
        string="Result Text",
        help="For non-numeric results (e.g. Positive/Negative).",
    )
    unit = fields.Char(related="test_type_id.unit", readonly=True)
    normal_range_min = fields.Float(related="test_type_id.normal_range_min", readonly=True)
    normal_range_max = fields.Float(related="test_type_id.normal_range_max", readonly=True)
    is_abnormal = fields.Boolean(
        string="Abnormal",
        compute="_compute_is_abnormal",
        store=True,
    )

    @api.depends("value", "test_type_id.normal_range_min", "test_type_id.normal_range_max")
    def _compute_is_abnormal(self):
        # TODO(hms_lab): only numeric ranges are checked. For qualitative tests
        # (e.g. Positive/Negative via value_text), the tech must toggle
        # is_abnormal manually. Add qualitative matching if needed later.
        for result in self:
            low = result.test_type_id.normal_range_min
            high = result.test_type_id.normal_range_max
            if low or high:
                result.is_abnormal = result.value < low or result.value > high
            else:
                result.is_abnormal = False
