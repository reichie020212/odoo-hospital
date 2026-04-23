from odoo import models


class HmsConsultation(models.Model):
    _inherit = "hms.consultation"

    def _get_billing_product(self):
        """Resolve the service product — unchanged, just inherited for clarity."""
        return super()._get_billing_product()

    def action_create_sale_order(self):
        """Extend: after creating the SO, apply insurance discount if policy exists."""
        result = super().action_create_sale_order()
        self._apply_insurance_discount()
        return result

    def _apply_insurance_discount(self):
        """If the patient has an active insurance policy, add a negative discount line."""
        self.ensure_one()
        if not self.sale_order_id:
            return
        policy = self.env["hms.insurance.policy"].get_active_policy(self.patient_id.id)
        if not policy:
            return

        discount_product = self.env.ref("hms_insurance.product_insurance_discount", raise_if_not_found=False)
        if not discount_product:
            return

        coverage = policy.coverage_percentage / 100.0
        for line in self.sale_order_id.order_line:
            if line.product_id == discount_product:
                return  # already applied

        total = sum(self.sale_order_id.order_line.mapped("price_subtotal"))
        insurer_share = total * coverage

        if insurer_share > 0:
            self.env["sale.order.line"].create(
                {
                    "order_id": self.sale_order_id.id,
                    "product_id": discount_product.id,
                    "name": (
                        f"Insurance discount — {policy.insurance_company_id.name} "
                        f"({policy.name}, {policy.coverage_percentage}%)"
                    ),
                    "product_uom_qty": 1,
                    "price_unit": -insurer_share,
                }
            )
