# Architecture

## Layered View
```
Presentation (templates + static)
Application (Flask Blueprints)
Data Access (SQLAlchemy models)
Database (SQLite / PostgreSQL)
```

## Blueprint ↔ DFD Mapping
```
routes/auth.py      → 1.0
routes/products.py  → 2.0
routes/cart.py      → 3.0
routes/orders.py    → 4.0 + 5.0
routes/admin.py     → 6.0 + 7.0 + 8.0
routes/main.py      → Home / About
```

## Security
- Werkzeug password hashing
- Flask-Login sessions
- `@role_required` decorator
- CSRF on all forms
- Soft deletes

## Future Path
1. Extract pure REST API
2. React / Next.js frontend
3. Redis for cart
4. Docker + Gunicorn + Nginx
5. Real payment gateway (Stripe)
