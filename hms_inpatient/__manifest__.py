{
    "name": "Hospital Management — Inpatient",
    "summary": "Ward and bed management, admissions, discharge, daily room-charge billing.",
    "description": """
Introduces ``hms.ward``, ``hms.bed``, and ``hms.admission`` for inpatient
care.  Admitting a patient marks the bed as occupied and creates a draft
sale order.  A daily CRON adds room-charge lines to the order based on the
bed's product.  Discharge frees the bed and finalizes the billing period.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_clinical", "hms_billing"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/hms_inpatient_data.xml",
        "views/hms_ward_views.xml",
        "views/hms_bed_views.xml",
        "views/hms_admission_views.xml",
        "views/hms_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
