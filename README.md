# QA Luxury Wheels

**Português** | [English](#english)

Testes automáticos em **Python + pytest** para o website [Luxury Wheels](https://github.com/Gabibrbs/luxury-wheels),
um site de aluguer de carros e motos feito com Flask e SQLite como projeto final do curso de Programação Python.
Autor: Gabriel Barbosa.

## O que contém

- **128 casos de teste:** regras de datas e preços, validação de formulários, páginas, pesquisa e filtros,
  registo e início de sessão, incluindo testes de valores-limite, negativos e de segurança.
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
python -m pytest
```

Para gerar um relatório HTML:

```
python -m pytest --html=report.html --self-contained-html
```

Se o projeto estiver noutra pasta, define a variável de ambiente `LUXURY_WHEELS_PATH`.

## Estrutura

```
tests/conftest.py                 fixtures partilhadas (base de dados temporária, veículos de teste, dados de registo)
tests/test_dates.py               datas e regras de reserva
tests/test_prices.py              resumo e preço da reserva
tests/test_validations.py         utilizador, e-mail, password e cartão
tests/test_web_public.py          páginas públicas, pesquisa e filtros
tests/test_web_authentication.py  registo, início e fim de sessão
docs/test_plan.md                 plano de testes
```

---

## English

Automated tests in **Python + pytest** for the [Luxury Wheels](https://github.com/Gabibrbs/luxury-wheels)
website, a car and motorbike rental site built with Flask and SQLite as the final project of a Python
programming course. Author: Gabriel Barbosa.

### What it contains

- **128 test cases:** date and price rules, form validation, pages, search and filters, sign-up and login,
  including boundary-value, negative and security tests.
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
python -m pytest
```

To generate an HTML report:

```
python -m pytest --html=report.html --self-contained-html
```

If the project is in another folder, set the `LUXURY_WHEELS_PATH` environment variable.

### Structure

```
tests/conftest.py                 shared fixtures (temporary database, test vehicles, sign-up data)
tests/test_dates.py               dates and booking rules
tests/test_prices.py              booking summary and price
tests/test_validations.py         username, e-mail, password and card
tests/test_web_public.py          public pages, search and filters
tests/test_web_authentication.py  sign-up, login and logout
docs/test_plan.md                 test plan
```
