# Database Schema – Sneaker Store

## ER Overview

```
User (1) ──< (N) Order
User (1) ──< (N) CartItem
Product (1) ─< (N) CartItem
Product (1) ─< (N) OrderItem
Order (1) ───< (N) OrderItem
Order (1) ─── (1) Payment
Order (1) ─── (1) Invoice
Category (1) ─< (N) Product
Brand (1) ───< (N) Product
```

## Tables

### users (D1)
| Column        | Type         | Notes |
|---------------|--------------|-------|
| id            | Integer PK   | |
| email         | String(120)  | Unique |
| password_hash | String(256)  | Werkzeug |
| full_name     | String(100)  | |
| role          | String(20)   | customer / shopkeeper / staff / admin |
| phone         | String(20)   | |
| address       | Text         | |
| is_active     | Boolean      | Soft delete |
| created_at    | DateTime     | |

### categories
| id | name | slug | description |

### brands
| id | name | slug |

### products (D2)
| Column      | Type          | Notes |
|-------------|---------------|-------|
| id          | Integer PK    | |
| name        | String(150)   | |
| slug        | String(160)   | Unique |
| description | Text          | |
| price       | Numeric(10,2) | |
| stock       | Integer       | |
| category_id | FK            | |
| brand_id    | FK            | |
| size        | String(20)    | e.g. 8, 9, 10, 42 |
| color       | String(40)    | |
| image_url   | String(255)   | |
| is_active   | Boolean       | |
| created_at  | DateTime      | |

### cart_items (D3)
| id | user_id (nullable) | session_id | product_id | quantity |

### orders (D4)
| id | order_number | user_id | status | total_amount | shipping_address | created_at |

### order_items
| id | order_id | product_id | quantity | unit_price | subtotal |

### payments (D5)
| id | order_id | amount | method | status | transaction_id | paid_at |

### invoices (D5)
| id | order_id | invoice_number | issued_at | pdf_path |

### sales_logs (D6)
| id | order_id | product_id | quantity | amount | sold_at |

## Indexes
- users.email (unique)
- products.slug, products.brand_id, products.category_id
- orders.user_id, orders.status, orders.created_at
