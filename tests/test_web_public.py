"""Tests for the public pages of the site (no login)."""

import pytest

pytestmark = pytest.mark.web


@pytest.mark.parametrize("url", ["/", "/veiculos", "/contactos", "/login", "/registo"])
def test_public_pages_open(client, url):
    assert client.get(url).status_code == 200


def test_unknown_page_returns_404(client):
    assert client.get("/this-page-does-not-exist").status_code == 404


@pytest.mark.parametrize("url", ["/reservas", "/veiculos/1/alugar", "/reservas/1/cancelar"])
def test_private_pages_redirect_to_login(client, url):
    response = client.get(url)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_remembers_the_requested_page(client):
    # Journey from the brief: someone who tries to rent without logging in is
    # sent to the login page and, after signing in, returns to that page
    response = client.get("/veiculos/1/alugar")
    assert response.headers["Location"] == "/login?proximo=/veiculos/1/alugar"


def test_list_only_shows_available_vehicles(client, no_vehicles, insert_vehicle):
    insert_vehicle(brand="Available", model="Current")
    insert_vehicle(brand="ServicePassed", model="X", days_until_next_service=-1)
    insert_vehicle(brand="LegalisationExpired", model="X", days_since_legalisation=366)
    html = client.get("/veiculos").get_data(as_text=True)
    assert "Available" in html
    assert "ServicePassed" not in html
    assert "LegalisationExpired" not in html


def test_legalisation_of_exactly_365_days_is_still_valid(client, no_vehicles, insert_vehicle):
    # Boundary of the rule "legalisation older than 1 year makes the vehicle unavailable"
    insert_vehicle(brand="AtTheLimit", model="X", days_since_legalisation=365)
    assert "AtTheLimit" in client.get("/veiculos").get_data(as_text=True)


def test_service_date_today_is_still_valid(client, no_vehicles, insert_vehicle):
    insert_vehicle(brand="ServiceToday", model="X", days_until_next_service=0)
    assert "ServiceToday" in client.get("/veiculos").get_data(as_text=True)


@pytest.fixture
def catalogue(client, no_vehicles, insert_vehicle):
    """Small, controlled catalogue to test the search and the filters."""
    insert_vehicle(brand="Alfa", model="Small1", category="Pequeno", daily_rate=20, seats=4)
    insert_vehicle(brand="Beta", model="Suv1", category="SUV", daily_rate=80,
                   transmission="Automático", seats=5)
    insert_vehicle(brand="Gama", model="Moto1", category="Médio", vehicle_type="Moto",
                   daily_rate=30, seats=2)
    insert_vehicle(brand="Delta", model="Van1", category="Grande", daily_rate=100, seats=7)
    return client


def get_list(catalogue, parameters=""):
    return catalogue.get("/veiculos" + parameters).get_data(as_text=True)


@pytest.mark.parametrize("parameters, should_appear, should_not_appear", [
    ("?pesquisa=alf", ["Alfa"], ["Beta", "Gama", "Delta"]),         # partial, case-insensitive
    ("?pesquisa=Suv1", ["Beta"], ["Alfa", "Gama", "Delta"]),        # search by model
    ("?categoria=SUV", ["Beta"], ["Alfa", "Gama", "Delta"]),
    ("?tipo_veiculo=Moto", ["Gama"], ["Alfa", "Beta", "Delta"]),
    ("?transmissao=Automático", ["Beta"], ["Alfa", "Gama", "Delta"]),
    ("?valor_min=30&valor_max=80", ["Beta", "Gama"], ["Alfa", "Delta"]),   # limits included
    ("?pessoas=1-4", ["Alfa", "Gama"], ["Beta", "Delta"]),
    ("?pessoas=5-6", ["Beta"], ["Alfa", "Gama", "Delta"]),
    ("?pessoas=7%2B", ["Delta"], ["Alfa", "Beta", "Gama"]),         # 7 seats fall in "7 or more"
    ("?categoria=SUV&tipo_veiculo=Moto", [], ["Alfa", "Beta", "Gama", "Delta"]),  # filters combine with AND
])
def test_search_and_filters(catalogue, parameters, should_appear, should_not_appear):
    html = get_list(catalogue, parameters)
    for brand in should_appear:
        assert brand in html
    for brand in should_not_appear:
        assert brand not in html


@pytest.mark.parametrize("parameters", [
    "?valor_min=abc", "?valor_max=", "?categoria=Inexistente", "?pessoas=99",
    "?pesquisa=%27%3B+DROP+TABLE+veiculos%3B--",
])
def test_invalid_filters_do_not_break_the_site(catalogue, parameters):
    assert catalogue.get("/veiculos" + parameters).status_code == 200


def test_list_is_sorted_from_cheapest_to_most_expensive(catalogue):
    html = get_list(catalogue)
    positions = [html.index(brand) for brand in ["Alfa", "Gama", "Beta", "Delta"]]
    assert positions == sorted(positions)
