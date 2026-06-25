from app.domain.validators import (
    normalize_italian_phone,
    sanitize_citizen_name,
    sanitize_contact,
    validate_citizen_name,
    validate_italian_phone,
)


class TestNameValidation:
    def test_valid_simple_name(self):
        valid, error = validate_citizen_name("Mario Rossi")
        assert valid is True
        assert error is None

    def test_valid_name_with_hyphen(self):
        valid, error = validate_citizen_name("Maria-Teresa Bianchi")
        assert valid is True

    def test_valid_name_with_apostrophe(self):
        valid, error = validate_citizen_name("Luigi d'Amico")
        assert valid is True

    def test_valid_name_italian_characters(self):
        valid, error = validate_citizen_name("Francesca Rossi")
        assert valid is True

    def test_empty_name_rejected(self):
        valid, error = validate_citizen_name("")
        assert valid is False
        assert "vuoto" in error.lower()

    def test_too_short_name_rejected(self):
        valid, error = validate_citizen_name("A")
        assert valid is False
        assert "breve" in error.lower()

    def test_too_long_name_rejected(self):
        long_name = "A" * 256
        valid, error = validate_citizen_name(long_name)
        assert valid is False
        assert "lungo" in error.lower()

    def test_name_with_numbers_rejected(self):
        valid, error = validate_citizen_name("Mario123 Rossi")
        assert valid is False
        assert "caratteri non validi" in error.lower()

    def test_name_with_special_chars_rejected(self):
        valid, error = validate_citizen_name("Mario@Rossi")
        assert valid is False

    def test_name_with_sql_injection_rejected(self):
        valid, error = validate_citizen_name("Mario'; DROP TABLE--")
        assert valid is False

    def test_whitespace_trimmed(self):
        valid, error = validate_citizen_name("  Mario Rossi  ")
        assert valid is True


class TestPhoneValidation:
    def test_valid_italian_mobile_with_zero(self):
        valid, error = validate_italian_phone("0912345678")
        assert valid is True
        assert error is None

    def test_valid_italian_mobile_with_plus39(self):
        valid, error = validate_italian_phone("+39 912345678")
        assert valid is True

    def test_valid_italian_mobile_with_0039(self):
        valid, error = validate_italian_phone("0039912345678")
        assert valid is True

    def test_phone_with_spaces_accepted(self):
        valid, error = validate_italian_phone("09 12 34 56 78")
        assert valid is True

    def test_phone_with_hyphens_accepted(self):
        valid, error = validate_italian_phone("09-12-34-56-78")
        assert valid is True

    def test_phone_with_parentheses_accepted(self):
        valid, error = validate_italian_phone("+39 (91) 234-5678")
        assert valid is True

    def test_empty_phone_rejected(self):
        valid, error = validate_italian_phone("")
        assert valid is False
        assert "vuoto" in error.lower()

    def test_too_short_phone_rejected(self):
        valid, error = validate_italian_phone("0912")
        assert valid is False
        assert "breve" in error.lower()

    def test_too_long_phone_rejected(self):
        valid, error = validate_italian_phone("+39 9" + "1" * 100)
        assert valid is False
        assert "lungo" in error.lower()

    def test_phone_with_letters_rejected(self):
        valid, error = validate_italian_phone("091ABC5678")
        assert valid is False
        assert "non validi" in error.lower()

    def test_non_italian_format_rejected(self):
        valid, error = validate_italian_phone("(123) 456-7890")  # US format
        assert valid is False

    def test_valid_plain_mobile_number(self):
        valid, error = validate_italian_phone("3312345678")  # Plain mobile (3XX XXXXXXX)
        assert valid is True
        assert error is None

    def test_valid_plain_mobile_with_spaces(self):
        valid, error = validate_italian_phone("33 1234 5678")
        assert valid is True

    def test_valid_plain_landline_number(self):
        valid, error = validate_italian_phone("0512345678")  # Plain landline (0XX XXXXXX)
        assert valid is True


class TestPhoneNormalization:
    def test_normalize_with_spaces(self):
        result = normalize_italian_phone("09 12 34 56 78")
        assert result == "+39912345678"

    def test_normalize_with_hyphens(self):
        result = normalize_italian_phone("09-12-34-56-78")
        assert result == "+39912345678"

    def test_normalize_with_plus39(self):
        result = normalize_italian_phone("+39 912345678")
        assert result == "+39912345678"

    def test_normalize_with_0039(self):
        result = normalize_italian_phone("0039 912345678")
        assert result == "+39912345678"

    def test_normalize_with_0(self):
        result = normalize_italian_phone("0912345678")
        assert result == "+39912345678"

    def test_normalize_idempotent(self):
        """Normalizing twice should give same result"""
        once = normalize_italian_phone("09 12 34 56 78")
        twice = normalize_italian_phone(once)
        assert once == twice

    def test_normalize_plain_mobile_number(self):
        result = normalize_italian_phone("3312345678")
        assert result == "+393312345678"

    def test_normalize_plain_mobile_with_spaces(self):
        result = normalize_italian_phone("33 1234 5678")
        assert result == "+393312345678"

    def test_normalize_plain_landline_number(self):
        result = normalize_italian_phone("0512345678")
        assert result == "+39512345678"


class TestSanitization:
    def test_sanitize_name_strips_whitespace(self):
        result = sanitize_citizen_name("  Mario Rossi  ")
        assert result == "Mario Rossi"

    def test_sanitize_name_normalizes_spaces(self):
        result = sanitize_citizen_name("Mario    Rossi")
        assert result == "Mario Rossi"

    def test_sanitize_contact_strips_whitespace(self):
        result = sanitize_contact("  09 12 34 56 78  ")
        assert result == "09 12 34 56 78"
