{
    "name": "Hospital Management — Insurance",
    "summary": "Insurance policies, co-pay split billing, and TPA integration.",
    "description": """
Adds insurance policy management for patients and a split-billing engine that
automatically calculates the insurer's share and the patient's co-pay when
creating sale orders from consultations, lab requests, or admissions.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_billing"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/hms_insurance_data.xml",
        "views/hms_insurance_policy_views.xml",
        "views/res_partner_views.xml",
        "views/hms_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
