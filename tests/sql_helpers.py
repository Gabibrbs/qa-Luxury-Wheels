"""
Small helpers to read and change the test database directly.

They live in their own module (not in conftest.py) because there is more than
one conftest.py in this repository (tests/ and tests/e2e/), and importing from
a module called "conftest" would be ambiguous.
"""

import database  # the Luxury Wheels module; tests/conftest.py makes it importable


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
