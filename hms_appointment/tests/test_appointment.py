from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCalendarEventAppointment(TransactionCase):
    """Tests for the medical-appointment extension on calendar.event."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Test Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Test", "is_doctor": True})
        cls.appt_type = cls.env["hms.appointment.type"].create({"name": "Checkup", "default_duration": 0.75})
        cls.start = datetime.now().replace(second=0, microsecond=0)
        cls.stop = cls.start + timedelta(hours=1)

    def _create_appointment(self, **overrides):
        vals = {
            "name": "Test Appointment",
            "start": self.start,
            "stop": self.stop,
            "is_appointment": True,
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
        }
        vals.update(overrides)
        return self.env["calendar.event"].create(vals)

    # -- Constraint tests -------------------------------------------------

    def test_constraint_requires_patient(self):
        """is_appointment=True without a patient must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_appointment(patient_id=False)

    def test_constraint_requires_doctor(self):
        """is_appointment=True without a doctor must raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._create_appointment(doctor_id=False)

    def test_non_appointment_no_constraint(self):
        """is_appointment=False should allow missing patient/doctor."""
        event = self.env["calendar.event"].create(
            {
                "name": "Team Meeting",
                "start": self.start,
                "stop": self.stop,
                "is_appointment": False,
            }
        )
        self.assertFalse(event.patient_id)
        self.assertFalse(event.doctor_id)

    # -- State transition tests -------------------------------------------

    def test_default_state_is_draft(self):
        appt = self._create_appointment()
        self.assertEqual(appt.appointment_state, "draft")

    def test_confirm(self):
        appt = self._create_appointment()
        appt.action_confirm()
        self.assertEqual(appt.appointment_state, "confirmed")

    def test_check_in(self):
        appt = self._create_appointment()
        appt.action_confirm()
        appt.action_check_in()
        self.assertEqual(appt.appointment_state, "checked_in")

    def test_done(self):
        appt = self._create_appointment()
        appt.action_confirm()
        appt.action_check_in()
        appt.action_done()
        self.assertEqual(appt.appointment_state, "done")

    def test_cancel(self):
        appt = self._create_appointment()
        appt.action_cancel()
        self.assertEqual(appt.appointment_state, "cancelled")

    def test_reset_to_draft(self):
        appt = self._create_appointment()
        appt.action_cancel()
        appt.action_draft()
        self.assertEqual(appt.appointment_state, "draft")

    def test_full_lifecycle(self):
        """Walk an appointment through draft → confirmed → checked_in → done."""
        appt = self._create_appointment()
        self.assertEqual(appt.appointment_state, "draft")
        appt.action_confirm()
        self.assertEqual(appt.appointment_state, "confirmed")
        appt.action_check_in()
        self.assertEqual(appt.appointment_state, "checked_in")
        appt.action_done()
        self.assertEqual(appt.appointment_state, "done")

    # -- Onchange test ----------------------------------------------------

    def test_onchange_type_sets_duration(self):
        """Selecting an appointment type should update the event duration."""
        appt = self._create_appointment(appointment_type_id=self.appt_type.id)
        appt._onchange_appointment_type_id()
        self.assertEqual(appt.duration, 0.75)

    # -- Attendee sync tests -----------------------------------------------

    def test_create_syncs_patient_to_attendees(self):
        """Patient should be added to partner_ids (attendees) on create."""
        appt = self._create_appointment()
        self.assertIn(self.patient, appt.partner_ids)

    def test_create_syncs_doctor_to_attendees(self):
        """Doctor's linked user partner should be added to attendees on create."""
        user = self.env["res.users"].create({"name": "Dr. User", "login": "dr_user_sync_test"})
        self.doctor.user_id = user
        appt = self._create_appointment()
        self.assertIn(user.partner_id, appt.partner_ids)

    def test_write_syncs_new_patient_to_attendees(self):
        """Changing patient_id via write should add the new patient to attendees."""
        appt = self._create_appointment()
        new_patient = self.env["res.partner"].create({"name": "New Patient", "is_patient": True})
        appt.write({"patient_id": new_patient.id})
        self.assertIn(new_patient, appt.partner_ids)
