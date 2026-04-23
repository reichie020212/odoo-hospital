from odoo import http
from odoo.http import request


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
