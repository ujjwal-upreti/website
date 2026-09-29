# Use Case Diagram – Sneaker E-Commerce System

> Directly adapted from the uploaded "Sneaker E-Commerce System" Use Case Diagram.

## Actors

| Actor       | Description                                      | Rights |
|-------------|--------------------------------------------------|--------|
| Customer    | End user who browses, carts and purchases shoes  | Low    |
| Shopkeeper  | Manages products/stock and views daily sales     | Medium |
| Staff       | Handles products, payments, customers            | Medium |
| Admin       | Full system control + user/staff management      | High   |

## Use Cases (exactly as diagram)

### Customer
- View shoes
- Add to cart
- Place order  `<<include>>`  Make payment  `<<include>>`  Generate invoice
- Authentication (login/logout)
- Manage My Profile (Profile & Password)

### Shopkeeper
- Check daily sales report
- Add stock
- Authentication
- Manage My Profile

### Staff
- Manage product
- Manage payment
- Manage customer
- Authentication
- Manage My Profile

### Admin
- Manage users and full application
- Manage shopping cart
- Manage order
- (inherits all Staff capabilities)

## Relationships

```
Customer ----> View shoes
Customer ----> Add to cart
Customer ----> Place order  <<include>>  Make payment  <<include>>  Generate invoice
Customer ----> Authentication
Customer ----> Manage My Profile

Shopkeeper --> Check daily sales report
Shopkeeper --> Add stock
Shopkeeper --> Authentication / Profile

Staff -------> Manage product / payment / customer
Staff -------> Authentication / Profile

Admin -------> Manage users and full application
Admin -------> Manage shopping cart / Manage order
```

## Implementation Notes
- Place Order **includes** Make Payment
- Make Payment **includes** Generate Invoice
- Staff has **no** full admin rights (cannot manage other admins)
- Authentication is shared across all actors
