"""
Shared test configuration (pytest reads this file automatically).

These tests check the Luxury Wheels project, which lives in a separate
repository (github.com/Gabibrbs/luxury-wheels). By default the project is
looked up in a "luxury-wheels" folder next to this repository; to use another
folder, set the LUXURY_WHEELS_PATH environment variable.

Note: the application under test is written in Portuguese (a course
requirement), so the names of its modules, functions, form fields and
database columns appear below exactly as they are in the project.
"""

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

TESTS_FOLDER = Path(__file__).resolve().parent
PROJECT_PATH = Path(
    os.environ.get("LUXURY_WHEELS_PATH", TESTS_FOLDER.parent.parent / "luxury-wheels")
)

if not (PROJECT_PATH / "app.py").exists():
    raise RuntimeError(
        f"Could not find the Luxury Wheels project in {PROJECT_PATH}. "
        "Clone it into a 'luxury-wheels' folder next to this repository "
        "or set LUXURY_WHEELS_PATH."
    )

# Make the project's modules (app, database, reservas, autenticacao) importable
sys.path.insert(0, str(PROJECT_PATH))

import database  # noqa: E402  (must come after the sys.path change)
from app import aplicacao  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Flask test client (simulates a customer using the site) connected to a
    TEMPORARY database, created from scratch for every test. The project's
    real database is never touched.
    """
    monkeypatch.setattr(database, "CAMINHO_BASE_DADOS", tmp_path / "test.db")
    database.inicializar_base_dados()
    aplicacao.config["TESTING"] = True
    return aplicacao.test_client()


def run_sql(statement, parameters=()):
    """Runs a change (INSERT/UPDATE/DELETE) on the test database."""
    connection = database.obter_ligacao()
    try:
        connection.execute(statement, parameters)
        connection.commit()
    finally:
        connection.close()


def query_sql(statement, parameters=()):
    """Runs a SELECT on the test database and returns all the rows."""
    connection = database.obter_ligacao()
    try:
        return connection.execute(statement, parameters).fetchall()
    finally:
        connection.close()


@pytest.fixture
def insert_vehicle(client):
    """
    Returns a function that inserts a test vehicle into the database.

    The dates are calculated from TODAY, so the tests do not start failing
    just because time passes (the service date and legalisation of the sample
    vehicles eventually expire). By default the vehicle is available.
    """
    def insert(brand="Brand", model="Model", category="Médio", vehicle_type="Carro",
               transmission="Manual", seats=4, daily_rate=50.0,
               days_until_next_service=180, days_since_legalisation=30):
        today = date.today()
        run_sql(
            """
            INSERT INTO veiculos (marca, modelo, categoria, tipo_veiculo, transmissao,
                quantidade_pessoas, imagem, valor_diaria, data_ultima_revisao,
                data_proxima_revisao, data_ultima_legalizacao)
            VALUES (?, ?, ?, ?, ?, ?, 'x.jpg', ?, ?, ?, ?)
            """,
            (brand, model, category, vehicle_type, transmission, seats,
             daily_rate, (today - timedelta(days=30)).isoformat(),
             (today + timedelta(days=days_until_next_service)).isoformat(),
             (today - timedelta(days=days_since_legalisation)).isoformat()),
        )
    return insert


@pytest.fixture
def no_vehicles(client):
    """Deletes the sample vehicles, so each test controls what exists."""
    run_sql("DELETE FROM veiculos")


@pytest.fixture
def vehicle_for_dates():
    """
    Vehicle (dictionary) to test the date rules without a database: next
    service in 90 days and legalisation valid for another 335 days
    (legalisation lasts 365 days from the last one).
    """
    today = date.today()
    return {
        "data_proxima_revisao": (today + timedelta(days=90)).isoformat(),
        "data_ultima_legalizacao": (today - timedelta(days=30)).isoformat(),
        "valor_diaria": 50.0,
    }


@pytest.fixture
def registration_data():
    """Valid sign-up form data; each test changes whatever it needs."""
    return {
        "nome": "Test User",
        "utilizador": "test_user",
        "email": "test@example.com",
        "password": "Secure123",
        "confirmacao_password": "Secure123",
    }
