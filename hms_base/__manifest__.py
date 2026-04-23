{
    "name": "Hospital Management — Base",
    "summary": "Patient and medical-staff extensions on top of Odoo CE.",
    "description": """
Hospital Management base module.

Extends ``res.partner`` with the patient flag and medical demographics, extends
``hr.employee`` with clinical-staff flags, and introduces the
``hms.specialization`` master model plus the Hospital application security
groups.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["contacts", "hr", "mail"],
    "data": [
        "security/hms_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/hms_specialization_data.xml",
        "views/hms_specialization_views.xml",
        "views/hr_employee_views.xml",
        "views/res_partner_views.xml",
        "views/hms_menus.xml",
    ],
    "application": True,
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
