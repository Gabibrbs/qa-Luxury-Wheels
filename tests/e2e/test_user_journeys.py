"""
Browser tests: the main journeys of a customer, from the first click to the
last. They complement the faster tests in the other files, which check the
rules one by one.

Locators prefer what a person sees (button and link names, labels). Form
fields use their `id`, because the site's placeholders are long and the fields
have no visible labels. There are no fixed waits: `expect(...)` retries until
the page shows the expected result or the time runs out.

Note: the site is written in Portuguese (a course requirement), so the texts
searched for on the page are in Portuguese.
"""

import re
from datetime import date, timedelta

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e

CARD_NUMBER = "4111111111111111"  # 16 digits; payment is simulated
CARD_HOLDER = "Maria Teste"
SECURITY_CODE = "123"


def as_site_date(days_from_today):
    """A date relative to today, written the way the site shows it (DD/MM/YYYY)."""
    return (date.today() + timedelta(days=days_from_today)).strftime("%d/%m/%Y")


def choose_option(page: Page, field_id, option_text):
    """
    Picks an option in one of the site's drop-down lists. The theme replaces
    each <select> with its own styled list (nice-select), so, like a customer,
    the test opens that list and clicks the option instead of using the hidden
    <select>.
    """
    page.locator(f"#{field_id} + .nice-select").click()
    page.locator(f"#{field_id} + .nice-select li.option", has_text=option_text).click()


def log_in(page: Page, user):
    page.goto("/login")
    page.locator("#utilizador").fill(user["username"])
    page.locator("#password").fill(user["password"])
    page.get_by_role("button", name="iniciar sessão").click()
    expect(page.get_by_role("link", name=re.compile("Terminar sessão"))).to_be_visible()


def book_cheapest_vehicle(page: Page, start_in_days=5, duration_days=3):
    """
    Books the first vehicle of the list (the cheapest) and pays with a new
    card. Returns its daily price, the number of days and the booking number.
    """
    page.goto("/veiculos")
    first_card = page.locator(".car-item").first
    daily_price = float(first_card.locator(".price").inner_text().split()[0])
    first_card.get_by_role("link", name="Efetuar aluguer").click()

    page.locator("#data_inicio").fill(as_site_date(start_in_days))
    page.locator("#data_fim").fill(as_site_date(start_in_days + duration_days - 1))
    page.get_by_role("button", name="continuar para o pagamento").click()

    page.get_by_label("Usar um cartão novo").check()
    page.locator("#numero_cartao").fill(CARD_NUMBER)
    page.locator("#nome_titular").fill(CARD_HOLDER)
    page.locator("#codigo_seguranca").fill(SECURITY_CODE)
    page.get_by_role("button", name=re.compile("concluir pagamento")).click()

    confirmation = page.get_by_role("heading", name=re.compile("está confirmada"))
    expect(confirmation).to_be_visible()
    booking_number = re.search(r"n\.º (\d+)", confirmation.inner_text()).group(1)
    return daily_price, duration_days, booking_number


def test_customer_registers_logs_out_and_logs_in_again(page: Page):
    page.goto("/registo")
    page.locator("#nome").fill("Joana Silva")
    page.locator("#utilizador").fill("joana_silva")
    page.locator("#email").fill("joana@example.com")
    page.locator("#password").fill("Secure123")
    page.locator("#confirmacao_password").fill("Secure123")
    page.get_by_role("button", name="criar nova conta").click()

    # The account is created and the customer is already logged in
    expect(page.locator(".mensagens-feedback")).to_contain_text("Conta criada com sucesso")
    page.get_by_role("link", name=re.compile("Terminar sessão")).click()
    expect(page.get_by_role("link", name="Iniciar sessão")).to_be_visible()

    # The same credentials work on the login page
    page.get_by_role("link", name="Iniciar sessão").click()
    page.locator("#utilizador").fill("joana_silva")
    page.locator("#password").fill("Secure123")
    page.get_by_role("button", name="iniciar sessão").click()
    expect(page.locator(".mensagens-feedback")).to_contain_text("Olá, Joana Silva")


