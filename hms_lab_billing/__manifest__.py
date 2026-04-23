{
    "name": "Hospital Management — Lab Billing",
    "summary": "Bill lab tests by adding service products to the patient's sale order.",
    "description": """
Bridge module between ``hms_lab`` and ``hms_billing``.  Adds a "Bill" button
on lab requests that creates or extends a draft sale order with one line per
ordered test type (using the test type's linked service product).
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_lab", "hms_billing"],
    "data": [
        "views/hms_lab_request_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
