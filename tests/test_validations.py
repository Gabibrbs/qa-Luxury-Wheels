"""Form validation tests: username, e-mail, password and card."""

import pytest

import autenticacao
import reservas

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("username, is_valid", [
    ("abc", True),                 # minimum: 3 characters
    ("ab", False),                 # below the minimum
    ("a" * 20, True),              # maximum: 20 characters
    ("a" * 21, False),             # above the maximum
    ("john.smith_1", True),        # dot and underscore allowed
    ("john smith", False),         # spaces not allowed
    ("joão", True),                # accented letters count as letters
    ("ana!", False),               # symbol not allowed
    ("ana-test", False),           # hyphen not allowed (only "_" and ".")
    ("", False),
])
def test_valid_username(username, is_valid):
    assert autenticacao.utilizador_valido(username) is is_valid


@pytest.mark.parametrize("email, is_valid", [
    ("ana@example.com", True),
    ("a@b.c", True),
    ("ana@example", False),        # no dot in the domain
    ("anaexample.com", False),     # no @
    ("ana@@example.com", False),   # two @
    ("@example.com", False),       # nothing before the @
    ("ana@.com", False),           # domain starts with a dot
    ("ana@example.", False),       # domain ends with a dot
    ("ana @example.com", False),   # space
    ("", False),
])
def test_valid_email(email, is_valid):
    assert autenticacao.email_valido(email) is is_valid


def test_valid_password_gives_no_errors():
    assert autenticacao.validar_password("Secure123", "Secure123") == []


@pytest.mark.parametrize("password, confirmation, error_text", [
    ("Ab1", "Ab1", "pelo menos 8"),                # too short
    ("Abcdefg1", "Abcdefg1", None),                # exactly 8: valid (boundary)
    ("12345678", "12345678", "uma letra"),         # no letters
    ("abcdefgh", "abcdefgh", "um número"),         # no digits
    ("Secure123", "Secure124", "não coincidem"),   # different confirmation
])
def test_validate_password(password, confirmation, error_text):
    errors = autenticacao.validar_password(password, confirmation)
    if error_text is None:
        assert errors == []
    else:
        assert any(error_text in error for error in errors)


@pytest.mark.parametrize("number, name, cvv, expected_errors", [
    ("1234567812345678", "Ana Test", "123", 0),
    ("1234 5678 1234 5678", "Ana Test", "123", 0),    # spaces accepted
    ("123456781234567", "Ana Test", "123", 1),        # 15 digits
    ("12345678123456789", "Ana Test", "123", 1),      # 17 digits
    ("1234567812345abc", "Ana Test", "123", 1),       # letters in the number
    ("1234567812345678", "Ab", "123", 1),             # name too short
    ("1234567812345678", "Ana 123", "123", 1),        # name with digits
    ("1234567812345678", "Ana Test", "12", 1),        # CVV too short
    ("1234567812345678", "Ana Test", "1234", 1),      # CVV too long
    ("", "", "", 3),                                  # everything empty: 3 errors
])
def test_validate_card(number, name, cvv, expected_errors):
    assert len(reservas.validar_cartao(number, name, cvv)) == expected_errors
