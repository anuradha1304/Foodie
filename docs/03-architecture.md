# 03 — Architecture

## 1. Package layout

```
com.foodapp
├── FoodOrderingApplication.java
├── config
│   ├── SecurityConfig.java          # SecurityFilterChain, PasswordEncoder
│   ├── AsyncConfig.java             # @EnableAsync + ThreadPoolTaskExecutor bean
│   ├── AppProperties.java           # @ConfigurationProperties("app")
│   └── WebConfig.java               # static resource + CORS (dev only)
├── domain                           # JPA entities + enums only. No logic beyond invariants.
│   ├── User.java  Restaurant.java  MenuItem.java
│   ├── Cart.java  CartItem.java
│   ├── Order.java OrderItem.java OrderStatusHistory.java
│   └── enums/ Role.java OrderStatus.java
├── repository                       # Spring Data JPA interfaces
├── dto
│   ├── request/                     # records, jakarta.validation annotated
│   └── response/                    # records
├── mapper                           # entity → DTO static mappers
├── service
│   ├── AuthService.java
│   ├── RestaurantService.java
│   ├── MenuService.java
│   ├── CartService.java
│   ├── OrderService.java            # placement — the critical transaction
│   ├── OrderStatusService.java      # transitions + history
│   └── NotificationService.java     # @Async side effects
├── controller
│   ├── AuthController.java          /api/auth/**
│   ├── RestaurantController.java    /api/restaurants/**
│   ├── CartController.java          /api/cart/**
│   ├── OrderController.java         /api/orders/**
│   └── admin/ AdminMenuController.java, AdminOrderController.java
├── exception
│   ├── ApiException.java (base) + NotFoundException, ForbiddenException,
│   │   ConflictException, ValidationException
│   └── GlobalExceptionHandler.java  # @RestControllerAdvice
└── security
    ├── AppUserDetailsService.java
    └── SecurityUtils.java           # currentUserId() helper
```

## 2. Layering rules

```
Browser ──HTTP/JSON──> Controller ──> Service ──> Repository ──> Hibernate ──> MySQL
```

- A controller may call **only** services. Never a repository directly.
- A service may call repositories and other services.
- A repository is never injected outside `service`.
- Transactions begin and end **in the service layer**. Never `@Transactional` on a controller.
- Entities never leave the service layer. Services return DTOs.

## 3. Dependency injection (project requirement NFR-6)

Constructor injection everywhere, with `final` fields:

```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final CartService cartService;
    private final NotificationService notificationService;

    public OrderService(OrderRepository orderRepository,
                        CartService cartService,
                        NotificationService notificationService) {
        this.orderRepository = orderRepository;
        this.cartService = cartService;
        this.notificationService = notificationService;
    }
}
```

Lombok `@RequiredArgsConstructor` is acceptable as a shorthand for the same thing.

## 4. Transaction boundaries

| Operation | Boundary | Isolation |
|---|---|---|
| Register user | `@Transactional` | default |
| Add/update/remove cart item | `@Transactional` | default |
| **Place order** | `@Transactional` — the single most important boundary | `READ_COMMITTED` |
| Update order status | `@Transactional` | default |
| All list/read endpoints | `@Transactional(readOnly = true)` | default |

Order placement must do all of the following **inside one transaction**, and roll back
entirely if any step fails:

1. Load and lock the cart's menu items
2. Re-validate availability, restaurant-open, and prices
3. Create `Order` + `OrderItem` snapshot rows
4. Write the initial `OrderStatusHistory` row (`PLACED`)
5. Clear the cart

The async notification (step 6) fires **after commit**, not inside the transaction.

## 5. Concurrency design (project requirement NFR-1 — graded, do this carefully)

Three distinct concurrency problems. Solve each with the named mechanism.

### 5.1 Two customers ordering the same item as it goes unavailable

**Mechanism: pessimistic write lock on the menu items being ordered.**

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select m from MenuItem m where m.id in :ids and m.isDeleted = false")
List<MenuItem> lockAllByIds(@Param("ids") List<Long> ids);
```

Call this at the start of `placeOrder`, **sorted by id ascending** to prevent deadlock between
two transactions locking the same set in different orders. Then validate `isAvailable` and
that `price` still equals what the cart quoted.

### 5.2 Two restaurant admins updating the same order's status simultaneously

**Mechanism: optimistic locking via `@Version` on `Order`.**

The second commit throws `OptimisticLockingFailureException`. Catch it in
`GlobalExceptionHandler` and return HTTP 409 `CONCURRENT_MODIFICATION`. Do **not** retry
silently — the admin must re-read and re-decide.

### 5.3 Same customer double-submitting the same order

**Mechanism: idempotency key + UNIQUE constraint.**

The client generates a UUID when the checkout page loads and sends it as the
`Idempotency-Key` header. `placeOrder` first checks `findByIdempotencyKey`; if present it
returns the existing order. The UNIQUE index on `orders.idempotency_key` is the real
guarantee — catch `DataIntegrityViolationException` and return the existing order.

### 5.4 Async execution (NFR-2)

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    @Bean("taskExecutor")
    public ThreadPoolTaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor ex = new ThreadPoolTaskExecutor();
        ex.setCorePoolSize(4);
        ex.setMaxPoolSize(10);
        ex.setQueueCapacity(50);
        ex.setThreadNamePrefix("foodapp-async-");
        ex.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        ex.initialize();
        return ex;
    }
}
```

