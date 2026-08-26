# Online Food Ordering System — Documentation Index

Read these in order before starting work.

| # | Document | What it defines |
|---|---|---|
| — | `../AGENTS.md` | Hard rules. Applies to every task. Read first. |
| 01 | `01-requirements.md` | Scope, actors, functional + non-functional requirements, user flows |
| 02 | `02-data-model.md` | Entities, relationships, constraints, canonical DDL, seed data |
| 03 | `03-architecture.md` | Package layout, layering, concurrency design, transaction boundaries |
| 04 | `04-api-contract.md` | Every REST endpoint: method, path, auth, request, response, errors |
| 05 | `05-frontend-spec.md` | Pages, DOM structure, AJAX call map, state handling |
| 06 | `06-build-plan.md` | Milestones M0–M8 with exact task prompts and acceptance criteria |
| 07 | `07-verification.md` | Test scenarios the build must pass before it is considered done |

## Project identity

- **Artifact name:** `food-ordering-system`
- **Group ID:** `com.foodapp`
- **Base package:** `com.foodapp`
- **DB name:** `food_ordering_dev`
- **Port:** 8080

## One-line summary

A Spring Boot 3 monolith exposing a JSON REST API, consumed by a static HTML/CSS/vanilla-JS
frontend via AJAX, persisting to MySQL 8 through Hibernate/JPA, with role-based access for
two actors: `CUSTOMER` and `RESTAURANT_ADMIN`.
