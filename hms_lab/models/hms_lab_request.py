from odoo import api, fields, models
from odoo.exceptions import UserError


class HmsLabRequest(models.Model):
    _name = "hms.lab.request"
    _description = "Lab Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

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
        string="Requesting Doctor",
        required=True,
        domain=[("is_doctor", "=", True)],
        tracking=True,
    )
    consultation_id = fields.Many2one(
        "hms.consultation",
        string="Consultation",
    )
    date = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("collected", "Sample Collected"),
            ("processing", "Processing"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    test_type_ids = fields.Many2many(
        "hms.lab.test.type",
        string="Ordered Tests",
        help="Select individual tests or panels. Use 'Generate Results' to expand panels into result lines.",
    )
    result_ids = fields.One2many("hms.lab.result", "request_id", string="Results")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("hms.lab.request") or "New"
        return super().create(vals_list)

    def action_generate_results(self):
        """Create result lines from ordered test types, expanding panels into individual tests."""
        for request in self:
            if request.state not in ("draft", "collected"):
                raise UserError("Results can only be generated while the request is in Draft or Collected state.")
            if not request.test_type_ids:
                raise UserError("Please select at least one test type before generating results.")
            existing_type_ids = set(request.result_ids.mapped("test_type_id").ids)
            for test_type in request.test_type_ids:
                if test_type.is_panel:
                    for child in test_type.child_ids:
                        if child.id not in existing_type_ids:
                            self.env["hms.lab.result"].create({"request_id": request.id, "test_type_id": child.id})
                            existing_type_ids.add(child.id)
                elif test_type.id not in existing_type_ids:
                    self.env["hms.lab.result"].create({"request_id": request.id, "test_type_id": test_type.id})
                    existing_type_ids.add(test_type.id)

    # -- State transitions ------------------------------------------------

    def action_collect(self):
        self.write({"state": "collected"})

    def action_process(self):
        self.write({"state": "processing"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_draft(self):
        self.write({"state": "draft"})
