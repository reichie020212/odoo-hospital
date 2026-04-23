from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsAdmission(TransactionCase):
    """Tests for hms.admission workflow, bed state management, and daily room charges."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Inpatient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Admit", "is_doctor": True})
        cls.product = cls.env["product.product"].create(
            {"name": "Standard Room", "type": "service", "list_price": 100.0}
        )
        cls.ward = cls.env["hms.ward"].create({"name": "Test Ward"})
        cls.bed = cls.env["hms.bed"].create(
            {"name": "T-01", "ward_id": cls.ward.id, "bed_type": "standard", "product_id": cls.product.id}
        )

    def _create_admission(self, **overrides):
        vals = {
            "patient_id": self.patient.id,
            "doctor_id": self.doctor.id,
            "bed_id": self.bed.id,
        }
        vals.update(overrides)
        return self.env["hms.admission"].create(vals)

    def test_sequence_assigned(self):
        adm = self._create_admission()
        self.assertTrue(adm.name.startswith("ADM/"))

    def test_default_state_draft(self):
        adm = self._create_admission()
        self.assertEqual(adm.state, "draft")

    def test_admit_marks_bed_occupied(self):
        adm = self._create_admission()
        adm.action_admit()
        self.assertEqual(adm.state, "admitted")
        self.assertEqual(self.bed.state, "occupied")

    def test_admit_creates_sale_order(self):
        adm = self._create_admission()
        adm.action_admit()
        self.assertTrue(adm.sale_order_id)
        self.assertEqual(adm.sale_order_id.partner_id, self.patient)

    def test_admit_occupied_bed_raises(self):
        adm1 = self._create_admission()
        adm1.action_admit()
        bed2_adm = self._create_admission()
        with self.assertRaises(UserError):
            bed2_adm.action_admit()

    def test_discharge_sets_bed_cleaning(self):
        adm = self._create_admission()
        adm.action_admit()
        adm.action_discharge()
        self.assertEqual(adm.state, "discharged")
        self.assertEqual(self.bed.state, "cleaning")
        self.assertTrue(adm.discharge_date)

    def test_cancel_frees_bed(self):
        adm = self._create_admission()
        adm.action_admit()
        adm.action_cancel()
        self.assertEqual(self.bed.state, "available")
        self.assertEqual(adm.state, "cancelled")

    def test_gender_restriction_blocks_wrong_gender(self):
        """Admitting a male patient to a female-only ward should raise."""
        female_ward = self.env["hms.ward"].create({"name": "Female Ward", "gender_restriction": "female"})
        bed_f = self.env["hms.bed"].create({"name": "F-01", "ward_id": female_ward.id, "product_id": self.product.id})
        male_patient = self.env["res.partner"].create({"name": "Male Patient", "is_patient": True, "gender": "male"})
        adm = self._create_admission(patient_id=male_patient.id, bed_id=bed_f.id)
        with self.assertRaises(UserError):
            adm.action_admit()

    def test_gender_restriction_allows_matching_gender(self):
        """Admitting a female patient to a female-only ward should succeed."""
        female_ward = self.env["hms.ward"].create({"name": "Female Ward 2", "gender_restriction": "female"})
        bed_f = self.env["hms.bed"].create({"name": "F-02", "ward_id": female_ward.id, "product_id": self.product.id})
        female_patient = self.env["res.partner"].create(
            {"name": "Female Patient", "is_patient": True, "gender": "female"}
        )
        adm = self._create_admission(patient_id=female_patient.id, bed_id=bed_f.id)
        adm.action_admit()
        self.assertEqual(adm.state, "admitted")

    def test_gender_restriction_mixed_allows_any(self):
        """Mixed wards should accept any gender."""
        adm = self._create_admission()
        adm.action_admit()
        self.assertEqual(adm.state, "admitted")

    def test_cron_daily_room_charges(self):
        adm = self._create_admission()
        adm.action_admit()
        self.env["hms.admission"]._cron_daily_room_charges()
        self.assertEqual(len(adm.sale_order_id.order_line), 1)
        self.assertEqual(adm.sale_order_id.order_line.product_id, self.product)

    def test_cron_idempotent(self):
        """Running the CRON twice on the same day should not create duplicate lines."""
        adm = self._create_admission()
        adm.action_admit()
        self.env["hms.admission"]._cron_daily_room_charges()
        self.env["hms.admission"]._cron_daily_room_charges()
        self.assertEqual(len(adm.sale_order_id.order_line), 1)

    def test_cron_skips_no_product(self):
        """Beds without a room-charge product should be silently skipped."""
        bed_no_prod = self.env["hms.bed"].create({"name": "T-NoProd", "ward_id": self.ward.id})
        adm = self._create_admission(bed_id=bed_no_prod.id)
        adm.action_admit()
        self.env["hms.admission"]._cron_daily_room_charges()
        self.assertEqual(len(adm.sale_order_id.order_line), 0)

    def test_ward_id_stored_from_bed(self):
        adm = self._create_admission()
        self.assertEqual(adm.ward_id, self.ward)

    def test_action_view_sale_order(self):
        adm = self._create_admission()
        adm.action_admit()
        action = adm.action_view_sale_order()
        self.assertEqual(action["res_id"], adm.sale_order_id.id)
