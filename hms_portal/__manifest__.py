{
    "name": "Hospital Management — Patient Portal",
    "summary": "View-only patient portal for appointments, consultations, and vitals.",
    "description": """
Extends Odoo's portal so patients can view their medical appointments,
consultations (with vitals and prescriptions), and lab requests.  Read-only
— patients cannot create or modify records from the portal.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["portal", "hms_appointment", "hms_clinical"],
    "data": [
        "security/hms_portal_security.xml",
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
