# AGENTS.md — Rules of Engagement

You are building an **Online Food Ordering System**. Read `/docs/00-INDEX.md` first.
These rules apply to **every** task in this repo. Do not deviate without asking.

---

## 1. Stack — locked, do not substitute

| Layer | Technology | Version |
|---|---|---|
| Language | Java | 17 |
| Framework | Spring Boot | 3.3.x |
| Web | Spring MVC (REST) | bundled |
| Security | Spring Security | 6.x (bundled) |
| ORM | Hibernate via Spring Data JPA | 6.x (bundled) |
| DB | MySQL | 8.x |
| Build | Maven | 3.9+ |
| Frontend | Plain HTML5 + CSS3 + vanilla JS (`fetch` for AJAX) | — |
| Test | JUnit 5 + Spring Boot Test + Testcontainers (optional) | bundled |

**Forbidden:** React, Angular, Vue, Tailwind, TypeScript, Lombok-free code is NOT required
(Lombok IS allowed), JSP, Struts, XML-based Spring config, `WebSecurityConfigurerAdapter`
(removed in Spring Security 6), `WebMvcConfigurerAdapter`, `javax.*` imports (use `jakarta.*`).

## 2. Before writing Spring/Hibernate code

Call **context7** to fetch current Spring Boot 3.3 / Spring Security 6 / Hibernate 6 docs.
Your training data likely contains Spring Boot 2.x patterns that no longer compile.
Specifically verify before using: `SecurityFilterChain`, `PasswordEncoder` bean setup,
`@EnableMethodSecurity` (not `@EnableGlobalMethodSecurity`), `AuthenticationManager` wiring.

## 3. Database rules

- Use the **mysql** MCP server to inspect the live schema before and after every entity change.
- `spring.jpa.hibernate.ddl-auto=update` during development ONLY.
- The canonical schema is `/docs/02-data-model.md`. If Hibernate generates something
  different from that document, the **document wins** — fix the entity mapping.
- Never `DROP` a table. Never run `DELETE` without a `WHERE`.
- All money is `BigDecimal` with `columnDefinition = "DECIMAL(10,2)"`. Never `double` or `float`.

## 4. Code standards

- Constructor injection only. No `@Autowired` on fields.
- Controllers contain **zero** business logic — they validate input, call a service, map to DTO.
- Entities never cross the controller boundary. Always map to a DTO/record.
- Every service method that writes is `@Transactional`. Read-only methods are
  `@Transactional(readOnly = true)`.
- All `@ManyToOne` associations are `fetch = FetchType.LAZY`. No exceptions.
- Use `record` for DTOs.
- Custom exceptions + one `@RestControllerAdvice` global handler. No `try/catch` returning
  `ResponseEntity` inside controllers.
- Validate all request bodies with `jakarta.validation` annotations + `@Valid`.

## 5. Frontend rules

- No build step. Static files under `src/main/resources/static/`.
- All server calls use `fetch()` with `credentials: 'same-origin'`.
- Never full-page-reload for cart operations or order-status refresh — that defeats the
  AJAX requirement. Update the DOM in place.
- One shared `js/api.js` wrapping `fetch` with error handling. No duplicated fetch logic.

## 6. Definition of done for any task

A task is complete only when **all** of these hold:

1. `mvn clean compile` passes with zero errors.
2. `mvn test` passes.
3. The app starts: `mvn spring-boot:run` reaches "Started FoodOrderingApplication".
4. You verified the schema via the **mysql** MCP server.
5. For UI tasks: you drove the flow in the browser and it works end to end.
6. You produced a short summary of what changed and what you verified.

## 7. Working style

- Work **one milestone at a time** from `/docs/05-build-plan.md`. Do not jump ahead.
- Commit after each milestone with a conventional-commit message
  (`feat(order): add order placement with optimistic locking`).
- If a requirement in the docs is ambiguous, **ask** — do not invent a design.
- Do not add features that are not in `/docs/01-requirements.md`.
- Do not generate placeholder/mock data in service layer code. Seed via SQL only.

## 8. Never do

- Never hardcode DB credentials, secrets, or API keys in Java files. Use `application.yml`
  + environment variable placeholders.
- Never store passwords in plaintext. BCrypt only.
- Never expose `passwordHash` in any API response.
- Never let a customer read or mutate another customer's order.
- Never let a restaurant admin touch a restaurant they do not own.
