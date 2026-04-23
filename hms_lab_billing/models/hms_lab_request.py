from odoo import api, fields, models
from odoo.exceptions import UserError


class HmsLabRequest(models.Model):
    _inherit = "hms.lab.request"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        readonly=True,
        copy=False,
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
        for req in self:
            req.billing_state = "billed" if req.sale_order_id else "not_billed"

    def action_create_lab_bill(self):
        """Create a draft sale order with one line per billable test type."""
        self.ensure_one()
        if self.sale_order_id:
            raise UserError("This lab request already has a linked sale order.")

        billable_types = self.env["hms.lab.test.type"]
        for test_type in self.test_type_ids:
            if test_type.is_panel:
                billable_types |= test_type.child_ids.filtered("product_id")
            elif test_type.product_id:
                billable_types |= test_type

        if not billable_types:
            raise UserError("No billable test types found. Ensure each test type has a billing product set.")

        order_lines = [
            (
                0,
                0,
                {
                    "product_id": tt.product_id.id,
                    "name": f"{self.name} — {tt.name}",
                    "product_uom_qty": 1,
                },
            )
            for tt in billable_types
        ]
        so = self.env["sale.order"].create(
            {
                "partner_id": self.patient_id.id,
                "origin": self.name,
                "order_line": order_lines,
            }
        )
        self.sale_order_id = so.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": so.id,
            "view_mode": "form",
        }

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
        }
