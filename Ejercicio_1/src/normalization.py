"""
Utilities for normalizing phone numbers.
"""

import re


def normalize_phone(phone: str | None) -> str | None:
    """
    Normalize a phone number to the canonical format +57XXXXXXXXXX.

    Args:
        phone: Original phone number.

    Returns:
        Normalized phone number or None when the value cannot be normalized.
    """

    # 1. Handle missing values
    if phone is None:
        return None

    # 2. Ensure the value is a string
    if not isinstance(phone, str):
        return None

    # 3. Remove leading and trailing whitespace
    phone = phone.strip()

    if not phone:
        return None

    # 4. Validate allowed characters
    if not re.fullmatch(r"[0-9+\-()\s]+", phone):
        return None
    
    # 5. The plus sign can only appear at the beginning
    if "+" in phone and not phone.startswith("+"):
        return None

    # 6. If '+' exists, it must represent the Colombian country code
    if phone.startswith("+"):
        phone_without_plus = phone[1:].lstrip()

        if not phone_without_plus.startswith("57"):
            return None

    # 7. Remove formatting characters
    digits = re.sub(r"[\s\-()]", "", phone)

    # 8. Remove '+' after validating its position
    if digits.startswith("+"):
        digits = digits[1:]

    # 9. Handle international format: 57 + 10 national digits
    if len(digits) == 12 and digits.startswith("57"):
        digits = digits[2:]

    # 10. Validate Colombian national number length
    if not re.fullmatch(r"\d{10}", digits):
        return None

    # 11. Return canonical format
    return f"+57{digits}"