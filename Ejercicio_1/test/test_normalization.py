import unittest

from Ejercicio_1.src.normalization import normalize_phone


class TestNormalizePhone(unittest.TestCase):

    def test_mobile_without_formatting(self):
        self.assertEqual(
            normalize_phone("3001234567"),
            "+573001234567"
        )

    def test_mobile_with_hyphens(self):
        self.assertEqual(
            normalize_phone("300-123-4567"),
            "+573001234567"
        )

    def test_mobile_with_spaces(self):
        self.assertEqual(
            normalize_phone("300 123 4567"),
            "+573001234567"
        )

    def test_mobile_with_country_code(self):
        self.assertEqual(
            normalize_phone("+57 300 123 4567"),
            "+573001234567"
        )

    def test_mobile_with_country_code_without_plus(self):
        self.assertEqual(
            normalize_phone("573001234567"),
            "+573001234567"
        )

    def test_landline_without_formatting(self):
        self.assertEqual(
            normalize_phone("6013254585"),
            "+576013254585"
        )

    def test_landline_with_formatting(self):
        self.assertEqual(
            normalize_phone("(604) 325-4585"),
            "+576043254585"
        )

    def test_landline_with_country_code(self):
        self.assertEqual(
            normalize_phone("+57 604 325 4585"),
            "+576043254585"
        )

    def test_mobile_with_spaces_grouped(self):
        self.assertEqual(
            normalize_phone("300 526 36 54"),
            "+573005263654"
        )

    def test_landline_with_spaces_grouped(self):
        self.assertEqual(
            normalize_phone("605 568 65 25"),
            "+576055686525"
        )

    def test_mobile_with_country_code_and_grouped_spaces(self):
        self.assertEqual(
            normalize_phone("+57 300 526 36 54"),
            "+573005263654"
        )

    def test_landline_with_country_code_and_grouped_spaces(self):
        self.assertEqual(
            normalize_phone("+57 605 568 65 25"),
            "+576055686525"
        )

    def test_invalid_short_number(self):
        self.assertIsNone(
            normalize_phone("8999655")
        )

    def test_invalid_text(self):
        self.assertIsNone(
            normalize_phone("telefono")
        )

    def test_invalid_plus_position(self):
        self.assertIsNone(
            normalize_phone("311+359+45+66")
        )

    def test_empty_phone(self):
        self.assertIsNone(
            normalize_phone("")
        )

    def test_none_phone(self):
        self.assertIsNone(
            normalize_phone(None)
        )

    def test_landline_with_country_code_without_plus(self):
        self.assertEqual(
            normalize_phone("576043254585"),
            "+576043254585"
    )

    def test_mobile_with_parentheses(self):
        self.assertEqual(
            normalize_phone("(300) 526-3654"),
            "+573005263654"
        )

    def test_invalid_dots_format(self):
        self.assertIsNone(
            normalize_phone("311.256.32.63")
    )
        
if __name__ == "__main__":
    unittest.main()