{
    "name": "Hospital Management — Billing",
    "summary": "Direct-pay invoicing from consultations via sale.order.",
    "description": """
Adds a billing workflow to ``hms.consultation``: a one-click button creates a
draft ``sale.order`` for the patient using the consultation fee defined on the
appointment type.  A "Billed" ribbon prevents double-invoicing.  Also extends
``hms.appointment.type`` with a billing-product link.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_clinical", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/hms_billing_data.xml",
        "views/hms_consultation_views.xml",
        "views/hms_appointment_type_views.xml",
    ],
    "installable": True,
}
