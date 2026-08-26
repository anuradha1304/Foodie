# 02 — Data Model

Database: `food_ordering_dev` · Engine: InnoDB · Charset: `utf8mb4` · Collation: `utf8mb4_unicode_ci`

## 1. Entity relationship overview

```
User (1) ──owns──> (0..1) Restaurant
User (1) ──has───> (0..1) Cart
User (1) ──places─> (0..*) Order

Restaurant (1) ──has──> (0..*) MenuItem
Restaurant (1) ──receives──> (0..*) Order

Cart (1) ──has──> (0..*) CartItem ──refers──> (1) MenuItem

Order (1) ──has──> (1..*) OrderItem ──snapshots──> (1) MenuItem
Order (1) ──has──> (1..*) OrderStatusHistory
```

## 2. Enums

```java
public enum Role { CUSTOMER, RESTAURANT_ADMIN }

public enum OrderStatus {
    PLACED, ACCEPTED, REJECTED, PREPARING, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
}
```

Persist enums as `@Enumerated(EnumType.STRING)`. **Never** `ORDINAL`.

## 3. Entities

### 3.1 `users`

| Column | Type | Constraints | JPA notes |
|---|---|---|---|
| `id` | BIGINT | PK, AUTO_INCREMENT | `@Id @GeneratedValue(IDENTITY)` |
| `full_name` | VARCHAR(120) | NOT NULL | |
| `email` | VARCHAR(180) | NOT NULL, UNIQUE | index `uk_users_email` |
| `password_hash` | VARCHAR(100) | NOT NULL | BCrypt, `@JsonIgnore` |
| `phone` | VARCHAR(20) | NOT NULL | |
| `role` | VARCHAR(30) | NOT NULL | `@Enumerated(STRING)` |
| `enabled` | BOOLEAN | NOT NULL DEFAULT TRUE | |
| `created_at` | DATETIME(6) | NOT NULL | `@CreationTimestamp` |

Table name is `users`, not `user` — `USER` is reserved in MySQL 8.

### 3.2 `restaurants`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK, AUTO_INCREMENT |
| `name` | VARCHAR(150) | NOT NULL |
| `description` | VARCHAR(500) | NULL |
| `cuisine_type` | VARCHAR(60) | NOT NULL, indexed |
| `address` | VARCHAR(300) | NOT NULL |
| `phone` | VARCHAR(20) | NOT NULL |
| `image_url` | VARCHAR(500) | NULL |
| `is_open` | BOOLEAN | NOT NULL DEFAULT TRUE |
| `owner_id` | BIGINT | NOT NULL, FK → `users(id)`, UNIQUE |
| `created_at` | DATETIME(6) | NOT NULL |

`owner_id` is UNIQUE → one admin owns exactly one restaurant.
Mapping: `@OneToOne(fetch = LAZY) @JoinColumn(name = "owner_id")`.

### 3.3 `menu_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK, AUTO_INCREMENT |
| `restaurant_id` | BIGINT | NOT NULL, FK → `restaurants(id)`, indexed |
| `name` | VARCHAR(150) | NOT NULL |
| `description` | VARCHAR(500) | NULL |
| `category` | VARCHAR(60) | NOT NULL (e.g. Starters, Main Course, Breads, Desserts, Beverages) |
| `price` | DECIMAL(10,2) | NOT NULL, CHECK > 0 |
| `image_url` | VARCHAR(500) | NULL |
| `is_available` | BOOLEAN | NOT NULL DEFAULT TRUE |
| `is_deleted` | BOOLEAN | NOT NULL DEFAULT FALSE |
| `version` | BIGINT | NOT NULL DEFAULT 0 — `@Version` |
| `created_at` | DATETIME(6) | NOT NULL |
| `updated_at` | DATETIME(6) | NOT NULL — `@UpdateTimestamp` |

Composite index `idx_menu_restaurant_avail (restaurant_id, is_available, is_deleted)`.
All queries filter `is_deleted = false`.

### 3.4 `carts`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK |
| `user_id` | BIGINT | NOT NULL, FK → `users(id)`, UNIQUE |
| `restaurant_id` | BIGINT | NULL, FK → `restaurants(id)` |
| `updated_at` | DATETIME(6) | NOT NULL |

`restaurant_id` is NULL when the cart is empty; it is set by the first added item and
enforces the single-restaurant rule (FR-C2).

### 3.5 `cart_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK |
| `cart_id` | BIGINT | NOT NULL, FK → `carts(id)` ON DELETE CASCADE |
| `menu_item_id` | BIGINT | NOT NULL, FK → `menu_items(id)` |
| `quantity` | INT | NOT NULL, CHECK BETWEEN 1 AND 20 |

