from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLabBilling(TransactionCase):
    """Tests for the lab-request → sale.order billing bridge."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Lab Bill Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. LabBill", "is_doctor": True})
        cls.product_glucose = cls.env["product.product"].create(
            {"name": "Glucose Test Fee", "type": "service", "list_price": 25.0}
        )
        cls.glucose = cls.env["hms.lab.test.type"].create(
            {"name": "Glucose Bill", "unit": "mg/dL", "product_id": cls.product_glucose.id}
        )
        cls.no_product_test = cls.env["hms.lab.test.type"].create({"name": "Free Test", "unit": "U"})

    def _create_request(self, test_types):
        return self.env["hms.lab.request"].create(
            {
                "patient_id": self.patient.id,
                "doctor_id": self.doctor.id,
                "test_type_ids": [(6, 0, test_types.ids)],
            }
        )

    def test_bill_creates_sale_order(self):
        req = self._create_request(self.glucose)
        req.action_generate_results()
        req.action_collect()
        req.action_process()
        req.action_done()
        req.action_create_lab_bill()
        self.assertTrue(req.sale_order_id)
        self.assertEqual(req.sale_order_id.partner_id, self.patient)
        self.assertEqual(len(req.sale_order_id.order_line), 1)
        self.assertEqual(req.sale_order_id.order_line.product_id, self.product_glucose)

    def test_billing_state_updates(self):
        req = self._create_request(self.glucose)
        self.assertEqual(req.billing_state, "not_billed")
        req.action_collect()
        req.action_process()
        req.action_done()
        req.action_create_lab_bill()
        self.assertEqual(req.billing_state, "billed")

    def test_double_billing_raises(self):
        req = self._create_request(self.glucose)
        req.action_collect()
        req.action_process()
        req.action_done()
        req.action_create_lab_bill()
        with self.assertRaises(UserError):
            req.action_create_lab_bill()

    def test_no_billable_tests_raises(self):
        req = self._create_request(self.no_product_test)
        req.action_collect()
        req.action_process()
        req.action_done()
        with self.assertRaises(UserError):
            req.action_create_lab_bill()
