# Plano de testes / Test plan: Luxury Wheels

**Português** | [English](#english)

## Plano de testes

**Objetivo:** verificar que o website de aluguer de veículos cumpre as regras do enunciado do curso e que as
validações rejeitam dados inválidos sem estragar o site.

**Âmbito:** regras de negócio (datas, preços, disponibilidade dos veículos), validação de formulários, páginas
públicas e privadas, pesquisa e filtros, registo e início de sessão, e os percursos principais do cliente no
browser (registo, pesquisa, reserva com pagamento e cancelamento).
**Fora do âmbito (por agora):** alteração das datas de uma reserva, recuperação de password, formulário de
contactos, outros browsers além do Chromium e o aspeto em ecrãs pequenos.

### Técnicas usadas

- **Análise de valores-limite:** testar o limite exato e o valor seguinte (30 e 31 dias, utilizadores com
  2, 3, 20 e 21 caracteres, legalização de 365 e 366 dias, reserva a terminar no dia de validade).
- **Partição por classes de equivalência:** um caso por grupo de dados semelhantes (e-mails válidos e
  inválidos, filtros válidos e inválidos).
- **Testes negativos:** dados vazios, mal formados ou maliciosos (`'; DROP TABLE`, redirecionamentos para sites externos).
- **Testes independentes:** cada teste cria a sua própria base de dados temporária e não depende dos outros.
- **Datas relativas a hoje:** os dados de teste são calculados a partir da data atual, para que os testes
  não falhem só por o tempo passar.
- **Testes de ponta a ponta (E2E) com Playwright:** poucos testes, lentos mas realistas, que usam o site num
  browser a sério. Os pormenores das regras ficam nos testes rápidos; os de browser verificam que os percursos funcionam do princípio ao fim.
- **Esperas automáticas:** os testes de browser não usam pausas fixas; esperam até a página mostrar o
  resultado esperado (ou até ao tempo limite), o que evita testes instáveis.

### Casos de teste

| Área | Regra verificada | Ficheiro | Casos |
|---|---|---|---|
| Datas | Conversão de DD/MM/AAAA e AAAA-MM-DD; datas impossíveis (31 de abril, 29 de fevereiro num ano não bissexto) | `test_dates.py` | 13 |
| Datas | A contagem de dias inclui o dia de início e o dia de fim | `test_dates.py` | 4 |
| Datas | Datas inválidas; início no passado ou hoje; fim antes do início | `test_dates.py` | 6 |
| Datas | Máximo de 30 dias (29 e 30 aceites, 31 rejeitado) | `test_dates.py` | 3 |
| Datas | A data de revisão e o limite de legalização do veículo condicionam a reserva (incluindo os dias-limite) | `test_dates.py` | 6 |
| Preços | Diárias, extras por dia e fixos, total, arredondamento | `test_prices.py` | 5 |
| Preços | 200 km incluídos por dia; aviso de revisão durante a reserva | `test_prices.py` | 8 |
| Validação | Utilizador e e-mail (válidos, inválidos, limites) | `test_validations.py` | 20 |
| Validação | Password e cartão (válidos, inválidos, limites) | `test_validations.py` | 16 |
| Site público | Páginas abrem, 404, páginas privadas redirecionam para o login | `test_web_public.py` | 9 |
| Site público | Só os veículos disponíveis são listados (limites de 365 dias e da data de revisão) | `test_web_public.py` | 3 |
| Site público | Pesquisa parcial, filtros e ordenação por preço; filtros inválidos | `test_web_public.py` | 17 |
| Autenticação | Registo válido e inválido, utilizador/e-mail repetidos, password com *hash* | `test_web_authentication.py` | 8 |
| Autenticação | Início de sessão certo e errado, fim de sessão, página privada, regresso à página pedida | `test_web_authentication.py` | 7 |
| Segurança | O início de sessão não redireciona para sites externos | `test_web_authentication.py` | 3 |
| Browser (E2E) | Registo, fim de sessão e novo início de sessão | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Pesquisa por tipo, pesquisa sem resultados e "limpar filtros" | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Visitante enviado para o login e devolvido ao veículo escolhido | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Reserva e pagamento; a reserva aparece em "As minhas reservas" | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | O valor total e o número de dias aparecem antes de pagar | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Cancelamento com reembolso; a reserva fica "Cancelada" | `e2e/test_user_journeys.py` | 1 |

Total: 134 casos (128 rápidos, parametrizados, cerca de 3 segundos; 6 de browser, cerca de 15 segundos).

### Verificação da qualidade dos testes

Para confirmar que os testes detetam mesmo erros, o código do projeto foi estragado de propósito em 8 sítios
(por exemplo, máximo de 31 dias em vez de 30, contagem de dias sem o dia de fim, filtro de preço mínimo
exclusivo). Na primeira execução um deles passou sem ser detetado, a reserva a terminar exatamente no dia de
validade da legalização, por isso foi acrescentado um teste de valor-limite. Com ele, as 8 alterações são detetadas.

Os testes de browser foram verificados da mesma forma, com 5 erros deliberados: um cancelamento que não cancela,
um início de sessão que ignora a página pedida, um filtro de tipo que não filtra, uma contagem de dias sem o dia
de fim e um registo que não inicia a sessão. Cada erro fez falhar pelo menos um teste.

---

## English

**Goal:** check that the car rental website follows the rules in the course brief, and that its validations
reject invalid data without breaking the site.

**Scope:** business rules (dates, prices, vehicle availability), form validation, public and private pages,
search and filters, sign-up and login, and the main customer journeys in the browser (sign-up, search,
booking with payment, and cancellation).
**Out of scope (for now):** changing the dates of a booking, password recovery, the contact form, browsers
other than Chromium, and the layout on small screens.

### Techniques used

- **Boundary-value analysis:** test the exact limit and the next value (30 and 31 days, usernames of
  2, 3, 20 and 21 characters, legalisation of 365 and 366 days, booking ending on the expiry day).
- **Equivalence partitioning:** one case per group of similar data (valid and invalid e-mails, valid and
  invalid filters).
- **Negative testing:** empty, malformed or malicious input (`'; DROP TABLE`, redirects to external sites).
- **Independent tests:** each test creates its own temporary database and does not depend on the others.
- **Dates relative to today:** test data is calculated from the current date, so tests do not fail just
  because time passes.
- **End-to-end (E2E) tests with Playwright:** a few slow but realistic tests that use the site in a real
  browser. The detail of the rules stays in the fast tests; the browser tests check that the journeys work
  from start to finish.
- **Automatic waiting:** the browser tests use no fixed pauses; they wait until the page shows the expected
  result (or until the timeout), which avoids flaky tests.

### Test cases

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
| Browser (E2E) | Sign-up, logout and logging in again | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Search by type, search with no results and "clear filters" | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | A visitor is sent to login and returned to the chosen vehicle | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Booking and payment; the booking appears in "My bookings" | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | The total and the number of days are shown before paying | `e2e/test_user_journeys.py` | 1 |
| Browser (E2E) | Cancellation with refund; the booking becomes "Cancelled" | `e2e/test_user_journeys.py` | 1 |

Total: 134 cases (128 fast, parametrised, about 3 seconds; 6 in the browser, about 15 seconds).

### Checking the quality of the tests

To confirm that the tests really detect errors, the project code was deliberately broken in 8 places
(for example a 31-day maximum instead of 30, a day count without the end day, an exclusive minimum-price
filter). The first run missed one of them, the booking ending exactly on the legalisation expiry day, so a
boundary test was added. With it, all 8 changes are detected.

The browser tests were checked the same way, with 5 deliberate errors: a cancellation that does not cancel,
a login that ignores the requested page, a type filter that does not filter, a day count without the end day,
and a sign-up that does not log the customer in. Each error made at least one test fail.
