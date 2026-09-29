from datetime import datetime
from backend.extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", backref="brand", lazy="dynamic")

    def __repr__(self):
        return f"<Brand {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # Kept as an aggregate stock value for backwards compatibility.
    stock = db.Column(db.Integer, default=0, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"))
    # Legacy/default values retained for existing templates/data.
    size = db.Column(db.String(20), default="9")
    color = db.Column(db.String(40), default="Black")
    image_url = db.Column(db.String(255), default="/static/images/products/air-max-90.jpg")
    image_url_2 = db.Column(db.String(255))
    image_url_3 = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variants = db.relationship(
        "ProductVariant",
        backref="product",
        lazy="select",
        cascade="all, delete-orphan",
        order_by="ProductVariant.id",
    )
    cart_items = db.relationship("CartItem", backref="product", lazy="dynamic")
    order_items = db.relationship("OrderItem", backref="product", lazy="dynamic")
    wishlists = db.relationship("Wishlist", backref="product", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def available_sizes(self):
        values = [v.size for v in self.variants if v.stock > 0]
        return sorted(set(values), key=lambda value: float(value) if str(value).replace('.', '', 1).isdigit() else str(value))

    @property
    def available_colors(self):
        return sorted({v.color for v in self.variants if v.stock > 0})

    def is_in_stock(self, qty=1):
        return self.stock >= qty and self.is_active

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(40), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("product_id", "size", "color", name="uq_product_variant"),
    )

    def is_in_stock(self, qty=1):
        return self.stock >= qty and self.product.is_active

    def __repr__(self):
        return f"<ProductVariant {self.product_id} {self.size}/{self.color}>"


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", name="uq_user_wishlist_product"),
    )

    def __repr__(self):
        return f"<Wishlist user={self.user_id} product={self.product_id}>"
