"""
Fixtures for the browser tests (Playwright).

These tests open the real website in a real browser (Chromium), so the Flask
application has to be running. The fixtures below start it in the background
on a free port, connected to a TEMPORARY database that is recreated for every
test. The project's real database is never touched.

The pytest-playwright plugin provides the `page` fixture (a fresh browser tab,
isolated for each test). The shared `tests/conftest.py` has already made the
Luxury Wheels modules importable.
"""

import logging
import threading

import pytest
from werkzeug.serving import make_server

import autenticacao
import database
from app import aplicacao


@pytest.fixture(scope="session")
def live_server():
    """Starts the website once for the whole run and returns its address."""
    logging.getLogger("werkzeug").setLevel(logging.ERROR)  # no request log in test output
    server = make_server("127.0.0.1", 0, aplicacao, threaded=True)  # port 0 = any free port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join()


@pytest.fixture(scope="session")
def base_url(live_server):
    """Makes page.goto("/veiculos") work: relative paths use the server address."""
    return live_server


@pytest.fixture(autouse=True)
def fresh_database(live_server, tmp_path, monkeypatch):
    """A new, empty database (with the 16 sample vehicles) for every test."""
    monkeypatch.setattr(database, "CAMINHO_BASE_DADOS", tmp_path / "e2e.db")
    database.inicializar_base_dados()


@pytest.fixture
def existing_user(fresh_database):
    """A customer who already has an account, created directly in the database."""
    user = {
        "name": "Maria Teste",
        "username": "maria_teste",
        "email": "maria@example.com",
        "password": "Secure123",
    }
    autenticacao.criar_cliente(
        user["name"], user["username"], user["email"], user["password"], False
    )
    return user
