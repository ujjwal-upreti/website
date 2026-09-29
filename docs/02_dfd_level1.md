# Level-1 Data Flow Diagram – Shoe Store System

> Mapped 1:1 from the uploaded "SHOE STORE SYSTEM – LEVEL 1 DFD".

## External Entities
- Customer
- Shopkeeper
- Admin
- Staff (managed by Admin – Staff has no admin rights)

## Processes

| ID  | Process Name               | Description |
|-----|----------------------------|-------------|
| 1.0 | Authentication & Profile   | Login, register, update credentials / profile |
| 2.0 | Browse & Search Shoes      | Search, filter, view product data & stock |
| 3.0 | Shopping Cart Management   | Add / update / remove cart items |
| 4.0 | Order Processing           | Place order, create order records |
| 5.0 | Payment & Invoicing        | Process payment, generate invoices |
| 6.0 | Product & Stock Management | CRUD products, manage stock levels |
| 7.0 | User / Customer Admin      | Manage users, staff, customers |
| 8.0 | Sales Reporting            | Generate sales reports & logs |

## Data Stores

| ID  | Name               | Description |
|-----|--------------------|-------------|
| D1  | Users              | Credentials & profiles of all roles |
| D2  | Products & Stock   | Shoe catalog + current stock |
| D3  | Cart               | Temporary shopping cart |
| D4  | Orders             | Confirmed order records |
| D5  | Payments & Invoices| Payment transactions + invoices |
| D6  | Sales Log          | Historical sales data for reporting |

## Key Data Flows (from diagram)

- Customer ↔ 1.0 : credentials / profile
- Customer → 2.0 : product data, search / results
- Customer → 3.0 : add to cart / update cart
- Customer → 4.0 : place order
- Customer → 5.0 : pay
- Shopkeeper → 6.0 : manage products / add stock
- Admin → 7.0 : manage users / staff
- 4.0 → 5.0 : order records
- 5.0 → 8.0 / D6 : sales data
- Staff ↔ 6.0, 7.0, 8.0 (limited)

## Notes
- Process 8.0 appears on both sides of the original diagram – treated as one logical process.
- All data stores support read + write where appropriate.
