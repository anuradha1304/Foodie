# 01 — Requirements Specification

## 1. Objective

An online food ordering platform where customers browse restaurants, view menus, build a
cart, place orders, and track them; and where restaurant admins manage menu items and
process incoming orders.

## 2. Actors

| Actor | Role constant | Capabilities |
|---|---|---|
| Customer | `ROLE_CUSTOMER` | Register, login, browse, cart, order, track, history |
| Restaurant Admin | `ROLE_RESTAURANT_ADMIN` | Manage own restaurant's menu, process own restaurant's orders |
| Anonymous | — | View restaurant list and menus only. Cannot cart or order. |

A `RESTAURANT_ADMIN` owns exactly one restaurant in this scope.

## 3. Functional requirements

### FR-A: Authentication (both actors)
- **FR-A1** Register with full name, email, password, phone, role. Email must be unique.
- **FR-A2** Password minimum 8 characters, stored BCrypt-hashed.
- **FR-A3** Login with email + password, establishing an HTTP session.
- **FR-A4** Logout invalidates the session.
- **FR-A5** `GET /api/auth/me` returns the current user or 401.

### FR-B: Browse (customer / anonymous)
- **FR-B1** List all restaurants with name, cuisine, image, open/closed status.
- **FR-B2** Filter restaurant list by cuisine type and search by name (server-side).
- **FR-B3** View one restaurant's menu, grouped by category.
- **FR-B4** Unavailable menu items are shown but visually disabled and cannot be added.

### FR-C: Cart (customer)
- **FR-C1** Add a menu item to the cart with a quantity ≥ 1.
- **FR-C2** A cart may only contain items from **one restaurant**. Adding an item from a
  different restaurant prompts the user to clear the cart first (HTTP 409).
- **FR-C3** Update the quantity of a cart line; quantity 0 removes the line.
- **FR-C4** Remove a single line; clear the whole cart.
- **FR-C5** The cart is persisted server-side per user and survives logout/login.
- **FR-C6** All cart mutations happen via AJAX with **no page reload**. The cart badge and
  totals update in place.
- **FR-C7** Cart returns subtotal, delivery fee, and total, computed server-side. The client
  never computes money.

### FR-D: Order placement (customer)
- **FR-D1** Place an order from the current cart with a delivery address and optional note.
- **FR-D2** Placement fails (HTTP 409) if: the cart is empty, the restaurant is closed, or any
  item in the cart has become unavailable or price-changed since it was added.
- **FR-D3** On success: an `Order` + `OrderItem`s are created, the cart is emptied, and an
  order number is returned. This is a single atomic transaction.
- **FR-D4** `OrderItem` stores a **snapshot** of item name and unit price at order time. Later
  menu price changes must never alter a historical order total.
- **FR-D5** Concurrent placement of the same cart (double-click / double submit) must create
  exactly one order.

### FR-E: Order tracking & history (customer)
- **FR-E1** View a single order's current status and full status timeline.
- **FR-E2** The tracking page polls status every 5 seconds via AJAX.
- **FR-E3** List all of the customer's past orders, newest first, paginated.
- **FR-E4** A customer may cancel an order **only** while it is in `PLACED`.
- **FR-E5** A customer can only see their own orders. Accessing another user's order → 403.

### FR-F: Menu management (restaurant admin)
- **FR-F1** Add a menu item: name, description, category, price, image URL, availability.
- **FR-F2** Update any field of an existing item, including price.
- **FR-F3** Toggle availability without deleting the item.
- **FR-F4** Soft-delete a menu item (never hard delete — historical orders reference it).
- **FR-F5** Toggle the restaurant's open/closed flag.
- **FR-F6** Admin may only touch items belonging to their own restaurant → else 403.

### FR-G: Order processing (restaurant admin)
- **FR-G1** View incoming orders for the owned restaurant, filterable by status.
- **FR-G2** Accept or reject a `PLACED` order. Rejection requires a reason.
- **FR-G3** Advance status through the allowed transition path only.
- **FR-G4** Every status change writes a row to the status history table.
- **FR-G5** Two admins acting on the same order concurrently: the second write fails with 409,
  not a silent overwrite.

## 4. Order status model

```
PLACED ──accept──> ACCEPTED ──> PREPARING ──> OUT_FOR_DELIVERY ──> DELIVERED
  │                                                                   (terminal)
  ├──reject──> REJECTED   (terminal)
  └──cancel──> CANCELLED  (terminal, customer-initiated)
```

**Allowed transitions — enforce this table in code, not in the UI:**

| From | Allowed to | Who |
|---|---|---|
| `PLACED` | `ACCEPTED`, `REJECTED` | Restaurant admin |
| `PLACED` | `CANCELLED` | Customer (owner) |
| `ACCEPTED` | `PREPARING` | Restaurant admin |
| `PREPARING` | `OUT_FOR_DELIVERY` | Restaurant admin |
| `OUT_FOR_DELIVERY` | `DELIVERED` | Restaurant admin |
| `REJECTED`, `CANCELLED`, `DELIVERED` | — (terminal) | — |

Any transition not in this table returns HTTP 409 with code `INVALID_STATUS_TRANSITION`.

## 5. Non-functional requirements

- **NFR-1 (Concurrency)** Order placement and status updates must be safe under concurrent
  access. See `03-architecture.md` §5 — this is a graded requirement of the project.
- **NFR-2 (Async)** Notification/side-effect work (confirmation "email", status-history
  enrichment) runs on a `@Async` thread pool and never blocks the HTTP response.
- **NFR-3 (Security)** BCrypt passwords, role-based endpoint authorization, ownership checks
  on every resource access, CSRF handled explicitly for the AJAX frontend.
- **NFR-4 (Money)** All monetary values `BigDecimal`, scale 2, `RoundingMode.HALF_UP`.
- **NFR-5 (No N+1)** Listing endpoints must not trigger N+1 queries. Use `JOIN FETCH` or
  `@EntityGraph` where an association is needed.
- **NFR-6 (DI)** All wiring by constructor injection — this demonstrates the Spring DI
  requirement of the project.
- **NFR-7 (Maven)** All dependencies managed in a single `pom.xml` with the Spring Boot BOM.

## 6. Business constants

| Constant | Value | Location |
|---|---|---|
| Delivery fee | ₹40.00 flat | `application.yml` → `app.order.delivery-fee` |
| Free delivery threshold | ₹500.00 subtotal | `app.order.free-delivery-threshold` |
| Max quantity per cart line | 20 | `app.cart.max-quantity` |
| Order-history page size | 10 | `app.order.page-size` |
| Currency | INR (`₹`) | display only |

## 7. Out of scope

Payment gateway integration, delivery-partner assignment, live GPS tracking, ratings and
reviews, coupons/discounts, multi-restaurant carts, email/SMS delivery to real providers
(log to console instead), image file upload (URLs only).
