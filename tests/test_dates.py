"""Date tests: text conversion, day counting and the booking rules."""

from datetime import date, timedelta

import pytest

import reservas

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("text, expected_date", [
    ("25/12/2026", date(2026, 12, 25)),    # Portuguese format
    ("2026-12-25", date(2026, 12, 25)),    # internal format
    ("  01/01/2027  ", date(2027, 1, 1)),  # surrounding spaces are ignored
    ("29/02/2028", date(2028, 2, 29)),     # leap year
    ("29/02/2027", None),                  # 2027 is not a leap year
    ("31/04/2026", None),                  # April only has 30 days
    ("2026/12/25", None),                  # separator not accepted
    ("tomorrow", None),                    # text that is not a date
    ("", None),
    (None, None),
])
def test_text_to_date(text, expected_date):
    assert reservas.texto_para_data(text) == expected_date


@pytest.mark.parametrize("value, expected_text", [
    (date(2026, 10, 5), "05/10/2026"),
    ("2026-10-05", "05/10/2026"),
    ("2026-10-05 14:30:00", "05/10/2026"),  # the time is ignored
])
def test_format_date(value, expected_text):
    assert reservas.formatar_data(value) == expected_text


@pytest.mark.parametrize("start, end, expected_days", [
    (date(2026, 10, 1), date(2026, 10, 1), 1),   # same day counts as 1
    (date(2026, 10, 1), date(2026, 10, 3), 3),   # start and end both count
    (date(2026, 10, 30), date(2026, 11, 2), 4),  # crosses a month change
    (date(2026, 12, 31), date(2027, 1, 1), 2),   # crosses a year change
])
def test_count_days_includes_start_and_end(start, end, expected_days):
    assert reservas.contar_dias(start, end) == expected_days


def as_text(date_value):
    """Helper: date -> YYYY-MM-DD text, as used in the site's links."""
    return date_value.isoformat()


def test_valid_dates_give_no_errors(vehicle_for_dates):
    today = date.today()
    errors, start, end = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(today), as_text(today + timedelta(days=4)))
    assert errors == []
    assert (start, end) == (today, today + timedelta(days=4))


@pytest.mark.parametrize("start_text, end_text", [
    ("", ""),
    ("abc", "2026-12-01"),
    ("2026-12-01", "31/02/2027"),
])
def test_invalid_dates_give_a_single_error(vehicle_for_dates, start_text, end_text):
    errors, _, _ = reservas.validar_datas_reserva(vehicle_for_dates, start_text, end_text)
    assert len(errors) == 1
    assert "válidas" in errors[0]


def test_start_in_the_past_is_rejected(vehicle_for_dates):
    yesterday = date.today() - timedelta(days=1)
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(yesterday), as_text(date.today()))
    assert any("anterior a hoje" in error for error in errors)


def test_start_today_is_accepted(vehicle_for_dates):
    today = date.today()
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(today), as_text(today))
    assert errors == []


def test_end_before_start_is_rejected(vehicle_for_dates):
    today = date.today()
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(today + timedelta(days=5)), as_text(today + timedelta(days=2)))
    assert any("fim não pode ser anterior" in error for error in errors)


@pytest.mark.parametrize("days, should_accept", [
    (29, True),
    (30, True),    # boundary: 30 days is the maximum allowed
    (31, False),   # boundary + 1: rejected (special contract)
])
def test_30_day_limit(vehicle_for_dates, days, should_accept):
    today = date.today()
    end = today + timedelta(days=days - 1)  # days are counted with start and end included
    errors, _, _ = reservas.validar_datas_reserva(vehicle_for_dates, as_text(today), as_text(end))
    assert (errors == []) is should_accept
    if not should_accept:
        assert any("máximo de 30 dias" in error for error in errors)


def test_start_after_the_service_date_is_rejected(vehicle_for_dates):
    service_date = date.fromisoformat(vehicle_for_dates["data_proxima_revisao"])
    start = service_date + timedelta(days=1)
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(start), as_text(start + timedelta(days=2)))
    assert any("revisão agendada" in error for error in errors)


def test_start_on_the_service_date_is_accepted(vehicle_for_dates):
    # Boundary: a service date during the booking is accepted (the customer
    # is warned in the booking summary)
    service_date = date.fromisoformat(vehicle_for_dates["data_proxima_revisao"])
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(service_date), as_text(service_date + timedelta(days=2)))
    assert errors == []


def test_end_on_the_legalisation_expiry_day_is_accepted(vehicle_for_dates):
    # Boundary: the booking may end exactly on the last valid day
    expiry = reservas.validade_legalizacao(vehicle_for_dates)
    # Next service far in the future, so that only the legalisation rule applies
    vehicle = dict(vehicle_for_dates, data_proxima_revisao=as_text(expiry + timedelta(days=30)))
    start = expiry - timedelta(days=2)
    errors, _, _ = reservas.validar_datas_reserva(vehicle, as_text(start), as_text(expiry))
    assert errors == []


def test_end_after_legalisation_expiry_is_rejected(vehicle_for_dates):
    expiry = reservas.validade_legalizacao(vehicle_for_dates)
    start = expiry - timedelta(days=1)
    errors, _, _ = reservas.validar_datas_reserva(
        vehicle_for_dates, as_text(start), as_text(expiry + timedelta(days=1)))
    assert any("legalização" in error for error in errors)


def test_legalisation_is_valid_for_365_days(vehicle_for_dates):
    last_legalisation = date.fromisoformat(vehicle_for_dates["data_ultima_legalizacao"])
    assert reservas.validade_legalizacao(vehicle_for_dates) == last_legalisation + timedelta(days=365)
