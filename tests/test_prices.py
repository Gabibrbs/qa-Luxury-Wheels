"""Booking summary tests: days, daily rates, extras, total, km and service warning."""

from datetime import date

import pytest

import reservas

pytestmark = pytest.mark.unit

VEHICLE = {"valor_diaria": 50.0, "data_proxima_revisao": "2030-01-01"}
INSURANCE = {"nome": "Insurance", "preco": 10.0, "tipo_preco": "por_dia"}   # per day
CHILD_SEAT = {"nome": "Child seat", "preco": 15.0, "tipo_preco": "fixo"}    # one-off


def test_summary_without_extras():
    summary = reservas.calcular_resumo_reserva(VEHICLE, date(2026, 10, 1), date(2026, 10, 3))
    assert summary["numero_dias"] == 3
    assert summary["valor_diarias"] == 150.0
    assert summary["valor_extras"] == 0
    assert summary["valor_total"] == 150.0
    assert summary["linhas_extras"] == []


def test_per_day_extra_is_multiplied_by_the_number_of_days():
    summary = reservas.calcular_resumo_reserva(
        VEHICLE, date(2026, 10, 1), date(2026, 10, 3), extras=[INSURANCE])
    assert summary["valor_extras"] == 30.0
    assert summary["valor_total"] == 180.0


def test_fixed_extra_is_paid_only_once():
    summary = reservas.calcular_resumo_reserva(
        VEHICLE, date(2026, 10, 1), date(2026, 10, 10), extras=[CHILD_SEAT])
    assert summary["valor_extras"] == 15.0
    assert summary["valor_total"] == 50.0 * 10 + 15.0


def test_several_extras_are_added_up():
    summary = reservas.calcular_resumo_reserva(
        VEHICLE, date(2026, 10, 1), date(2026, 10, 2), extras=[INSURANCE, CHILD_SEAT])
    assert summary["valor_total"] == 100.0 + 20.0 + 15.0
    assert [line["nome"] for line in summary["linhas_extras"]] == ["Insurance", "Child seat"]


def test_amounts_with_cents_are_rounded_to_two_decimals():
    vehicle = {"valor_diaria": 33.33, "data_proxima_revisao": "2030-01-01"}
    summary = reservas.calcular_resumo_reserva(vehicle, date(2026, 10, 1), date(2026, 10, 3))
    assert summary["valor_diarias"] == 99.99


@pytest.mark.parametrize("days, expected_km", [(1, 200), (3, 600), (30, 6000)])
def test_included_km_are_200_per_day(days, expected_km):
    summary = reservas.calcular_resumo_reserva(VEHICLE, date(2026, 10, 1), date(2026, 10, days))
    assert summary["km_incluidos"] == expected_km


@pytest.mark.parametrize("service_date, during_booking", [
    ("2026-10-01", True),    # on the first day of the booking
    ("2026-10-03", True),    # on the last day of the booking
    ("2026-10-02", True),    # in the middle
    ("2026-09-30", False),   # one day before
    ("2026-10-04", False),   # one day after
])
def test_service_warning_during_the_booking(service_date, during_booking):
    vehicle = {"valor_diaria": 50.0, "data_proxima_revisao": service_date}
    summary = reservas.calcular_resumo_reserva(vehicle, date(2026, 10, 1), date(2026, 10, 3))
    assert summary["revisao_durante_aluguer"] is during_booking
