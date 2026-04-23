{
    "name": "Hospital Management — Website",
    "summary": "Public hospital website with doctor profiles, services, and contact page.",
    "description": """
Creates a public-facing hospital website using Odoo's CMS engine.  Displays
doctor profiles (from ``hr.employee``) and medical services (from
``hms.appointment.type``) with ``website_published`` gating.  Integrates with
the patient portal via login/CTA buttons.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["website", "hms_base", "hms_appointment"],
    "data": [
        "views/website_templates.xml",
        "data/website_data.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
