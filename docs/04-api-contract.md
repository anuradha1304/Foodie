# 04 — REST API Contract

Base URL: `http://localhost:8080`
All request and response bodies are `application/json`.
All mutating requests must carry the `X-XSRF-TOKEN` header (see `03-architecture.md` §6).

---

## A. Authentication — `/api/auth`

### `POST /api/auth/register` — permitAll
```json
Request  { "fullName":"Amit Sharma", "email":"amit@x.com", "password":"Password123",
           "phone":"9876543210", "role":"CUSTOMER" }
201      { "id":5, "fullName":"Amit Sharma", "email":"amit@x.com", "role":"CUSTOMER" }
409      EMAIL_ALREADY_EXISTS
400      VALIDATION_FAILED
```
Validation: `fullName` 2–120 chars; `email` valid + ≤180; `password` ≥8 with at least one
letter and one digit; `phone` 10 digits; `role` in `{CUSTOMER, RESTAURANT_ADMIN}`.

### `POST /api/auth/login` — permitAll
```json
Request  { "email":"amit@x.com", "password":"Password123" }
200      { "id":5, "fullName":"Amit Sharma", "role":"CUSTOMER", "restaurantId":null }
401      BAD_CREDENTIALS
```
Sets the `JSESSIONID` session cookie. `restaurantId` is non-null only for admins.

### `POST /api/auth/logout` — authenticated → `204`
### `GET /api/auth/me` — authenticated → same body as login, or `401 UNAUTHENTICATED`

---

## B. Restaurants & menu — `/api/restaurants` (permitAll)

### `GET /api/restaurants?search=&cuisine=&openOnly=false`
```json
200 [ { "id":1, "name":"Punjab Grill", "cuisineType":"North Indian",
        "description":"...", "imageUrl":"...", "isOpen":true, "itemCount":14 } ]
```

### `GET /api/restaurants/{id}`
```json
200 { "id":1, "name":"Punjab Grill", "cuisineType":"North Indian", "address":"...",
      "phone":"...", "imageUrl":"...", "isOpen":true }
404 NOT_FOUND
```

### `GET /api/restaurants/{id}/menu`
Returns items grouped by category, deleted items excluded, unavailable items **included**
with the flag set (FR-B4).
```json
200 { "restaurantId":1, "restaurantName":"Punjab Grill", "isOpen":true,
      "categories":[
        { "category":"Starters",
          "items":[ { "id":10, "name":"Paneer Tikka", "description":"...",
                      "price":249.00, "imageUrl":"...", "isAvailable":true } ] } ] }
```

### `GET /api/restaurants/cuisines` → `200 ["North Indian","Italian","Chinese"]`

---

## C. Cart — `/api/cart` (ROLE_CUSTOMER)

**Every response from every cart endpoint is the full `CartResponse`**, so the frontend can
re-render from a single payload after any mutation.

```json
CartResponse {
  "cartId": 3,
  "restaurantId": 1,
  "restaurantName": "Punjab Grill",
  "items": [ { "cartItemId":7, "menuItemId":10, "name":"Paneer Tikka",
               "unitPrice":249.00, "quantity":2, "lineTotal":498.00,
               "isAvailable":true, "imageUrl":"..." } ],
  "itemCount": 2,
  "subtotal": 498.00,
  "deliveryFee": 40.00,
  "total": 538.00
}
```
An empty cart returns `restaurantId: null`, `items: []`, all money `0.00`.

| Endpoint | Body | Success | Errors |
|---|---|---|---|
| `GET /api/cart` | — | 200 CartResponse | — |
| `POST /api/cart/items` | `{ "menuItemId":10, "quantity":2 }` | 200 CartResponse | 409 `CART_RESTAURANT_MISMATCH`, 409 `ITEM_UNAVAILABLE`, 404, 400 |
| `PUT /api/cart/items/{cartItemId}` | `{ "quantity":3 }` | 200 CartResponse | 404, 400 |
| `DELETE /api/cart/items/{cartItemId}` | — | 200 CartResponse | 404 |
| `DELETE /api/cart` | — | 200 CartResponse (empty) | — |

Notes:
- `POST` with an item already in the cart **increments** quantity (capped at 20).
- `PUT` with `quantity: 0` removes the line.
- Removing the last line resets `carts.restaurant_id` to NULL.

---

## D. Orders — customer — `/api/orders` (ROLE_CUSTOMER)

### `POST /api/orders`
Header: `Idempotency-Key: <uuid>` (required — see `03-architecture.md` §5.3)
```json
Request  { "deliveryAddress":"H-12, Sector 34, Chandigarh", "customerNote":"No onions" }
201      OrderResponse
409      CART_EMPTY | RESTAURANT_CLOSED | ITEM_UNAVAILABLE | PRICE_CHANGED
400      VALIDATION_FAILED
```
A repeat call with the same `Idempotency-Key` returns `200` and the **existing** order.

