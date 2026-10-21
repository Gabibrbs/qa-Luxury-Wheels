# QA Luxury Wheels

**Português** | [English](#english)

Testes automáticos em **Python + pytest + Playwright** para o website [Luxury Wheels](https://github.com/Gabibrbs/luxury-wheels),
um site de aluguer de carros e motos feito com Flask e SQLite como projeto final do curso de Programação Python.
Autor: Gabriel Barbosa.

## O que contém

- **134 casos de teste:** 128 testes rápidos (regras de datas e preços, validação de formulários, páginas,
  pesquisa e filtros, registo e início de sessão, incluindo valores-limite, testes negativos e de segurança)
  e 6 testes de interface com **Playwright**, que abrem o site num browser real (registo, pesquisa, reserva,
  pagamento e cancelamento).
- **Testes independentes:** cada teste corre numa base de dados temporária própria.
- **Plano de testes:** as técnicas e a cobertura estão descritas em [`docs/test_plan.md`](docs/test_plan.md).
- **Integração contínua:** os testes correm no GitHub Actions a cada *push*.

> A aplicação testada está escrita em português (requisito do curso), por isso os nomes das suas funções,
> campos de formulário e mensagens aparecem nos testes exatamente como estão nesse projeto.

## Como correr

Coloca os dois repositórios lado a lado:

```
pasta/
  luxury-wheels/       (git clone https://github.com/Gabibrbs/luxury-wheels.git)
  qa-luxury-wheels/    (este repositório)
```

Depois, dentro de `qa-luxury-wheels`:

```
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest
```

O segundo comando descarrega o browser usado pelos testes de interface (só é preciso uma vez).
Para correr só os testes rápidos, sem browser: `python -m pytest -m "not e2e"`.
Para ver o browser a trabalhar: `python -m pytest tests/e2e --headed --slowmo 500`.

Para gerar um relatório HTML:

```
python -m pytest --html=report.html --self-contained-html
```

Se o projeto estiver noutra pasta, define a variável de ambiente `LUXURY_WHEELS_PATH`.

## Estrutura

```
tests/conftest.py                 fixtures partilhadas (base de dados temporária, veículos de teste, dados de registo)
tests/sql_helpers.py              funções para ler e alterar a base de dados de teste
tests/e2e/conftest.py             arranca o site para os testes de browser (servidor e base de dados temporários)
tests/e2e/test_user_journeys.py   percursos do cliente no browser (Playwright)
tests/test_dates.py               datas e regras de reserva
tests/test_prices.py              resumo e preço da reserva
tests/test_validations.py         utilizador, e-mail, password e cartão
tests/test_web_public.py          páginas públicas, pesquisa e filtros
tests/test_web_authentication.py  registo, início e fim de sessão
docs/test_plan.md                 plano de testes
```

---

## English

Automated tests in **Python + pytest + Playwright** for the [Luxury Wheels](https://github.com/Gabibrbs/luxury-wheels)
website, a car and motorbike rental site built with Flask and SQLite as the final project of a Python
programming course. Author: Gabriel Barbosa.

### What it contains

- **134 test cases:** 128 fast tests (date and price rules, form validation, pages, search and filters,
  sign-up and login, including boundary-value, negative and security tests) and 6 UI tests with
  **Playwright** that open the site in a real browser (sign-up, search, booking, payment and cancellation).
- **Independent tests:** every test runs on its own temporary database.
- **Test plan:** techniques and coverage are described in [`docs/test_plan.md`](docs/test_plan.md).
- **Continuous integration:** the tests run on GitHub Actions on every push.

> The application under test is written in Portuguese (a course requirement), so the names of its
> functions, form fields and messages appear in the tests exactly as they are in that project.

### How to run

Put both repositories side by side:

```
folder/
  luxury-wheels/       (git clone https://github.com/Gabibrbs/luxury-wheels.git)
  qa-luxury-wheels/    (this repository)
```

Then, inside `qa-luxury-wheels`:

```
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest
```

The second command downloads the browser used by the UI tests (needed only once).
To run only the fast tests, without a browser: `python -m pytest -m "not e2e"`.
To watch the browser work: `python -m pytest tests/e2e --headed --slowmo 500`.

To generate an HTML report:

```
python -m pytest --html=report.html --self-contained-html
```

If the project is in another folder, set the `LUXURY_WHEELS_PATH` environment variable.

### Structure

```
tests/conftest.py                 shared fixtures (temporary database, test vehicles, sign-up data)
tests/sql_helpers.py              functions to read and change the test database
tests/e2e/conftest.py             starts the site for the browser tests (temporary server and database)
tests/e2e/test_user_journeys.py   customer journeys in the browser (Playwright)
tests/test_dates.py               dates and booking rules
tests/test_prices.py              booking summary and price
tests/test_validations.py         username, e-mail, password and card
tests/test_web_public.py          public pages, search and filters
tests/test_web_authentication.py  sign-up, login and logout
docs/test_plan.md                 test plan
```
