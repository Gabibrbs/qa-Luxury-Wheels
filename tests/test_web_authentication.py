"""Tests for sign-up, login and logout."""

import pytest

from sql_helpers import query_sql

pytestmark = pytest.mark.web


def count_customers():
    return query_sql("SELECT COUNT(*) FROM clientes")[0][0]


def has_session(client):
    with client.session_transaction() as session:
        return "id_cliente" in session


def test_valid_sign_up_creates_a_customer_and_logs_in(client, registration_data):
    response = client.post("/registo", data=registration_data)
    assert response.status_code == 302
    assert count_customers() == 1
    assert has_session(client)


def test_password_is_never_stored_as_plain_text(client, registration_data):
    client.post("/registo", data=registration_data)
    stored_row = query_sql("SELECT * FROM clientes")[0]
    assert "Secure123" not in [str(value) for value in tuple(stored_row)]


@pytest.mark.parametrize("field, value", [
    ("utilizador", "ab"),
    ("email", "no-at-sign"),
    ("password", "short1"),
    ("nome", ""),
])
def test_sign_up_with_invalid_data_creates_no_customer(client, registration_data, field, value):
    registration_data[field] = value
    if field == "password":
        registration_data["confirmacao_password"] = value
    response = client.post("/registo", data=registration_data)
    assert response.status_code == 200      # back to the form, with errors
    assert count_customers() == 0
    assert not has_session(client)


def test_sign_up_with_repeated_username_is_rejected(client, registration_data):
    client.post("/registo", data=registration_data)
    client.get("/logout")
    second = dict(registration_data, email="other@example.com")
    client.post("/registo", data=second)
    assert count_customers() == 1


def test_sign_up_with_repeated_email_is_rejected(client, registration_data):
    client.post("/registo", data=registration_data)
    client.get("/logout")
    second = dict(registration_data, utilizador="other_user")
    client.post("/registo", data=second)
    assert count_customers() == 1


def test_login_with_correct_data(client, registration_data):
    client.post("/registo", data=registration_data)
    client.get("/logout")
    response = client.post(
        "/login", data={"utilizador": "test_user", "password": "Secure123", "proximo": ""})
    assert response.status_code == 302
    assert has_session(client)


@pytest.mark.parametrize("username, password", [
    ("test_user", "WrongPassword1"),
    ("does_not_exist", "Secure123"),
    ("", ""),
])
def test_login_with_wrong_data_does_not_start_a_session(client, registration_data, username, password):
    client.post("/registo", data=registration_data)
    client.get("/logout")
    client.post("/login", data={"utilizador": username, "password": password, "proximo": ""})
    assert not has_session(client)


def test_logout_ends_the_session(client, registration_data):
    client.post("/registo", data=registration_data)
    assert has_session(client)
    client.get("/logout")
    assert not has_session(client)


def test_private_page_opens_with_a_session(client, registration_data):
    client.post("/registo", data=registration_data)
    assert client.get("/reservas").status_code == 200


@pytest.mark.parametrize("destination", [
    "https://malicious-site.com", "//malicious-site.com", "javascript:alert(1)"])
def test_login_does_not_redirect_to_external_sites(client, registration_data, destination):
    # Security: the "proximo" parameter must not take the customer outside the site
    client.post("/registo", data=registration_data)
    client.get("/logout")
    response = client.post(
        "/login",
        data={"utilizador": "test_user", "password": "Secure123", "proximo": destination})
    assert "malicious-site" not in response.headers.get("Location", "")
    assert "javascript:" not in response.headers.get("Location", "")


def test_login_returns_to_the_requested_page(client, registration_data):
    client.post("/registo", data=registration_data)
    client.get("/logout")
    response = client.post(
        "/login",
        data={"utilizador": "test_user", "password": "Secure123", "proximo": "/reservas"})
    assert response.headers["Location"].endswith("/reservas")
