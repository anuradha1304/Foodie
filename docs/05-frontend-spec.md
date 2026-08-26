# 05 — Frontend Specification

No framework, no build step. Static files served by Spring Boot from
`src/main/resources/static/`.

## 1. File layout

```
static/
├── index.html                  # restaurant listing (landing page)
├── login.html
├── register.html
├── menu.html                   # ?restaurantId=1
├── cart.html
├── checkout.html
├── order-confirmation.html     # ?orderNumber=ORD-...
├── order-tracking.html         # ?orderId=21
├── order-history.html
├── admin/
│   ├── dashboard.html          # incoming orders queue
│   ├── menu.html               # menu item CRUD
│   └── order-detail.html       # ?orderId=21
├── css/
│   ├── base.css                # reset, variables, typography, buttons, layout
│   └── components.css          # cards, modal, toast, badges, tables
└── js/
    ├── api.js                  # fetch wrapper — ALL network calls go through this
    ├── auth.js                 # session state, nav rendering, route guards
    ├── ui.js                   # toast, modal, spinner, money formatter
    ├── restaurants.js
    ├── menu.js
    ├── cart.js
    ├── checkout.js
    ├── tracking.js
    ├── history.js
    └── admin/ dashboard.js, menu-admin.js
```

## 2. `js/api.js` — the required shared wrapper

Every network call in the app goes through this. No `fetch(` anywhere else.

```js
const BASE = '';

function csrfToken() {
  return document.cookie.split('; ')
    .find(c => c.startsWith('XSRF-TOKEN='))?.split('=')[1];
}

async function request(method, path, body, extraHeaders = {}) {
  const headers = { 'Accept': 'application/json', ...extraHeaders };
  if (body) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') headers['X-XSRF-TOKEN'] = decodeURIComponent(csrfToken() ?? '');

  const res = await fetch(BASE + path, {
    method, headers,
    credentials: 'same-origin',
    body: body ? JSON.stringify(body) : undefined
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401) { window.location.href = '/login.html'; return; }
    throw new ApiError(data?.code ?? 'INTERNAL_ERROR',
                       data?.message ?? 'Something went wrong',
                       data?.fieldErrors, res.status);
  }
  return data;
}

export const api = {
  get:  (p)       => request('GET', p),
  post: (p, b, h) => request('POST', p, b, h),
  put:  (p, b)    => request('PUT', p, b),
  patch:(p, b)    => request('PATCH', p, b),
  del:  (p)       => request('DELETE', p)
};
```

`ApiError` carries `code`, so callers switch on the error-code catalogue rather than parsing
message strings.

## 3. Page specifications

### `index.html` — restaurant listing
- Header with search input, cuisine `<select>`, "open only" checkbox.
- Debounced (300 ms) search → `GET /api/restaurants?search=&cuisine=&openOnly=`.
- Grid of restaurant cards: image, name, cuisine, item count, OPEN/CLOSED badge.
- Card click → `menu.html?restaurantId={id}`.
- Empty state when no results. Skeleton loaders while fetching.

### `menu.html` — menu + add to cart (**core AJAX page**)
- On load: `GET /api/restaurants/{id}` and `GET /api/restaurants/{id}/menu` in parallel via
  `Promise.all`.
- Render category sections with a sticky category nav.
- Each item card has a quantity stepper and an **Add to Cart** button.
- Clicking Add:
  1. disable the button, show inline spinner
  2. `POST /api/cart/items`
  3. on success → update the header cart badge from the returned `itemCount`, show a success
     toast, re-enable the button
  4. on `CART_RESTAURANT_MISMATCH` → open a confirm modal: "Your cart has items from
     {other}. Clear it and add this instead?" → `DELETE /api/cart` then retry the POST
  5. on `ITEM_UNAVAILABLE` → error toast, mark the card disabled in place
- **No page reload at any point.** This page is what demonstrates the AJAX requirement.
- Unavailable items render greyed with a "Currently unavailable" ribbon, button removed.

### `cart.html`
- `GET /api/cart` on load.
- Each line has −/+ steppers → `PUT /api/cart/items/{id}` on change (debounced 400 ms so
  rapid clicking sends one request), remove button → `DELETE`.
