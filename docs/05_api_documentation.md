# API Documentation – Sneaker E-Commerce

Base: `http://127.0.0.1:5000`

(Server-rendered forms are primary; the same routes can be extended to pure JSON later.)

## Auth
- `POST /auth/register` – new customer
- `POST /auth/login`
- `POST /auth/logout`
- `GET/POST /auth/profile`

## Products (Process 2.0)
- `GET /products/` – list + search + filters (brand, category, size)
- `GET /products/<slug>` – detail

## Cart (Process 3.0)
- `GET /cart/`
- `POST /cart/add/<product_id>`
- `POST /cart/update/<item_id>`
- `POST /cart/remove/<item_id>`

## Orders & Payment (4.0 + 5.0)
- `GET/POST /orders/checkout`
- `GET /orders/` – own / all (staff)
- `GET /orders/<id>`

## Admin (6.0, 7.0, 8.0)
- `GET /admin/` – dashboard + sales report
- `GET/POST /admin/products` – manage stock
- `GET /admin/users` – Admin only
- `GET /admin/orders` + status update

## Response Style
Success flashes + redirects (classic Flask).  
JSON endpoints can be added later under `/api/v1/`.