`NotificationService` methods are `@Async("taskExecutor")` and return `void` or
`CompletableFuture<Void>`. They log to console (no real email provider — out of scope).

Trigger them with `@TransactionalEventListener(phase = AFTER_COMMIT)` on an
`OrderPlacedEvent` / `OrderStatusChangedEvent`, so a notification never fires for a
rolled-back order. **Never** call an `@Async` method from inside the same class — the proxy
will be bypassed and it will run synchronously.

### 5.5 Concurrency demonstration test (required deliverable)

Write `OrderConcurrencyTest` that spawns 20 threads via `ExecutorService` all attempting to
place an order for the same last-available item, and asserts that exactly the expected number
succeed and the rest fail with `ConflictException`. Use a `CountDownLatch` so all threads
start simultaneously. This test is the evidence that NFR-1 is satisfied.

## 6. Security configuration

Spring Security 6 style — `SecurityFilterChain` bean, no `WebSecurityConfigurerAdapter`.

| Path pattern | Access |
|---|---|
| `/`, `/*.html`, `/css/**`, `/js/**`, `/images/**` | permitAll |
| `POST /api/auth/register`, `POST /api/auth/login` | permitAll |
| `GET /api/restaurants/**` | permitAll |
| `/api/cart/**`, `/api/orders/**` | `hasRole('CUSTOMER')` |
| `/api/admin/**` | `hasRole('RESTAURANT_ADMIN')` |
| everything else | authenticated |

- Session-based auth (`SessionCreationPolicy.IF_REQUIRED`), `JSESSIONID` cookie, `HttpOnly`.
- CSRF: enable with `CookieCsrfTokenRepository.withHttpOnlyFalse()` and have `js/api.js` read
  the `XSRF-TOKEN` cookie and send it as the `X-XSRF-TOKEN` header on every mutating request.
- Return **401 JSON** (not a login-page redirect) on unauthenticated API calls — configure a
  custom `AuthenticationEntryPoint`. A redirect breaks AJAX.
- `@PreAuthorize` on admin service methods as defence in depth, with `@EnableMethodSecurity`.
- **Ownership checks are separate from role checks.** Having `ROLE_RESTAURANT_ADMIN` does not
  mean you own restaurant #2. Every admin service method must verify
  `restaurant.getOwner().getId().equals(currentUserId())`.

## 7. Error response format

Every error returns this shape, produced by `GlobalExceptionHandler`:

```json
{
  "timestamp": "2026-08-25T10:15:30",
  "status": 409,
  "code": "ITEM_UNAVAILABLE",
  "message": "Paneer Tikka is no longer available",
  "fieldErrors": { "quantity": "must be between 1 and 20" }
}
```

`fieldErrors` is present only for validation failures (400).

**Error code catalogue:** `VALIDATION_FAILED`, `EMAIL_ALREADY_EXISTS`, `BAD_CREDENTIALS`,
`UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `CART_EMPTY`, `CART_RESTAURANT_MISMATCH`,
`RESTAURANT_CLOSED`, `ITEM_UNAVAILABLE`, `PRICE_CHANGED`, `INVALID_STATUS_TRANSITION`,
`CONCURRENT_MODIFICATION`, `INTERNAL_ERROR`.

## 8. Configuration (`application.yml`)

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/food_ordering_dev?useSSL=false&serverTimezone=Asia/Kolkata
    username: ${DB_USER:foodapp}
    password: ${DB_PASSWORD}
  jpa:
    hibernate.ddl-auto: update
    open-in-view: false          # MANDATORY — force explicit fetching
    properties:
      hibernate.dialect: org.hibernate.dialect.MySQLDialect
      hibernate.format_sql: true
      hibernate.jdbc.batch_size: 20
  sql.init.mode: always
logging.level.org.hibernate.SQL: DEBUG
app:
  order:
    delivery-fee: 40.00
    free-delivery-threshold: 500.00
    page-size: 10
  cart:
    max-quantity: 20
```

`open-in-view: false` is non-negotiable — it forces you to fetch associations explicitly and
surfaces N+1 problems at development time instead of hiding them.

## 9. Maven dependencies (NFR-7)

Parent: `spring-boot-starter-parent:3.3.x`. Required starters:

`spring-boot-starter-web`, `spring-boot-starter-data-jpa`,
`spring-boot-starter-security`, `spring-boot-starter-validation`,
`mysql-connector-j` (runtime), `spring-boot-starter-test` (test),
`spring-security-test` (test), `h2` (test scope, for fast slice tests),
`lombok` (optional, provided).
