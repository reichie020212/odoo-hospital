from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    hms_consultation_id = fields.Many2one(
        "hms.consultation",
        string="Consultation",
        readonly=True,
        copy=True,  # preserve link on backorders
    )

    def button_validate(self):
        """Override to mark prescription lines as dispensed after validation."""
        res = super().button_validate()
        for picking in self:
            if picking.hms_consultation_id and picking.state == "done":
                move_ids = picking.move_ids.ids
                lines = picking.hms_consultation_id.prescription_line_ids.filtered(
                    lambda line, ids=move_ids: line.move_id.id in ids
                )
                lines.write({"dispensing_state": "dispensed"})
        return res
