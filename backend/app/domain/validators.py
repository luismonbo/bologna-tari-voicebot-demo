import re
from typing import Optional


def validate_citizen_name(name: str) -> tuple[bool, Optional[str]]:
    """
    Validate citizen name.

    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Nome non può essere vuoto"

    name = name.strip()

    # Length check: reasonable limits for names
    if len(name) < 2:
        return False, "Nome troppo breve (minimo 2 caratteri)"

    if len(name) > 255:
        return False, "Nome troppo lungo (massimo 255 caratteri)"

    # Allow letters, spaces, hyphens, apostrophes (common in Italian names)
    # Reject special characters that could be problematic
    if not re.match(r"^[a-zA-Zàáâäæèéêëìíîïðñòóôöœùúûüýÿçœ\s\-']+$", name):
        return False, "Nome contiene caratteri non validi"

    return True, None


def validate_italian_phone(phone: str) -> tuple[bool, Optional[str]]:
    """
    Validate Italian phone number.

    Accepts:
    - Mobile numbers: 3XX XXXXXXX (10 digits starting with 3)
    - Landline numbers: 0XX XXXXXX (10 digits starting with 0)
    - With country code: +39 or 0039 prefixes
    - Flexible formatting with spaces, hyphens, parentheses

    Returns: (is_valid, error_message)
    """
    if not phone:
        return False, "Numero di telefono non può essere vuoto"

    phone = phone.strip()

    if len(phone) < 10:
        return False, "Numero di telefono troppo breve"

    # Italian phone numbers max ~15 chars (+39 9XX XXXX XXX)
    if len(phone) > 20:
        return False, "Numero di telefono troppo lungo"

    # Remove spaces, hyphens, parentheses for validation
    normalized = re.sub(r"[\s\-()]+", "", phone)

    # Must contain only digits and + prefix
    if not re.match(r"^\+?[0-9]+$", normalized):
        return False, "Numero di telefono contiene caratteri non validi"

    # Italian patterns:
    # +39 followed by 9-10 digits (mobile/landline with country code)
    # 0039 followed by 9-10 digits
    # 3XX XXXXXXX (10 digits, mobile number)
    # 0XX XXXXXX (10 digits, landline)
    italian_pattern = r"^(\+39|0039|3)[0-9]{8,10}$|^0[0-9]{8,10}$"

    if re.match(italian_pattern, normalized):
        return True, None

    return False, "Numero di telefono non valido (formato italiano atteso)"


def sanitize_citizen_name(name: str) -> str:
    """Sanitize citizen name by stripping and normalizing whitespace."""
    return " ".join(name.strip().split())


def sanitize_contact(contact: str) -> str:
    """Sanitize contact by stripping whitespace."""
    return contact.strip()


def normalize_italian_phone(phone: str) -> str:
    """
    Normalize Italian phone number to consistent format: +39 XXX XXXXXX or +39 9XX XXXXXX

    Takes any valid Italian phone format and converts to +39 followed by digits with standard spacing.
    Handles numbers with or without country code prefix.
    """
    if not phone:
        return ""

    # Strip whitespace
    phone = phone.strip()

    # Remove spaces, hyphens, parentheses
    normalized = re.sub(r"[\s\-()]+", "", phone)

    # Remove + if present (will add it back)
    normalized = normalized.lstrip("+")

    # Handle country code prefixes
    if normalized.startswith("0039"):
        normalized = normalized[4:]  # Remove 0039
    elif normalized.startswith("39"):
        normalized = normalized[2:]  # Remove 39
    elif normalized.startswith("0"):
        normalized = normalized[1:]  # Remove leading 0
    # else: already in format 3XX... (mobile) or similar, keep as is

    # Add +39 prefix
    return f"+39{normalized}"
