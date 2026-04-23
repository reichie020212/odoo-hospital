from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHmsLabRequest(TransactionCase):
    """Tests for hms.lab.request workflow, panel expansion, and result generation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["res.partner"].create({"name": "Lab Patient", "is_patient": True})
        cls.doctor = cls.env["hr.employee"].create({"name": "Dr. Lab", "is_doctor": True})

        # Individual test
        cls.glucose = cls.env["hms.lab.test.type"].create(
            {"name": "Glucose", "code": "GLU", "unit": "mg/dL", "normal_range_min": 70, "normal_range_max": 100}
        )
        # Panel with children
        cls.cbc = cls.env["hms.lab.test.type"].create({"name": "CBC", "code": "CBC", "is_panel": True})
        cls.wbc = cls.env["hms.lab.test.type"].create(
            {
                "name": "WBC",
                "unit": "×10³/μL",
                "normal_range_min": 4.5,
                "normal_range_max": 11.0,
                "parent_id": cls.cbc.id,
            }
        )
        cls.rbc = cls.env["hms.lab.test.type"].create(
            {
                "name": "RBC",
                "unit": "×10⁶/μL",
                "normal_range_min": 4.5,
                "normal_range_max": 5.5,
                "parent_id": cls.cbc.id,
            }
        )

    def _create_request(self, **overrides):
        vals = {"patient_id": self.patient.id, "doctor_id": self.doctor.id}
        vals.update(overrides)
        return self.env["hms.lab.request"].create(vals)

    def test_sequence_assigned(self):
        req = self._create_request()
        self.assertTrue(req.name.startswith("LAB/"), f"Expected LAB/ prefix, got {req.name}")

    def test_default_state_draft(self):
        req = self._create_request()
        self.assertEqual(req.state, "draft")

    def test_state_full_lifecycle(self):
        req = self._create_request()
        req.action_collect()
        self.assertEqual(req.state, "collected")
        req.action_process()
        self.assertEqual(req.state, "processing")
        req.action_done()
        self.assertEqual(req.state, "done")

    def test_generate_results_individual(self):
        """Ordering an individual test creates one result line."""
        req = self._create_request(test_type_ids=[(6, 0, [self.glucose.id])])
        req.action_generate_results()
        self.assertEqual(len(req.result_ids), 1)
        self.assertEqual(req.result_ids.test_type_id, self.glucose)

    def test_generate_results_panel_expansion(self):
        """Ordering a panel creates one result line per child test."""
        req = self._create_request(test_type_ids=[(6, 0, [self.cbc.id])])
        req.action_generate_results()
        self.assertEqual(len(req.result_ids), 2)
        result_types = req.result_ids.mapped("test_type_id")
        self.assertIn(self.wbc, result_types)
        self.assertIn(self.rbc, result_types)

    def test_generate_results_mixed(self):
        """Ordering a panel + individual test creates correct total lines."""
        req = self._create_request(test_type_ids=[(6, 0, [self.cbc.id, self.glucose.id])])
        req.action_generate_results()
        self.assertEqual(len(req.result_ids), 3)

    def test_generate_results_no_duplicates(self):
        """Calling generate twice should not create duplicate result lines."""
        req = self._create_request(test_type_ids=[(6, 0, [self.glucose.id])])
        req.action_generate_results()
        req.action_generate_results()
        self.assertEqual(len(req.result_ids), 1)

    def test_generate_results_empty_raises(self):
        """Generating results without ordered tests should raise."""
        req = self._create_request()
        with self.assertRaises(UserError):
            req.action_generate_results()

    def test_abnormal_flag(self):
        """Result value outside normal range should be flagged abnormal."""
        req = self._create_request(test_type_ids=[(6, 0, [self.glucose.id])])
        req.action_generate_results()
        result = req.result_ids[0]
        result.value = 85  # within 70-100
        self.assertFalse(result.is_abnormal)
        result.value = 120  # above 100
        self.assertTrue(result.is_abnormal)
        result.value = 50  # below 70
        self.assertTrue(result.is_abnormal)

    def test_consultation_link(self):
        """Lab request created from consultation should link back."""
        consultation = self.env["hms.consultation"].create({"patient_id": self.patient.id, "doctor_id": self.doctor.id})
        action = consultation.action_create_lab_request()
        req = self.env["hms.lab.request"].browse(action["res_id"])
        self.assertEqual(req.consultation_id, consultation)
        self.assertEqual(req.patient_id, self.patient)
        consultation.invalidate_recordset()
        self.assertEqual(consultation.lab_request_count, 1)

    def test_cascade_delete(self):
        req = self._create_request(test_type_ids=[(6, 0, [self.glucose.id])])
        req.action_generate_results()
        result_id = req.result_ids[0].id
        req.unlink()
        self.assertFalse(self.env["hms.lab.result"].browse(result_id).exists())
