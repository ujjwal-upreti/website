# System Design – Sneaker E-Commerce

## High-Level Architecture

```
Browser (Bootstrap + Jinja2)
        │  HTTP
        ▼
Flask Application (Blueprints)
        │
SQLAlchemy ORM
        │
SQLite / PostgreSQL
```

**Style**: Modular Monolith – ideal for undergrad projects. Easy to later extract microservices.

## Components mapped to DFD

| DFD Process | Component              | Responsibility |
|-------------|------------------------|----------------|
| 1.0         | Auth Module            | Login, register, profile, sessions |
| 2.0         | Product Catalog        | Search, filter (brand, size, category) |
| 3.0         | Cart Service           | Session + DB cart |
| 4.0 + 5.0   | Order & Payment Engine | Place order, stock check, payment sim, invoice |
| 6.0         | Inventory Module       | Product CRUD + stock |
| 7.0         | User Admin             | Manage users & staff |
| 8.0         | Reporting Engine       | Daily sales, revenue |

## Role-Based Access Control

```
customer   → view shoes, cart, place order, own profile
shopkeeper → + manage stock, view sales reports
staff      → + manage products, payments, customers
admin      → * (everything)
```

## Key Design Decisions
1. Monolith first – faster delivery for academic deadline
2. SQLite for zero-config development
3. Server-side rendering – simple auth & CSRF
4. Soft deletes via `is_active`
5. Stock decremented only after successful payment
6. Optimistic locking on stock at checkout

## Non-Functional Targets
- Page load < 300 ms (catalog)
- CSRF + hashed passwords + role decorators
- Clear Blueprint separation for maintainability
