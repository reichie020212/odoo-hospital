{
    "name": "Hospital Management — Pharmacy Billing",
    "summary": "Add dispensed medicines to the patient's sale order on picking validation.",
    "description": """
Bridge module between ``hms_pharmacy`` and ``hms_billing``.  When a dispensing
picking is validated, each dispensed product is automatically added as a line
to the consultation's existing sale order (from ``hms_billing``), or a new
draft SO is created if one doesn't exist.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_pharmacy", "hms_billing"],
    "installable": True,
    "auto_install": True,
}
