from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """Extend: after dispensing validation, add dispensed products to the consultation's SO."""
        res = super().button_validate()
        for picking in self:
            consultation = picking.hms_consultation_id
            if not consultation or picking.state != "done":
                continue
            so = consultation.sale_order_id
            if not so:
                so = self.env["sale.order"].create(
                    {
                        "partner_id": consultation.patient_id.id,
                        "origin": consultation.name,
                    }
                )
                consultation.sale_order_id = so.id
            for move in picking.move_ids.filtered(lambda m: m.state == "done"):
                self.env["sale.order.line"].create(
                    {
                        "order_id": so.id,
                        "product_id": move.product_id.id,
                        "name": f"{consultation.name} — {move.product_id.name} (dispensed)",
                        "product_uom_qty": move.quantity,
                    }
                )
        return res
