from odoo import api, fields, models
from odoo.exceptions import UserError


class HmsConsultation(models.Model):
    _inherit = "hms.consultation"

    picking_ids = fields.One2many(
        "stock.picking",
        "hms_consultation_id",
        string="Dispensing Orders",
        readonly=True,
    )
    dispensing_count = fields.Integer(
        string="Dispensing Orders",
        compute="_compute_dispensing_count",
    )

    @api.depends("picking_ids")
    def _compute_dispensing_count(self):
        for cons in self:
            cons.dispensing_count = len(cons.picking_ids)

    def action_create_dispensing(self):
        """Create an outgoing stock.picking from pending, dispensable prescription lines."""
        self.ensure_one()
        lines = self.prescription_line_ids.filtered(
            lambda line: line.dispensing_state == "pending" and line.product_id.type in ("product", "consu")
        )
        if not lines:
            raise UserError("No pending dispensable prescription lines found.")

        picking_type = self.env.ref("hms_pharmacy.picking_type_dispensing", raise_if_not_found=False)
        if not picking_type:
            raise UserError("Dispensing picking type not found. Please check hms_pharmacy configuration.")

        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "partner_id": self.patient_id.id,
                "origin": self.name,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": picking_type.default_location_dest_id.id,
                "hms_consultation_id": self.id,
            }
        )

        for line in lines:
            move = self.env["stock.move"].create(
                {
                    "name": f"{self.name} — {line.product_id.name}",
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty or 1.0,
                    "product_uom": line.product_id.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": picking.location_id.id,
                    "location_dest_id": picking.location_dest_id.id,
                }
            )
            line.move_id = move.id

        picking.action_confirm()
        picking.action_assign()

        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "res_id": picking.id,
            "view_mode": "form",
        }

    def action_view_dispensing(self):
        self.ensure_one()
        if self.dispensing_count == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "res_id": self.picking_ids.id,
                "view_mode": "form",
            }
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "domain": [("id", "in", self.picking_ids.ids)],
        }