def test_search_filters_the_vehicle_list(page: Page):
    page.goto("/veiculos")
    total_vehicles = page.locator(".car-item").count()

    # Filter by type: every vehicle shown is a motorbike
    choose_option(page, "tipo_veiculo", "Moto")
    page.get_by_role("button", name="pesquisar").click()
    cards = page.locator(".car-item")
    expect(cards).not_to_have_count(total_vehicles)
    assert cards.count() > 0
    for position in range(cards.count()):
        expect(cards.nth(position).locator(".details-list li").first).to_contain_text("Moto")

    # A search with no matches shows a message instead of an empty page
    page.goto("/veiculos")
    page.locator("#pesquisa").fill("zzzz")
    page.get_by_role("button", name="pesquisar").click()
    expect(page.get_by_text("Não foi encontrado nenhum veículo")).to_be_visible()

    # "Clear filters" brings every vehicle back
    page.get_by_role("link", name="limpar filtros").click()
    expect(page.locator(".car-item")).to_have_count(total_vehicles)


def test_visitor_is_sent_to_login_and_back_to_the_chosen_vehicle(page: Page, existing_user):
    page.goto("/veiculos")
    page.locator(".car-item").first.get_by_role("link", name="Efetuar aluguer").click()

    # Not logged in: the site asks for the login first...
    expect(page).to_have_url(re.compile(r"/login\?proximo="))
    page.locator("#utilizador").fill(existing_user["username"])
    page.locator("#password").fill(existing_user["password"])
    page.get_by_role("button", name="iniciar sessão").click()

    # ...and then returns to the booking page of the same vehicle
    expect(page).to_have_url(re.compile(r"/veiculos/\d+/alugar"))
    expect(page.get_by_role("heading", name="Levantamento")).to_be_visible()


def test_customer_books_a_vehicle_and_sees_the_booking(page: Page, existing_user):
    log_in(page, existing_user)
    daily_price, days, booking_number = book_cheapest_vehicle(page)

    page.get_by_role("link", name="Ver as minhas reservas").click()
    booking = page.locator(".reserva-cartao").filter(has_text=f"Reserva n.º {booking_number}")
    expect(booking).to_contain_text("Futura")
    expect(booking).to_contain_text(f"{daily_price * days:.2f} €")


def test_payment_page_shows_the_total_before_paying(page: Page, existing_user):
    log_in(page, existing_user)
    page.goto("/veiculos")
    first_card = page.locator(".car-item").first
    daily_price = float(first_card.locator(".price").inner_text().split()[0])
    first_card.get_by_role("link", name="Efetuar aluguer").click()

    page.locator("#data_inicio").fill(as_site_date(5))
    page.locator("#data_fim").fill(as_site_date(8))  # 4 days: both ends count
    page.get_by_role("button", name="continuar para o pagamento").click()

    summary = page.locator("table.table")
    expect(summary.locator("tr", has_text="Número de dias")).to_contain_text("4")
    expect(summary.locator("tr", has_text="Valor total")).to_contain_text(f"{daily_price * 4:.2f} €")


def test_customer_cancels_a_booking_and_is_refunded(page: Page, existing_user):
    log_in(page, existing_user)
    daily_price, days, booking_number = book_cheapest_vehicle(page)

    page.get_by_role("link", name="Ver as minhas reservas").click()
    page.get_by_role("link", name="Cancelar reserva").click()
    expect(page.get_by_role("heading", name=re.compile("Tem a certeza"))).to_be_visible()
    page.get_by_role("button", name="sim, cancelar a reserva").click()

    expect(page.locator(".mensagens-feedback")).to_contain_text(f"reserva n.º {booking_number} foi cancelada")
    booking = page.locator(".reserva-cartao").filter(has_text=f"Reserva n.º {booking_number}")
    expect(booking).to_contain_text("Cancelada")
    expect(booking).to_contain_text("(reembolsado)")
    # A cancelled booking can no longer be changed or cancelled
    expect(booking.get_by_role("link", name="Cancelar reserva")).to_have_count(0)
