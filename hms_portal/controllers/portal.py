from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class HmsPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if "appointment_count" in counters:
            values["appointment_count"] = (
                request.env["calendar.event"]
                .sudo()
                .search_count([("is_appointment", "=", True), ("patient_id", "=", partner.id)])
            )
        if "consultation_count" in counters:
            values["consultation_count"] = (
                request.env["hms.consultation"].sudo().search_count([("patient_id", "=", partner.id)])
            )
        return values

    # -- Appointments -----------------------------------------------------

    @http.route(
        ["/my/appointments", "/my/appointments/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_appointments(self, page=1, sortby=None, **kw):
        partner = request.env.user.partner_id
        domain = [("is_appointment", "=", True), ("patient_id", "=", partner.id)]
        appointments = request.env["calendar.event"].sudo().search(domain, order="start desc")
        values = {
            "appointments": appointments,
            "page_name": "appointments",
        }
        return request.render("hms_portal.portal_my_appointments", values)

    @http.route(
        "/my/appointments/<int:appointment_id>",
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_appointment(self, appointment_id, **kw):
        partner = request.env.user.partner_id
        appointment = request.env["calendar.event"].sudo().browse(appointment_id)
        if not appointment.exists() or appointment.patient_id.id != partner.id:
            return request.redirect("/my")
        values = {
            "appointment": appointment,
            "page_name": "appointment",
        }
        return request.render("hms_portal.portal_my_appointment", values)

    # -- Consultations ----------------------------------------------------

    @http.route(
        ["/my/consultations", "/my/consultations/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_consultations(self, page=1, sortby=None, **kw):
        partner = request.env.user.partner_id
        domain = [("patient_id", "=", partner.id)]
        consultations = request.env["hms.consultation"].sudo().search(domain, order="date desc")
        values = {
            "consultations": consultations,
            "page_name": "consultations",
        }
        return request.render("hms_portal.portal_my_consultations", values)

    @http.route(
        "/my/consultations/<int:consultation_id>",
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_consultation(self, consultation_id, **kw):
        partner = request.env.user.partner_id
        consultation = request.env["hms.consultation"].sudo().browse(consultation_id)
        if not consultation.exists() or consultation.patient_id.id != partner.id:
            return request.redirect("/my")
        values = {
            "consultation": consultation,
            "page_name": "consultation",
        }
        return request.render("hms_portal.portal_my_consultation", values)
