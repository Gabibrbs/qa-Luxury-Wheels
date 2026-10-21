# QA Luxury Wheels

Automated tests in **Python + pytest** for the [Luxury Wheels](https://github.com/Gabibrbs/luxury-wheels)
website, a car and motorbike rental site built with Flask and SQLite as the final project of a Python
programming course.

- **128 test cases:** date and price rules, form validation, pages, search and filters, sign-up and login,
  including boundary-value, negative and security tests.
- **Independent tests:** every test runs on its own temporary database.
- **Test plan:** techniques and coverage are described in [`docs/test_plan.md`](docs/test_plan.md).
- **Continuous integration:** the tests run on GitHub Actions on every push.

> The application under test is written in Portuguese (a course requirement), so the names of its
> functions, form fields and messages appear in the tests exactly as they are in that project.

## How to run

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

## Structure

```
tests/conftest.py                 shared fixtures (temporary database, test vehicles, sign-up data)
tests/test_dates.py               dates and booking rules
tests/test_prices.py              booking summary and price
tests/test_validations.py         username, e-mail, password and card
tests/test_web_public.py          public pages, search and filters
tests/test_web_authentication.py  sign-up, login and logout
docs/test_plan.md                 test plan
```