- Re-render totals from the returned `CartResponse` after every mutation. Never compute money
  in JS — only format it.
- "Clear cart" with a confirm modal. "Proceed to checkout" → `checkout.html`, disabled when
  the cart is empty.

### `checkout.html`
- Order summary (read-only) + delivery address textarea + optional note.
- **Generate a UUID once on page load**, store it in a module variable, and send it as the
  `Idempotency-Key` header. Do not regenerate it on retry — that is the whole point.
- `POST /api/orders` on submit. Disable the button for the duration of the request.
- Success → redirect to `order-confirmation.html?orderNumber=...`.
- `409` → show the specific message and a link back to the cart.

### `order-confirmation.html`
- Order number, item list, total, ETA text, buttons: "Track order", "Order again".

### `order-tracking.html`
- Horizontal stepper: Placed → Accepted → Preparing → Out for delivery → Delivered.
- `GET /api/orders/{id}/status` immediately, then `setInterval` every **5000 ms**.
- **Clear the interval** on terminal status (`DELIVERED`, `REJECTED`, `CANCELLED`) and in
  `beforeunload`. A leaked interval is a bug.
- Also stop polling when `document.hidden` is true; resume on `visibilitychange`.
- "Cancel order" button visible only while status is `PLACED`.
- Rejected orders show the rejection reason prominently.

### `order-history.html`
- `GET /api/orders?page=&size=10`, rows with status colour badges, pagination controls.
- Row click → `order-tracking.html?orderId=`.

### `login.html` / `register.html`
- Client-side validation mirrors the server rules, but the server remains authoritative.
- Render `fieldErrors` from a 400 response next to the matching input.
- On login success: `CUSTOMER` → `index.html`, `RESTAURANT_ADMIN` → `admin/dashboard.html`.

### `admin/dashboard.html`
- Status filter tabs: New (`PLACED`) / Accepted / Preparing / Out for delivery / Completed.
- Order cards with customer name, items, total, elapsed time since placed.
- `PLACED` cards show **Accept** and **Reject** buttons; Reject opens a reason modal.
- Other statuses show a single "Advance to {next}" button driven by the transition table.
- Auto-refresh the `PLACED` queue every 15 s via AJAX.
- On `409 CONCURRENT_MODIFICATION`: toast "This order was just updated elsewhere",
  then refresh that card.
- Toggle for restaurant open/closed in the header.

### `admin/menu.html`
- Table of all menu items with inline availability toggle switches
  (`PATCH .../availability`, optimistic UI with rollback on failure).
- "Add item" opens a modal form; "Edit" reuses the same modal prefilled.
- Delete asks for confirmation and calls the soft-delete endpoint.

## 4. Shared UI behaviours

| Behaviour | Rule |
|---|---|
| Loading | Skeletons for lists, inline spinner inside the clicked button for actions |
| Errors | Toast top-right, red, auto-dismiss 4 s; validation errors inline under inputs |
| Success | Toast top-right, green, auto-dismiss 2.5 s |
| Money | One `formatMoney(value)` in `ui.js` → `₹1,234.00`. Used everywhere. |
| Empty states | Every list has an illustration + message + primary action |
| Auth guard | `auth.js` runs `GET /api/auth/me` on protected pages; redirects to login on 401 |
| Nav | Header renders differently for anonymous / customer / admin. Cart badge for customers. |

## 5. Styling direction

- CSS custom properties in `:root` for the palette. Warm food-app palette: a saturated
  accent (`--accent: #E23744`-family), neutral greys, one success green, one warning amber.
- System font stack. No web fonts.
- Mobile-first, breakpoints at 640 / 1024 px. CSS Grid for card grids, Flexbox for rows.
- 8 px spacing scale. `border-radius: 12px` on cards, `8px` on buttons.
- Buttons need visible `:hover`, `:active`, `:disabled` and `:focus-visible` states.
- Accessibility: semantic elements, `alt` on every image, labels tied to inputs,
  `aria-live="polite"` on the toast container, keyboard-operable modals with focus trap.
