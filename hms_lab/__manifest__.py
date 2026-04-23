{
    "name": "Hospital Management — Laboratory",
    "summary": "Lab test requests, panel expansion, results, and validation workflow.",
    "description": """
Introduces ``hms.lab.request`` for ordering lab tests from a consultation,
``hms.lab.test.type`` for defining individual tests and panels (e.g. CBC),
and ``hms.lab.result`` for recording values with automatic abnormal-flag
detection based on normal ranges.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_clinical"],
    "data": [
        "security/hms_lab_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/hms_lab_test_type_data.xml",
        "views/hms_lab_test_type_views.xml",
        "views/hms_lab_request_views.xml",
        "views/hms_consultation_views.xml",
        "views/hms_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
