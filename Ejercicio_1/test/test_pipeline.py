import csv
import tempfile
import unittest
from pathlib import Path

from Ejercicio_1.src.pipeline import process_dataset


class TestPhonePipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.exercise_dir = Path(__file__).resolve().parents[1]
        cls.input_file = cls.exercise_dir / "data" / "clients.csv"

    def _run_pipeline(self):
        """
        Execute the pipeline using a temporary output file
        and return the processed rows.
        """
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        output_file = Path(temp_dir.name) / "processed_clientes.csv"

        process_dataset(
            str(self.input_file),
            str(output_file),
        )

        with open(
            output_file,
            mode="r",
            encoding="utf-8",
            newline="",
        ) as file:
            return list(csv.DictReader(file))

    def test_pipeline_preserves_number_of_records(self):
        rows = self._run_pipeline()

        self.assertEqual(len(rows), 33)

    def test_output_contains_expected_columns(self):
        rows = self._run_pipeline()

        expected_columns = {
            "customer_id",
            "original_phone",
            "normalized_phone",
            "phone_type",
            "status",
            "validation_reason",
            "duplicate_group",
        }

        self.assertEqual(
            set(rows[0].keys()),
            expected_columns,
        )

    def test_original_phone_is_preserved(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        self.assertEqual(
            rows_by_id["002"]["original_phone"],
            "300-123-4567",
        )

        self.assertEqual(
            rows_by_id["026"]["original_phone"],
            "300 526 36 54",
        )

        self.assertEqual(
            rows_by_id["020"]["original_phone"],
            "311.256.32.63",
        )

    def test_equivalent_mobile_formats_are_normalized_equally(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        customer_ids = [
            "001",
            "002",
            "003",
            "004",
            "005",
            "006",
        ]

        normalized_values = {
            rows_by_id[customer_id]["normalized_phone"]
            for customer_id in customer_ids
        }

        self.assertEqual(
            normalized_values,
            {"+573001234567"},
        )

    def test_equivalent_landline_formats_are_normalized_equally(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        customer_ids = [
            "009",
            "014",
            "015",
        ]

        normalized_values = {
            rows_by_id[customer_id]["normalized_phone"]
            for customer_id in customer_ids
        }

        self.assertEqual(
            normalized_values,
            {"+576043254585"},
        )

    def test_invalid_records_are_registered(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        invalid_ids = [
            "016",
            "017",
            "018",
            "019",
            "020",
            "021",
            "025",
        ]

        for customer_id in invalid_ids:
            self.assertEqual(
                rows_by_id[customer_id]["status"],
                "INVALID",
            )

    def test_invalid_dot_format_is_not_normalized(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        result = rows_by_id["020"]

        self.assertEqual(
            result["original_phone"],
            "311.256.32.63",
        )
        self.assertEqual(
            result["normalized_phone"],
            "",
        )
        self.assertEqual(
            result["status"],
            "INVALID",
        )
        self.assertEqual(
            result["validation_reason"],
            "NORMALIZATION_FAILED",
        )

    def test_missing_phone_is_registered(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        result = rows_by_id["025"]

        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(
            result["validation_reason"],
            "MISSING_VALUE",
        )

    def test_suspicious_patterns_are_registered(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        suspicious_ids = [
            "022",
            "023",
            "024",
        ]

        for customer_id in suspicious_ids:
            result = rows_by_id[customer_id]

            self.assertEqual(
                result["status"],
                "SUSPICIOUS",
            )
            self.assertEqual(
                result["validation_reason"],
                "REPEATED_DIGITS",
            )
            self.assertEqual(
                result["phone_type"],
                "mobile",
            )

    def test_pipeline_status_counts(self):
        rows = self._run_pipeline()

        valid_count = sum(
            row["status"] == "VALID"
            for row in rows
        )

        invalid_count = sum(
            row["status"] == "INVALID"
            for row in rows
        )

        suspicious_count = sum(
            row["status"] == "SUSPICIOUS"
            for row in rows
        )

        self.assertEqual(valid_count, 23)
        self.assertEqual(invalid_count, 7)
        self.assertEqual(suspicious_count, 3)

    def test_pipeline_detects_four_duplicate_groups(self):
        rows = self._run_pipeline()

        duplicate_groups = {
            row["duplicate_group"]
            for row in rows
            if row["duplicate_group"]
        }

        self.assertEqual(
            len(duplicate_groups),
            4,
        )

    def test_equivalent_phones_share_duplicate_group(self):
        rows = self._run_pipeline()
        rows_by_id = {
            row["customer_id"]: row
            for row in rows
        }

        groups = [
            ["001", "002", "003", "004", "005", "006"],
            ["009", "014", "015"],
            ["026", "028", "030", "032"],
            ["027", "029", "031", "033"],
        ]

        for customer_ids in groups:
            duplicate_groups = {
                rows_by_id[customer_id]["duplicate_group"]
                for customer_id in customer_ids
            }

            self.assertEqual(
                len(duplicate_groups),
                1,
            )

            self.assertNotEqual(
                next(iter(duplicate_groups)),
                "",
            )


if __name__ == "__main__":
    unittest.main()