from odoo import api, fields, models
from odoo.exceptions import UserError


class HmsAdmission(models.Model):
    _name = "hms.admission"
    _description = "Patient Admission"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "admission_date desc, id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        default="New",
        copy=False,
        readonly=True,
    )
    patient_id = fields.Many2one(
        "res.partner",
        string="Patient",
        required=True,
        domain=[("is_patient", "=", True)],
        tracking=True,
    )
    doctor_id = fields.Many2one(
        "hr.employee",
        string="Attending Doctor",
        required=True,
        domain=[("is_doctor", "=", True)],
        tracking=True,
    )
    bed_id = fields.Many2one(
        "hms.bed",
        string="Bed",
        required=True,
        tracking=True,
    )
    ward_id = fields.Many2one(related="bed_id.ward_id", store=True, readonly=True)
    consultation_id = fields.Many2one("hms.consultation", string="Consultation")
    admission_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    discharge_date = fields.Datetime(tracking=True)
    diagnosis = fields.Text()
    notes = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("admitted", "Admitted"),
            ("discharged", "Discharged"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    sale_order_id = fields.Many2one("sale.order", string="Room Charges SO", readonly=True, copy=False)
    last_charge_date = fields.Date(
        string="Last Room Charge Date",
        copy=False,
        help="Tracks the last date a room-charge line was added by the daily CRON.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("hms.admission") or "New"
        return super().create(vals_list)

    # -- State transitions ------------------------------------------------

    def action_admit(self):
        for admission in self:
            if admission.bed_id.state != "available":
                raise UserError(
                    f"Bed '{admission.bed_id.name}' is not available (current state: {admission.bed_id.state})."
                )
            restriction = admission.ward_id.gender_restriction
            patient_gender = admission.patient_id.gender
            if restriction != "mixed" and patient_gender and patient_gender != restriction:
                raise UserError(f"Ward '{admission.ward_id.name}' is restricted to {restriction} patients.")
            admission.bed_id.state = "occupied"
            if not admission.sale_order_id:
                so = self.env["sale.order"].create(
                    {
                        "partner_id": admission.patient_id.id,
                        "origin": admission.name,
                    }
                )
                admission.sale_order_id = so.id
        self.write({"state": "admitted"})

    def action_discharge(self):
        for admission in self:
            admission.discharge_date = fields.Datetime.now()
            admission.bed_id.state = "cleaning"
        self.write({"state": "discharged"})

    def action_cancel(self):
        for admission in self:
            if admission.state == "admitted":
                admission.bed_id.state = "available"
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})

    # -- CRON: daily room charges -----------------------------------------

    @api.model
    def _cron_daily_room_charges(self):
        """Add a room-charge SO line for each active admission (runs daily)."""
        today = fields.Date.context_today(self)
        active_admissions = self.search([("state", "=", "admitted")])
        for admission in active_admissions:
            if admission.last_charge_date and admission.last_charge_date >= today:
                continue
            product = admission.bed_id.product_id
            if not product or not admission.sale_order_id:
                continue
            self.env["sale.order.line"].create(
                {
                    "order_id": admission.sale_order_id.id,
                    "product_id": product.id,
                    "name": f"{admission.name} — Room charge {today}",
                    "product_uom_qty": 1,
                }
            )
            admission.last_charge_date = today

    # -- Navigation -------------------------------------------------------

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
        }
