# 07 — Verification Scenarios

The agent must run every row and report PASS / FAIL with evidence. The project is not done
until all rows pass.

## A. Authentication

| # | Scenario | Expected |
|---|---|---|
| A1 | Register with a new email | 201, user row exists, `password_hash` starts with `$2a$` |
| A2 | Register with an existing email | 409 `EMAIL_ALREADY_EXISTS` |
| A3 | Register with password `abc` | 400, `fieldErrors.password` present |
| A4 | Login with correct credentials | 200 + `JSESSIONID` cookie set |
| A5 | Login with wrong password | 401 `BAD_CREDENTIALS`, no cookie |
| A6 | `GET /api/cart` with no session | **JSON** 401, not an HTML redirect |
| A7 | Any response anywhere | never contains `passwordHash` |

## B. Browsing

| # | Scenario | Expected |
|---|---|---|
| B1 | List restaurants anonymously | 200, all seeded restaurants |
| B2 | Search by partial name | filtered server-side (verify SQL contains `LIKE`) |
| B3 | Filter by cuisine | only matching rows |
| B4 | View a menu | grouped by category, deleted items absent |
| B5 | Unavailable item in menu response | present with `isAvailable: false` |
| B6 | Restaurant list SQL query count | constant, independent of row count (no N+1) |

## C. Cart

| # | Scenario | Expected |
|---|---|---|
| C1 | Add an item | 200, full CartResponse, `itemCount` 1 |
| C2 | Add the same item again | quantity becomes 2, still one `cart_items` row |
| C3 | Add an item from a different restaurant | 409 `CART_RESTAURANT_MISMATCH` |
| C4 | Add an unavailable item | 409 `ITEM_UNAVAILABLE` |
| C5 | Set quantity to 0 | line removed |
| C6 | Set quantity to 21 | 400 validation error |
| C7 | Remove the last line | `carts.restaurant_id` is NULL in the DB |
| C8 | Subtotal 450.00 | `deliveryFee` 40.00, total 490.00 |
| C9 | Subtotal exactly 500.00 | `deliveryFee` 0.00, total 500.00 |
| C10 | Logout and log back in | cart contents survive |
| C11 | Add to cart in the browser | **zero** page reloads in the network panel |

## D. Order placement

| # | Scenario | Expected |
|---|---|---|
| D1 | Place an order from a valid cart | 201, order + items + one history row, cart emptied |
| D2 | Place from an empty cart | 409 `CART_EMPTY` |
| D3 | Place while the restaurant is closed | 409 `RESTAURANT_CLOSED` |
| D4 | Admin marks an item unavailable, then customer places | 409 `ITEM_UNAVAILABLE` |
| D5 | Admin changes a price after the item is carted, then customer places | 409 `PRICE_CHANGED` |
| D6 | Repeat POST with the same `Idempotency-Key` | 200, same `orderNumber`, one row in `orders` |
| D7 | Change a menu item's price after an order is placed | historical order total unchanged |
| D8 | Customer A opens customer B's order | 403 `FORBIDDEN` |
| D9 | `OrderConcurrencyTest`, 20 threads | exactly the expected number succeed; 10 runs, 10 passes |

## E. Order lifecycle

| # | Scenario | Expected |
|---|---|---|
| E1 | Admin accepts a `PLACED` order | `ACCEPTED` + history row |
| E2 | Admin rejects with a reason | `REJECTED`, reason stored and shown to the customer |
| E3 | Reject with no reason | 400 validation error |
| E4 | `PLACED` → `DELIVERED` directly | 409 `INVALID_STATUS_TRANSITION` |
| E5 | `DELIVERED` → anything | 409 `INVALID_STATUS_TRANSITION` |
| E6 | Customer cancels while `PLACED` | `CANCELLED` |
| E7 | Customer cancels while `PREPARING` | 409 `INVALID_STATUS_TRANSITION` |
| E8 | Two admin threads update the same order simultaneously | one 200, one 409 `CONCURRENT_MODIFICATION` |
| E9 | Admin B accesses admin A's order | 403 `FORBIDDEN` |
| E10 | Full lifecycle | five history rows in chronological order |

## F. Admin menu

| # | Scenario | Expected |
|---|---|---|
| F1 | Add a menu item | 201, visible on the public menu |
| F2 | Update the price | new price on the menu, old orders unchanged |
| F3 | Toggle availability off | item still listed, `isAvailable: false`, cannot be carted |
| F4 | Soft-delete an item | absent from the public menu, still resolvable from old orders |
| F5 | Admin B edits admin A's item | 403 `FORBIDDEN` |
| F6 | Close the restaurant | listing shows CLOSED, ordering blocked |

## G. Async

| # | Scenario | Expected |
|---|---|---|
| G1 | Place an order | log line on a `foodapp-async-*` thread, not `http-nio-*` |
| G2 | Notification deliberately sleeps 2 s | HTTP response still returns immediately |
| G3 | Order placement rolls back | no notification logged |

## H. Frontend end-to-end

| # | Scenario | Expected |
|---|---|---|
| H1 | Register → browse → menu → cart → checkout → confirm → track | completes without error |
| H2 | Customer tracking tab open, admin advances status in another tab | tracking updates within 5 s, no reload |
| H3 | Order reaches `DELIVERED` | polling interval cleared (verify: no further network calls) |
| H4 | Navigate away from tracking | interval cleared, no console errors |
| H5 | Backend stopped mid-session | error toast shown, not a blank page or unhandled rejection |
| H6 | Every page at 375 px width | usable, no horizontal scroll |
| H7 | `grep -r "fetch(" static/js --exclude=api.js` | no matches |
| H8 | Tab through login and checkout forms | visible focus rings, correct order |

## I. Build health

| # | Check | Expected |
|---|---|---|
| I1 | `mvn clean verify` | BUILD SUCCESS, zero test failures |
| I2 | Compiler warnings | no deprecation warnings from Spring APIs |
| I3 | `grep -ri "javax\." src/main/java` | no matches (must be `jakarta.*`) |
| I4 | `grep -ri "password" application.yml` | only an env-var placeholder, never a literal |
| I5 | Fresh DB + `mvn spring-boot:run` | schema created, seed loaded, app usable |
| I6 | `open-in-view` | `false` in `application.yml` |

## Reporting format

The agent reports as a table: scenario id, PASS/FAIL, evidence (log excerpt, SQL result,
screenshot filename, or test name). FAIL rows list the root cause and the fix applied.
