{
    "name": "Hospital Management — Appointments",
    "summary": "Medical appointment scheduling on calendar.event.",
    "description": """
Extends ``calendar.event`` with medical-appointment semantics: patient, doctor,
appointment type, and a five-state workflow (draft → confirmed → checked-in →
done / cancelled).  Appointments are isolated from regular calendar meetings via
the ``is_appointment`` flag.
    """,
    "version": "19.0.1.0.0",
    "author": "Red",
    "license": "LGPL-3",
    "category": "Healthcare",
    "depends": ["hms_base", "calendar"],
    "data": [
        "security/ir.model.access.csv",
        "data/hms_appointment_type_data.xml",
        "views/hms_appointment_type_views.xml",
        "views/calendar_event_views.xml",
        "views/hms_appointment_views.xml",
        "views/hms_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
}
