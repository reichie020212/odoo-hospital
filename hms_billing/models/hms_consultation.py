from odoo import api, fields, models
from odoo.exceptions import UserError


class HmsConsultation(models.Model):
    _inherit = "hms.consultation"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        readonly=True,
        copy=False,
    )
    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        compute="_compute_invoice_ids",
    )
    invoice_count = fields.Integer(
        string="Invoice Count",
        compute="_compute_invoice_ids",
    )
    billing_state = fields.Selection(
        [
            ("not_billed", "Not Billed"),
            ("billed", "Billed"),
        ],
        string="Billing Status",
        compute="_compute_billing_state",
        store=True,
    )

    @api.depends("sale_order_id")
    def _compute_billing_state(self):
        for cons in self:
            cons.billing_state = "billed" if cons.sale_order_id else "not_billed"

    @api.depends("sale_order_id.invoice_ids")
    def _compute_invoice_ids(self):
        for cons in self:
            cons.invoice_ids = cons.sale_order_id.invoice_ids if cons.sale_order_id else False
            cons.invoice_count = len(cons.invoice_ids) if cons.invoice_ids else 0

    # -- Actions ----------------------------------------------------------

    def action_create_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            raise UserError("This consultation already has a linked sale order.")
        product = self._get_billing_product()
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.patient_id.id,
                "origin": self.name,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": f"{self.name} — {product.name}",
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        self.sale_order_id = sale_order.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": sale_order.id,
            "view_mode": "form",
        }

    def _get_billing_product(self):
        """Resolve the service product from the linked appointment type."""
        if self.appointment_id and self.appointment_id.appointment_type_id:
            product = self.appointment_id.appointment_type_id.product_id
            if product:
                return product
        raise UserError(
            "Cannot determine a billing product. Make sure the consultation is "
            "linked to an appointment whose type has a billing product set."
        )

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
        }

    def action_view_invoices(self):
        self.ensure_one()
        invoices = self.invoice_ids
        if len(invoices) == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "res_id": invoices.id,
                "view_mode": "form",
            }
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("id", "in", invoices.ids)],
        }