Unique constraint `uk_cart_item (cart_id, menu_item_id)` — adding an existing item
increments quantity rather than inserting a duplicate row.

Mapping on `Cart`: `@OneToMany(mappedBy="cart", cascade=ALL, orphanRemoval=true)`.

### 3.6 `orders`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK |
| `order_number` | VARCHAR(20) | NOT NULL, UNIQUE (format `ORD-yyyyMMdd-XXXXXX`) |
| `customer_id` | BIGINT | NOT NULL, FK → `users(id)`, indexed |
| `restaurant_id` | BIGINT | NOT NULL, FK → `restaurants(id)`, indexed |
| `status` | VARCHAR(30) | NOT NULL, indexed |
| `subtotal` | DECIMAL(10,2) | NOT NULL |
| `delivery_fee` | DECIMAL(10,2) | NOT NULL |
| `total_amount` | DECIMAL(10,2) | NOT NULL |
| `delivery_address` | VARCHAR(300) | NOT NULL |
| `customer_note` | VARCHAR(500) | NULL |
| `rejection_reason` | VARCHAR(300) | NULL |
| `idempotency_key` | VARCHAR(64) | NULL, UNIQUE |
| `version` | BIGINT | NOT NULL DEFAULT 0 — `@Version` |
| `placed_at` | DATETIME(6) | NOT NULL |
| `updated_at` | DATETIME(6) | NOT NULL |

Composite index `idx_orders_restaurant_status (restaurant_id, status, placed_at DESC)`.
`idempotency_key` UNIQUE is the DB-level guard for FR-D5 (double submit).

### 3.7 `order_items`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK |
| `order_id` | BIGINT | NOT NULL, FK → `orders(id)` ON DELETE CASCADE |
| `menu_item_id` | BIGINT | NOT NULL, FK → `menu_items(id)` |
| `item_name` | VARCHAR(150) | NOT NULL — **snapshot** |
| `unit_price` | DECIMAL(10,2) | NOT NULL — **snapshot** |
| `quantity` | INT | NOT NULL |
| `line_total` | DECIMAL(10,2) | NOT NULL = `unit_price * quantity` |

The snapshot columns are the whole point of this table (FR-D4). Do not resolve name/price
through the `MenuItem` association at read time.

### 3.8 `order_status_history`

| Column | Type | Constraints |
|---|---|---|
| `id` | BIGINT | PK |
| `order_id` | BIGINT | NOT NULL, FK → `orders(id)` ON DELETE CASCADE, indexed |
| `status` | VARCHAR(30) | NOT NULL |
| `note` | VARCHAR(300) | NULL |
| `changed_by_user_id` | BIGINT | NULL, FK → `users(id)` |
| `changed_at` | DATETIME(6) | NOT NULL |

One row is written on order creation (`PLACED`) and on every subsequent transition.

## 4. Canonical DDL

Hibernate generates the schema with `ddl-auto=update`. After the entities are written, run
this verification query through the **mysql** MCP server and compare against §3:

```sql
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'food_ordering_dev'
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

Any mismatch → fix the entity annotation, not the database.

## 5. Seed data

Place in `src/main/resources/data.sql`, guarded so it runs only on an empty DB.
Required seed volume:

- 2 restaurant admin users + 1 customer user (password for all: `Password123`, BCrypt-hashed)
- 2 restaurants (e.g. one North Indian, one Italian), both open
- 12 menu items minimum, spread across ≥ 3 categories per restaurant
- 2 items deliberately set `is_available = false` to exercise FR-B4 and FR-D2

Do not seed carts or orders — those must be created through the UI during verification.

## 6. Repository interfaces required

```
UserRepository            : findByEmail, existsByEmail
RestaurantRepository      : findByIsOpenTrue, findByOwnerId,
                            search(name, cuisine) via @Query
MenuItemRepository        : findByRestaurantIdAndIsDeletedFalse,
                            findAllByIdInAndIsDeletedFalse,
                            findByIdForUpdate (PESSIMISTIC_WRITE, see 03 §5)
CartRepository            : findByUserId (with @EntityGraph on items)
CartItemRepository        : findByCartIdAndMenuItemId, deleteByCartId
OrderRepository           : findByOrderNumber, findByCustomerIdOrderByPlacedAtDesc (Pageable),
                            findByRestaurantIdAndStatus (Pageable),
                            findByIdemponencyKey, findWithItemsById (@EntityGraph)
OrderStatusHistoryRepository : findByOrderIdOrderByChangedAtAsc
```
