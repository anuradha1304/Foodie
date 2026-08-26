# 06 — Build Plan

Nine milestones. **Run one milestone per agent task.** Do not combine them — a single
"build the whole app" run produces an unreviewable diff and buries bugs.

Each milestone below has a prompt you paste into the Antigravity agent panel verbatim, plus
acceptance criteria the agent must satisfy before you accept the changes and commit.

---

## M0 — Project scaffold

> Read `/docs/AGENTS.md`, `/docs/00-INDEX.md` and `/docs/03-architecture.md`.
> Use context7 to confirm current Spring Boot 3.3 project setup.
> Create a Maven Spring Boot 3.3 project: groupId `com.foodapp`, artifactId
> `food-ordering-system`, Java 17, packaging jar. Add exactly the dependencies listed in
> `03-architecture.md` §9. Create the full empty package structure from §1. Write
> `application.yml` per §8 and an `application-test.yml` using H2. Add `.gitignore`.
> Create the MySQL database `food_ordering_dev` and a `foodapp` user via the mysql MCP
> server. Verify `mvn clean compile` and `mvn spring-boot:run` both succeed, then stop the app.

**Accept when:** app starts and stops cleanly; `git status` shows no `target/` noise.

---

## M1 — Domain layer

> Read `/docs/02-data-model.md` in full. Create every entity, enum and repository interface
> exactly as specified — column names, lengths, nullability, unique constraints, indexes,
> `@Version` fields, `@Enumerated(STRING)`, all `@ManyToOne` LAZY, `BigDecimal` for money.
> Add `data.sql` seed data per §5 with BCrypt-hashed passwords.
> Start the app so Hibernate creates the schema, then run the verification query from §4
> through the mysql MCP server and paste the result. Fix any mismatch in the entity mappings.

**Accept when:** the `INFORMATION_SCHEMA` output matches §3 table by table; seed rows exist;
no `float`/`double` money columns; every enum column is `VARCHAR`.

---

## M2 — Security & authentication

> Read `/docs/03-architecture.md` §6 and `/docs/04-api-contract.md` §A.
> Use context7 for Spring Security 6.x — do NOT use `WebSecurityConfigurerAdapter`.
> Implement `SecurityConfig` (SecurityFilterChain, BCryptPasswordEncoder,
> `@EnableMethodSecurity`), `AppUserDetailsService`, `SecurityUtils.currentUserId()`,
> a JSON `AuthenticationEntryPoint` returning 401 (never a redirect), CSRF via
> `CookieCsrfTokenRepository.withHttpOnlyFalse()`, `AuthService`, `AuthController`,
> the exception hierarchy and `GlobalExceptionHandler` with the error format from §7.
> Write integration tests for register (success + duplicate email + weak password),
> login (success + bad credentials), and `/api/auth/me` (authenticated + 401).

**Accept when:** all four `/api/auth` endpoints behave per the contract; `password_hash` never
appears in any response; an unauthenticated `/api/cart` call returns JSON 401, not HTML.

---

## M3 — Restaurant browsing & menu (read side)

> Read `/docs/04-api-contract.md` §B. Implement `RestaurantService`, `MenuService`,
> `RestaurantController`, and the response DTOs/mappers. Menu items must be grouped by
> category, soft-deleted items excluded, unavailable items included with the flag.
> Search and cuisine filtering happen in the database, not in Java. Use `@EntityGraph` or
> `JOIN FETCH` so the listing endpoint does not N+1 — verify by reading the SQL log and
> report the query count for a 2-restaurant listing.

**Accept when:** endpoints match the contract; the restaurant list executes a constant number
of queries regardless of row count.

---

## M4 — Cart with AJAX (server side)

> Read `/docs/01-requirements.md` FR-C and `/docs/04-api-contract.md` §C.
> Implement `CartService`, `CartController`, `CartResponse`. Enforce: one restaurant per cart
> (409 `CART_RESTAURANT_MISMATCH`), add-existing increments quantity, quantity 0 removes,
> max quantity 20, unavailable items rejected, `carts.restaurant_id` reset to NULL when the
> last line is removed. All money computed server-side with `BigDecimal` and the delivery-fee
> rules from `01-requirements.md` §6. Every endpoint returns the full `CartResponse`.
> Write unit tests for the totals calculation including the free-delivery threshold boundary.

**Accept when:** all six cart behaviours above have a passing test; totals are correct at
subtotal exactly 500.00.

---

## M5 — Order placement & concurrency ⚠️ most important milestone

> Read `/docs/03-architecture.md` §4 and §5 carefully, and `/docs/04-api-contract.md` §D.
> Implement `OrderService.placeOrder` as a single `@Transactional` method that:
> pessimistically locks the cart's menu items **sorted by id ascending**, re-validates
> availability / restaurant-open / price-unchanged, creates the `Order` with an
> `orderNumber`, creates `OrderItem` snapshot rows (name + unit price copied, not
> referenced), writes the initial `PLACED` history row, and clears the cart.
> Implement idempotency via the `Idempotency-Key` header + the unique constraint, catching
> `DataIntegrityViolationException` and returning the existing order.
> Implement `GET /api/orders`, `GET /api/orders/{id}`, `GET /api/orders/{id}/status`
> and cancel, with ownership checks returning 403.
> Then write `OrderConcurrencyTest` per §5.5: 20 threads, `CountDownLatch`, one
> last-available item, assert exactly one order succeeds and 19 fail with `ConflictException`.

