from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWardBed(TransactionCase):
    """Tests for hms.ward and hms.bed models."""

    def test_ward_bed_count(self):
        ward = self.env["hms.ward"].create({"name": "Count Ward"})
        self.env["hms.bed"].create({"name": "B1", "ward_id": ward.id})
        self.env["hms.bed"].create({"name": "B2", "ward_id": ward.id})
        ward.invalidate_recordset()
        self.assertEqual(ward.bed_count, 2)
        self.assertEqual(ward.available_count, 2)

    def test_ward_available_count_updates(self):
        ward = self.env["hms.ward"].create({"name": "Occ Ward"})
        bed = self.env["hms.bed"].create({"name": "B1", "ward_id": ward.id})
        self.env["hms.bed"].create({"name": "B2", "ward_id": ward.id})
        bed.state = "occupied"
        ward.invalidate_recordset()
        self.assertEqual(ward.available_count, 1)

    def test_bed_default_state(self):
        ward = self.env["hms.ward"].create({"name": "Def Ward"})
        bed = self.env["hms.bed"].create({"name": "B1", "ward_id": ward.id})
        self.assertEqual(bed.state, "available")

    def test_action_view_beds(self):
        ward = self.env["hms.ward"].create({"name": "Nav Ward"})
        self.env["hms.bed"].create({"name": "B1", "ward_id": ward.id})
        action = ward.action_view_beds()
        self.assertEqual(action["res_model"], "hms.bed")
        self.assertIn(("ward_id", "=", ward.id), action["domain"])

    def test_seed_data_loaded(self):
        ward = self.env.ref("hms_inpatient.ward_general", raise_if_not_found=False)
        self.assertTrue(ward)
        bed = self.env.ref("hms_inpatient.bed_g1", raise_if_not_found=False)
        self.assertTrue(bed)
        self.assertEqual(bed.ward_id, ward)
