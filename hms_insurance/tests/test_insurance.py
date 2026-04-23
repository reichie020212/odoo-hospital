from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsInsurance(TransactionCase):
    """Tests for insurance policy detection and co-pay split billing."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.insurer = cls.env["res.partner"].create({"name": "MediCare Insurance", "is_insurance_company": True})
        cls.patient = cls.env["res.partner"].create({"name": "Insured Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Insurance", "is_doctor": True})

        cls.product_fee = cls.env["product.product"].create(
            {"name": "Consultation Fee Ins", "type": "service", "list_price": 100.0}
        )
        cls.appt_type = cls.env["hms.appointment.type"].create(
            {"name": "Ins Checkup", "default_duration": 0.5, "product_id": cls.product_fee.id}
        )

        start = datetime.now().replace(second=0, microsecond=0)
        cls.appointment = cls.env["calendar.event"].create(
            {
                "name": "Ins Appt",
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

    def _create_policy(self, coverage=80.0):
        today = date.today()
        return self.env["hms.insurance.policy"].create(
            {
                "name": "POL-001",
                "patient_id": self.patient.id,
                "insurance_company_id": self.insurer.id,
                "coverage_percentage": coverage,
                "valid_from": today - timedelta(days=30),
                "valid_until": today + timedelta(days=365),
            }
        )

    def test_get_active_policy(self):
        policy = self._create_policy()
        found = self.env["hms.insurance.policy"].get_active_policy(self.patient.id)
        self.assertEqual(found, policy)

    def test_no_policy_returns_false(self):
        found = self.env["hms.insurance.policy"].get_active_policy(self.patient.id)
        self.assertFalse(found)

    def test_expired_policy_not_found(self):
        today = date.today()
        self.env["hms.insurance.policy"].create(
            {
                "name": "POL-EXP",
                "patient_id": self.patient.id,
                "insurance_company_id": self.insurer.id,
                "coverage_percentage": 80.0,
                "valid_from": today - timedelta(days=365),
                "valid_until": today - timedelta(days=1),
            }
        )
        found = self.env["hms.insurance.policy"].get_active_policy(self.patient.id)
        self.assertFalse(found)

    def test_billing_without_policy_no_discount(self):
        """Without a policy, SO should have only the consultation fee line."""
        self.consultation.action_create_sale_order()
        so = self.consultation.sale_order_id
        self.assertEqual(len(so.order_line), 1)

    def test_billing_with_policy_adds_discount_line(self):
        """With an 80% policy, SO should have the fee + a negative discount line."""
        self._create_policy(coverage=80.0)
        self.consultation.action_create_sale_order()
        so = self.consultation.sale_order_id
        self.assertEqual(len(so.order_line), 2)
        discount_line = so.order_line.filtered(lambda line: line.price_unit < 0)
        self.assertTrue(discount_line)
        self.assertAlmostEqual(discount_line.price_unit, -80.0, places=2)

    def test_discount_not_applied_twice(self):
        """Calling _apply_insurance_discount again should not add a second line."""
        self._create_policy()
        self.consultation.action_create_sale_order()
        self.consultation._apply_insurance_discount()
        so = self.consultation.sale_order_id
        discount_lines = so.order_line.filtered(lambda line: line.price_unit < 0)
        self.assertEqual(len(discount_lines), 1)

    def test_partner_insurance_flag(self):
        self.assertTrue(self.insurer.is_insurance_company)
        self.assertFalse(self.patient.is_insurance_company)

    def test_seed_discount_product(self):
        product = self.env.ref("hms_insurance.product_insurance_discount", raise_if_not_found=False)
        self.assertTrue(product)
