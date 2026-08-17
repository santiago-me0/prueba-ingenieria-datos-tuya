import unittest

from Ejercicio_1.src.validation import validate_phone


class TestValidatePhone(unittest.TestCase):

    def test_valid_mobile(self):
        result = validate_phone("+573001234567")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "mobile")
        self.assertEqual(result["status"], "VALID")
        self.assertIsNone(result["reason"])

    def test_valid_landline_bogota(self):
        result = validate_phone("+576013254585")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "landline")
        self.assertEqual(result["status"], "VALID")
        self.assertIsNone(result["reason"])

    def test_valid_landline_antioquia(self):
        result = validate_phone("+576043254585")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "landline")
        self.assertEqual(result["status"], "VALID")
        self.assertIsNone(result["reason"])

    def test_valid_landline_caribbean(self):
        result = validate_phone("+576055686525")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "landline")
        self.assertEqual(result["status"], "VALID")
        self.assertIsNone(result["reason"])

    def test_invalid_phone_prefix(self):
        result = validate_phone("+579043254585")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "INVALID")

    def test_invalid_phone_length(self):
        result = validate_phone("+57300123456")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "INVALID")

    def test_invalid_phone_without_country_code(self):
        result = validate_phone("3001234567")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "INVALID")

    def test_invalid_none(self):
        result = validate_phone(None)

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "INVALID")

    def test_suspicious_repeated_digits(self):
        result = validate_phone("+573333333333")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "mobile")
        self.assertEqual(result["status"], "SUSPICIOUS")
        self.assertEqual(result["reason"], "REPEATED_DIGITS")

    def test_suspicious_zero_digits(self):
        result = validate_phone("+573000000000")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "mobile")
        self.assertEqual(result["status"], "SUSPICIOUS")
        self.assertEqual(result["reason"], "REPEATED_DIGITS")

    def test_suspicious_repeated_digits_after_mobile_prefix(self):
        result = validate_phone("+573111111111")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "mobile")
        self.assertEqual(result["status"], "SUSPICIOUS")
        self.assertEqual(result["reason"], "REPEATED_DIGITS")

    def test_suspicious_zero_pattern(self):
        result = validate_phone("+573000000000")

        self.assertTrue(result["is_valid"])
        self.assertEqual(result["phone_type"], "mobile")
        self.assertEqual(result["status"], "SUSPICIOUS")
        self.assertEqual(result["reason"], "REPEATED_DIGITS")

    def test_invalid_landline_local_prefix(self):
        result = validate_phone("+576011254585")

        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(
            result["reason"],
            "INVALID_LANDLINE_LOCAL_PREFIX"
    )


if __name__ == "__main__":
    unittest.main()