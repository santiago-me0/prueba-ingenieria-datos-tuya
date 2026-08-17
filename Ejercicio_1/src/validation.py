"""
Validation utilities for phone numbers.
"""

import re


LANDLINE_PREFIXES = {
    "601",
    "602",
    "604",
    "605",
    "606",
    "607",
    "608",
}


def validate_phone(phone: str | None) -> dict:
    """
    Validate a normalized phone number.

    Args:
        phone: Phone number in canonical format (+57XXXXXXXXXX).

    Returns:
        Dictionary containing validation status, phone type and reason.
    """

    result = {
        "is_valid": False,
        "phone_type": None,
        "status": "INVALID",
        "reason": None,
    }

    # Missing value
    if phone is None:
        result["reason"] = "MISSING_VALUE"
        return result

    # A validated phone must be a string
    if not isinstance(phone, str):
        result["reason"] = "INVALID_TYPE"
        return result

    # The validation stage expects canonical Colombian format
    if not re.fullmatch(r"\+57\d{10}", phone):
        result["reason"] = "INVALID_FORMAT"
        return result

    national_number = phone[3:]

    # Mobile phone
    if national_number.startswith("3"):
        result["is_valid"] = True
        result["phone_type"] = "mobile"

        if _has_suspicious_pattern(national_number):
            result["status"] = "SUSPICIOUS"
            result["reason"] = "REPEATED_DIGITS"
        else:
            result["status"] = "VALID"

        return result

    landline_prefix = national_number[:3]
    local_number = national_number[3:]

    if landline_prefix in LANDLINE_PREFIXES:
        if local_number[0] not in "2345678":
            result["reason"] = "INVALID_LANDLINE_LOCAL_PREFIX"
            return result

        result["is_valid"] = True
        result["phone_type"] = "landline"
        result["status"] = "VALID"
        return result

    # Unknown Colombian prefix
    result["reason"] = "INVALID_PREFIX"

    return result


def _has_suspicious_pattern(phone: str) -> bool:
    """
    Detect suspicious repetitive patterns in mobile numbers.
    """

    # All digits are the same, e.g. 3333333333
    if len(set(phone)) == 1:
        return True

    # Mobile prefix followed by the same digit repeatedly,
    # e.g. 3111111111 or 3000000000
    if phone[0] == "3" and len(set(phone[1:])) == 1:
        return True

    return False