**Accept when:** the concurrency test passes **10 consecutive runs**; a repeated POST with the
same idempotency key creates exactly one row in `orders` (verify via the mysql MCP server);
changing a menu item's price afterwards does not change the historical order total.

---

## M6 — Admin: menu management & order processing

> Read `/docs/01-requirements.md` FR-F/FR-G and `/docs/04-api-contract.md` §E/§F.
> Implement `AdminMenuController`, `AdminOrderController`, `OrderStatusService`.
> The restaurant id is always resolved from the session — never trusted from the request.
> Implement the transition table from `01-requirements.md` §4 as a validated state machine
> in `OrderStatusService`, rejecting invalid transitions with 409
> `INVALID_STATUS_TRANSITION`. Every transition writes an `order_status_history` row.
> Use `@Version` optimistic locking on `Order`; map `OptimisticLockingFailureException` to
> 409 `CONCURRENT_MODIFICATION` in the global handler.
> Write tests: every valid transition, a representative set of invalid ones, cross-restaurant
> access returning 403, and a two-thread simultaneous status update where exactly one wins.

**Accept when:** admin A cannot read or mutate admin B's restaurant or orders; the invalid
transition `PLACED → DELIVERED` returns 409; soft-deleted menu items still resolve correctly
in historical orders.

---

## M7 — Async notifications

> Read `/docs/03-architecture.md` §5.4. Implement `AsyncConfig` with the named
> `ThreadPoolTaskExecutor`, `NotificationService` with `@Async("taskExecutor")` methods that
> log order-placed and status-changed events, and domain events published from the services
> and consumed with `@TransactionalEventListener(phase = AFTER_COMMIT)`.
> Prove with a test that a rolled-back order placement fires **no** notification, and that
> the notification runs on a `foodapp-async-*` thread, not the request thread.

**Accept when:** logs show the async thread name; no notification on rollback; the HTTP
response time for placing an order is unaffected by a deliberately slow (2 s) notification.

---

## M8 — Frontend

Split this into three separate agent runs — it is too large for one.

**M8a — shell:**
> Read `/docs/05-frontend-spec.md` §1, §2, §4, §5. Create `base.css`, `components.css`,
> `js/api.js` (exactly as specified), `js/ui.js` (toast, modal, spinner, `formatMoney`),
> `js/auth.js`, plus `login.html`, `register.html` and the shared header. Verify login,
> logout and redirect-by-role in the browser.

**M8b — customer flow:**
> Read `/docs/05-frontend-spec.md` §3. Build `index.html`, `menu.html`, `cart.html`,
> `checkout.html`, `order-confirmation.html`, `order-tracking.html`, `order-history.html`
> with their JS modules. Then drive the full flow in the browser: register → browse →
> filter → open a menu → add two items → adjust quantity in the cart → checkout → confirm →
> track. Capture screenshots of each step. Confirm from the network panel that no cart or
> tracking action causes a page reload.

**M8c — admin flow:**
> Build `admin/dashboard.html`, `admin/menu.html`, `admin/order-detail.html` and their JS.
> Drive it in the browser: log in as an admin, add a menu item, toggle availability, then
> accept the order placed in M8b and advance it through every status while the customer's
> tracking page is open in a second tab — confirm the tracking page updates within 5 seconds
> without a reload.

**Accept M8 when:** the two-tab test above works, the tracking interval stops on `DELIVERED`,
and no `fetch(` call exists outside `js/api.js`.

---

## M9 — Hardening & documentation

> Run the full scenario list in `/docs/07-verification.md` and report pass/fail per row.
> Fix every failure. Then produce: a root `README.md` (setup, prerequisites, how to run,
> seeded credentials, screenshots), a generated ER diagram, and a short `ARCHITECTURE.md`
> summarising where each of the five "advanced concepts" — AJAX, Hibernate ORM, Spring DI,
> Maven, multithreading — is implemented, with file and line references.

**Accept when:** every row in `07-verification.md` passes and a fresh clone runs from the
README instructions alone.

---

## Commit convention

One commit per milestone:

```
feat(scaffold): initialise Spring Boot 3.3 project structure       # M0
feat(domain): add JPA entities, repositories and seed data          # M1
feat(auth): add Spring Security 6 config and auth endpoints         # M2
feat(catalog): add restaurant and menu browsing endpoints           # M3
feat(cart): add persistent cart with server-side totals             # M4
feat(order): add order placement with pessimistic locking           # M5
feat(admin): add menu management and order status state machine     # M6
feat(async): add async notifications on transaction commit          # M7
feat(ui): add customer and admin frontend                           # M8
docs(readme): add setup guide and architecture notes                # M9
```
