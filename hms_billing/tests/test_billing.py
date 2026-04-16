from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsBilling(TransactionCase):
    """Tests for the hms_billing direct-pay invoicing workflow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Bill Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Bill", "is_doctor": True})

        cls.product = cls.env["product.product"].create(
            {"name": "Test Consultation Fee", "type": "service", "list_price": 100.0}
        )
        cls.appt_type = cls.env["hms.appointment.type"].create(
            {"name": "Billing Checkup", "default_duration": 0.5, "product_id": cls.product.id}
        )

        start = datetime.now().replace(second=0, microsecond=0)
        cls.appointment = cls.env["calendar.event"].create(
            {
                "name": "Test Appt",
                "start": start,
                "stop": start + timedelta(hours=1),
                "is_appointment": True,
                "patient_id": cls.patient.id,
                "doctor_id": cls.doctor.id,
                "appointment_type_id": cls.appt_type.id,
            }
        )

        cls.consultation = cls.env["hms.consultation"].create(
            {
                "patient_id": cls.patient.id,
                "doctor_id": cls.doctor.id,
                "appointment_id": cls.appointment.id,
            }
        )

    def test_billing_state_default_not_billed(self):
        self.assertEqual(self.consultation.billing_state, "not_billed")

    def test_create_sale_order(self):
        self.consultation.action_create_sale_order()
        self.assertTrue(self.consultation.sale_order_id)
        so = self.consultation.sale_order_id
        self.assertEqual(so.partner_id, self.patient)
        self.assertEqual(so.origin, self.consultation.name)
        self.assertEqual(len(so.order_line), 1)
        self.assertEqual(so.order_line.product_id, self.product)

    def test_billing_state_billed_after_so(self):
        self.consultation.action_create_sale_order()
        self.assertEqual(self.consultation.billing_state, "billed")

    def test_double_billing_prevented(self):
        self.consultation.action_create_sale_order()
        with self.assertRaises(UserError):
            self.consultation.action_create_sale_order()

    def test_no_product_raises(self):
        """If the appointment type has no billing product, action should raise."""
        appt_type_no_prod = self.env["hms.appointment.type"].create(
            {"name": "No Product Type", "default_duration": 0.5}
        )
        start = datetime.now().replace(second=0, microsecond=0)
        appointment = self.env["calendar.event"].create(
            {
                "name": "NoProd Appt",
                "start": start,
                "stop": start + timedelta(hours=1),
                "is_appointment": True,
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "appointment_type_id": appt_type_no_prod.id,
            }
        )
        cons = self.env["hms.consultation"].create(
            {
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "appointment_id": appointment.id,
            }
        )
        with self.assertRaises(UserError):
            cons.action_create_sale_order()

    def test_no_appointment_raises(self):
        """If the consultation has no appointment, action should raise."""
        cons = self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        with self.assertRaises(UserError):
            cons.action_create_sale_order()

    def test_action_view_sale_order(self):
        self.consultation.action_create_sale_order()
        action = self.consultation.action_view_sale_order()
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(action["res_id"], self.consultation.sale_order_id.id)

    def test_seed_product_exists(self):
        product = self.env.ref("hms_billing.product_general_consultation_fee", raise_if_not_found=False)
        self.assertTrue(product, "Seed product 'General Consultation Fee' should exist.")

    def test_seed_appointment_type_linked(self):
        appt_type = self.env.ref("hms_appointment.appointment_type_general", raise_if_not_found=False)
        self.assertTrue(appt_type)
        self.assertTrue(appt_type.product_id, "General Consultation type should have a billing product.")
