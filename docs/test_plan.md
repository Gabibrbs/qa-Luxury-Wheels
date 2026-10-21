# Test plan: Luxury Wheels

**Goal:** check that the car rental website follows the rules in the course brief, and that its validations
reject invalid data without breaking the site.

**Scope:** business rules (dates, prices, vehicle availability), form validation, public and private pages,
search and filters, sign-up and login.
**Out of scope (for now):** payment, changing and cancelling bookings, and browser-level UI tests
(planned next, with Playwright).

## Techniques used

- **Boundary-value analysis:** test the exact limit and the next value (30 and 31 days, usernames of
  2, 3, 20 and 21 characters, legalisation of 365 and 366 days, booking ending on the expiry day).
- **Equivalence partitioning:** one case per group of similar data (valid and invalid e-mails, valid and
  invalid filters).
- **Negative testing:** empty, malformed or malicious input (`'; DROP TABLE`, redirects to external sites).
- **Independent tests:** each test creates its own temporary database and does not depend on the others.
- **Dates relative to today:** test data is calculated from the current date, so tests do not fail just
  because time passes.

## Test cases

| Area | Rule checked | File | Cases |
|---|---|---|---|
| Dates | Conversion of DD/MM/YYYY and YYYY-MM-DD; impossible dates (31 April, 29 February in a non-leap year) | `test_dates.py` | 13 |
| Dates | Day count includes both the start and the end day | `test_dates.py` | 4 |
| Dates | Invalid dates; start in the past or today; end before start | `test_dates.py` | 6 |
| Dates | 30-day maximum (29 and 30 accepted, 31 rejected) | `test_dates.py` | 3 |
| Dates | The vehicle's service date and legalisation limit the booking (including the boundary days) | `test_dates.py` | 6 |
| Prices | Daily rates, per-day and fixed extras, total, rounding | `test_prices.py` | 5 |
| Prices | 200 km included per day; service-date warning during the booking | `test_prices.py` | 8 |
| Validation | Username and e-mail (valid, invalid, boundaries) | `test_validations.py` | 20 |
| Validation | Password and card (valid, invalid, boundaries) | `test_validations.py` | 16 |
| Public site | Pages open, 404, private pages redirect to login | `test_web_public.py` | 9 |
| Public site | Only available vehicles are listed (365-day and service-date boundaries) | `test_web_public.py` | 3 |
| Public site | Partial search, filters and price ordering; invalid filters | `test_web_public.py` | 17 |
| Authentication | Valid and invalid sign-up, repeated username/e-mail, hashed password | `test_web_authentication.py` | 8 |
| Authentication | Right and wrong login, logout, private page, return to the requested page | `test_web_authentication.py` | 7 |
| Security | Login does not redirect to external sites | `test_web_authentication.py` | 3 |

Total: 128 cases (parametrised), about 3 seconds to run.

## Checking the quality of the tests

To confirm that the tests really detect errors, the project code was deliberately broken in 8 places
(for example a 31-day maximum instead of 30, a day count without the end day, an exclusive minimum-price
filter). The first run missed one of them, the booking ending exactly on the legalisation expiry day, so a
boundary test was added. With it, all 8 changes are detected.