```json
OrderResponse {
  "id": 21, "orderNumber":"ORD-20260825-0000A7",
  "status":"PLACED",
  "restaurantId":1, "restaurantName":"Punjab Grill",
  "items":[ { "itemName":"Paneer Tikka", "unitPrice":249.00,
              "quantity":2, "lineTotal":498.00 } ],
  "subtotal":498.00, "deliveryFee":40.00, "totalAmount":538.00,
  "deliveryAddress":"...", "customerNote":"No onions", "rejectionReason":null,
  "placedAt":"2026-08-25T14:32:10",
  "statusHistory":[ { "status":"PLACED", "note":null,
                      "changedAt":"2026-08-25T14:32:10" } ]
}
```

### `GET /api/orders?page=0&size=10` → paged order history, newest first
```json
200 { "content":[ OrderSummary ], "page":0, "size":10,
      "totalElements":23, "totalPages":3 }

OrderSummary { "id":21, "orderNumber":"...", "restaurantName":"Punjab Grill",
               "status":"DELIVERED", "totalAmount":538.00, "itemCount":2,
               "placedAt":"..." }
```

### `GET /api/orders/{id}` → full `OrderResponse`. `403 FORBIDDEN` if not the owner.

### `GET /api/orders/{id}/status` — the lightweight polling endpoint (FR-E2)
```json
200 { "orderNumber":"ORD-20260825-0000A7", "status":"PREPARING",
      "updatedAt":"2026-08-25T14:41:02",
      "statusHistory":[ { "status":"PLACED","changedAt":"..." },
                        { "status":"ACCEPTED","changedAt":"..." },
                        { "status":"PREPARING","changedAt":"..." } ] }
```
Keep this response small — it is polled every 5 seconds.

### `POST /api/orders/{id}/cancel`
```json
Request  { "reason":"Ordered by mistake" }
200      OrderResponse (status CANCELLED)
409      INVALID_STATUS_TRANSITION   // anything other than PLACED
403      FORBIDDEN                    // not the owner
```

---

## E. Menu management — admin — `/api/admin/menu` (ROLE_RESTAURANT_ADMIN)

All endpoints operate implicitly on **the caller's own restaurant**. The restaurant id is
resolved from the session, never taken from the request body.

| Endpoint | Body | Success | Errors |
|---|---|---|---|
| `GET /api/admin/menu` | — | 200 list of MenuItemAdminResponse (includes deleted flag) | — |
| `POST /api/admin/menu` | `{ "name","description","category","price","imageUrl","isAvailable" }` | 201 item | 400 |
| `PUT /api/admin/menu/{id}` | same fields (all optional) | 200 item | 403, 404, 409 `CONCURRENT_MODIFICATION` |
| `PATCH /api/admin/menu/{id}/availability` | `{ "isAvailable": false }` | 200 item | 403, 404 |
| `DELETE /api/admin/menu/{id}` | — | 204 (soft delete) | 403, 404 |

### `PATCH /api/admin/restaurant/status` — `{ "isOpen": false }` → `200` restaurant

---

## F. Order processing — admin — `/api/admin/orders` (ROLE_RESTAURANT_ADMIN)

### `GET /api/admin/orders?status=PLACED&page=0&size=10`
Returns only orders for the caller's restaurant. `status` optional.
```json
200 { "content":[ AdminOrderSummary ], "page":0, ... }

AdminOrderSummary { "id":21, "orderNumber":"...", "customerName":"Amit Sharma",
                    "customerPhone":"9876543210", "status":"PLACED",
                    "totalAmount":538.00, "itemCount":2, "placedAt":"..." }
```

### `GET /api/admin/orders/{id}` → full order incl. items, address and note. `403` if not owned.

### `POST /api/admin/orders/{id}/accept` → `200` OrderResponse (`ACCEPTED`)
### `POST /api/admin/orders/{id}/reject`
```json
Request { "reason":"Kitchen closed early" }   // required, 5–300 chars
200     OrderResponse (REJECTED)
409     INVALID_STATUS_TRANSITION
```

### `PATCH /api/admin/orders/{id}/status`
```json
Request { "status":"PREPARING", "note":"Started cooking" }
200     OrderResponse
409     INVALID_STATUS_TRANSITION | CONCURRENT_MODIFICATION
403     FORBIDDEN
```
The transition table in `01-requirements.md` §4 is enforced here, server-side.

---

## G. HTTP status conventions

| Status | Meaning in this API |
|---|---|
| 200 | OK |
| 201 | Created (register, place order, create menu item) |
| 204 | Success, no body (logout, soft delete) |
| 400 | Request body failed validation → `fieldErrors` populated |
| 401 | Not logged in |
| 403 | Logged in, but not allowed to touch this resource (ownership/role) |
| 404 | Resource does not exist (or is soft-deleted) |
| 409 | Business-rule conflict — the interesting one; see the error-code catalogue |
| 500 | Unhandled — must never be reachable through normal use |
