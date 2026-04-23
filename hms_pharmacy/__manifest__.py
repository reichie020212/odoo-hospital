{
    "name": "Hospital Management — Pharmacy",
    "summary": "Prescription dispensing via stock.picking with FEFO expiry tracking.",
    "description": """
Turns prescription lines from ``hms_clinical`` into outgoing stock pickings.
A pharmacist validates the pick; Odoo's FEFO removal strategy on the Pharmacy
location ensures the nearest-expiry lot is consumed first.  Extends
``product.product`` with an ``is_medicine`` flag for easy filtering.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_clinical", "stock", "product_expiry"],
    "data": [
        "security/hms_pharmacy_security.xml",
        "security/ir.model.access.csv",
        "data/hms_pharmacy_data.xml",
        "views/product_product_views.xml",
        "views/hms_consultation_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
