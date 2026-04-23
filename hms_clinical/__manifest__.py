{
    "name": "Hospital Management — Clinical / EMR",
    "summary": "Consultations, vitals, and prescription lines — the EMR core.",
    "description": """
The clinical module introduces ``hms.consultation`` (with chatter and
activities), ``hms.vital`` for standard vital-sign recording, and
``hms.prescription.line`` for medication orders.  It also wires the
patient-count smart button on employees and adds a Medical History page on the
patient form.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_appointment", "product"],
    "data": [
        "security/hms_clinical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/hms_consultation_views.xml",
        "views/res_partner_views.xml",
        "views/hms_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
