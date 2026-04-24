from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CreateStaffWizard(models.TransientModel):
    _name = "hms.create.staff.wizard"
    _description = "Create Hospital Staff (Doctor/Nurse)"

    name = fields.Char(required=True)
    email = fields.Char(string="Login Email", required=True)
    phone = fields.Char()
    role = fields.Selection(
        [
            ("doctor", "Doctor"),
            ("nurse", "Nurse"),
        ],
        required=True,
        default="doctor",
    )
    specialization_id = fields.Many2one(
        "hms.specialization",
        string="Specialization",
    )
    license_no = fields.Char(string="License Number")
    job_title = fields.Char()
    group_level = fields.Selection(
        [
            ("user", "Hospital User"),
            ("manager", "Hospital Manager"),
        ],
        string="Access Level",
        required=True,
        default="user",
    )

    @api.onchange("role")
    def _onchange_role(self):
        if self.role == "nurse":
            self.specialization_id = False

    def action_create(self):
        self.ensure_one()

        # Validate email uniqueness
        existing = self.env["res.users"].sudo().search([("login", "=", self.email)], limit=1)
        if existing:
            raise ValidationError(f"A user with login '{self.email}' already exists.")

        # Create employee
        employee_vals = {
            "name": self.name,
            "work_email": self.email,
            "work_phone": self.phone or False,
            "job_title": self.job_title or False,
            "is_doctor": self.role == "doctor",
            "is_nurse": self.role == "nurse",
        }
        if self.specialization_id and self.role == "doctor":
            employee_vals["specialization_id"] = self.specialization_id.id
        if self.license_no:
            employee_vals["license_no"] = self.license_no

        employee = self.env["hr.employee"].create(employee_vals)

        # Determine group
        if self.group_level == "manager":
            group = self.env.ref("hms_base.group_hms_manager")
        else:
            group = self.env.ref("hms_base.group_hms_user")

        # Create user linked to the employee's partner
        user = self.env["res.users"].create(
            {
                "name": self.name,
                "login": self.email,
                "partner_id": employee.work_contact_id.id if employee.work_contact_id else None,
                "group_ids": [(4, group.id)],
            }
        )

        # Link user back to employee
        employee.user_id = user.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.employee",
            "res_id": employee.id,
            "view_mode": "form",
            "target": "current",
        }
