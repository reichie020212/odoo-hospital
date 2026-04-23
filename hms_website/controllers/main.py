import logging

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class HmsWebsite(http.Controller):
    @http.route("/hospital", type="http", auth="public", website=True, sitemap=True)
    def hospital_home(self, **kw):
        doctors = (
            request.env["hr.employee"]
            .sudo()
            .search([("is_doctor", "=", True), ("website_published", "=", True)], limit=4)
        )
        services = request.env["hms.appointment.type"].sudo().search([("website_published", "=", True)], limit=6)
        company = request.env.company
        return request.render(
            "hms_website.hospital_home",
            {"doctors": doctors, "services": services, "company": company},
        )

    @http.route("/hospital/doctors", type="http", auth="public", website=True, sitemap=True)
    def hospital_doctors(self, **kw):
        doctors = request.env["hr.employee"].sudo().search([("is_doctor", "=", True), ("website_published", "=", True)])
        specializations = request.env["hms.specialization"].sudo().search([("active", "=", True)])
        return request.render(
            "hms_website.hospital_doctors",
            {"doctors": doctors, "specializations": specializations},
        )

    @http.route("/hospital/services", type="http", auth="public", website=True, sitemap=True)
    def hospital_services(self, **kw):
        services = request.env["hms.appointment.type"].sudo().search([("website_published", "=", True)])
        return request.render(
            "hms_website.hospital_services",
            {"services": services},
        )

    @http.route("/hospital/contact", type="http", auth="public", website=True, sitemap=True)
    def hospital_contact(self, **kw):
        company = request.env.company
        return request.render(
            "hms_website.hospital_contact",
            {"company": company},
        )

    # -- Patient Registration ------------------------------------------------

    @http.route("/hospital/register", type="http", auth="public", website=True, sitemap=True)
    def hospital_register(self, **kw):
        return request.render(
            "hms_website.hospital_register",
            {"error": None, "success": False, "values": {}},
        )

    @http.route("/hospital/register/submit", type="http", auth="public", website=True, methods=["POST"], csrf=True)
    def hospital_register_submit(self, **post):
        values = {
            "name": post.get("name", "").strip(),
            "email": post.get("email", "").strip(),
            "phone": post.get("phone", "").strip(),
            "password": post.get("password", ""),
            "password_confirm": post.get("password_confirm", ""),
            "date_of_birth": post.get("date_of_birth", ""),
            "gender": post.get("gender", ""),
        }

        # Validation
        if not values["name"] or not values["email"] or not values["password"]:
            return request.render(
                "hms_website.hospital_register",
                {"error": "Name, email, and password are required.", "success": False, "values": values},
            )
        if values["password"] != values["password_confirm"]:
            return request.render(
                "hms_website.hospital_register",
                {"error": "Passwords do not match.", "success": False, "values": values},
            )
        if len(values["password"]) < 8:
            return request.render(
                "hms_website.hospital_register",
                {"error": "Password must be at least 8 characters.", "success": False, "values": values},
            )

        # Check for existing user
        existing = request.env["res.users"].sudo().search([("login", "=", values["email"])], limit=1)
        if existing:
            return request.render(
                "hms_website.hospital_register",
                {"error": "An account with this email already exists.", "success": False, "values": values},
            )

        try:
            # Create partner flagged as patient
            partner_vals = {
                "name": values["name"],
                "email": values["email"],
                "phone": values["phone"] or False,
                "is_patient": True,
            }
            if values["gender"]:
                partner_vals["gender"] = values["gender"]
            if values["date_of_birth"]:
                partner_vals["date_of_birth"] = values["date_of_birth"]

            partner = request.env["res.partner"].sudo().create(partner_vals)

            # Create portal user linked to the partner
            portal_group = request.env.ref("base.group_portal")
            request.env["res.users"].sudo().create(
                {
                    "name": values["name"],
                    "login": values["email"],
                    "password": values["password"],
                    "partner_id": partner.id,
                    "groups_id": [(6, 0, [portal_group.id])],
                }
            )

            return request.render(
                "hms_website.hospital_register",
                {"error": None, "success": True, "values": {}},
            )

        except ValidationError as e:
            return request.render(
                "hms_website.hospital_register",
                {"error": str(e), "success": False, "values": values},
            )
        except Exception:
            _logger.exception("Patient registration failed")
            return request.render(
                "hms_website.hospital_register",
                {
                    "error": "Registration failed. Please try again or contact the hospital.",
                    "success": False,
                    "values": values,
                },
            )
