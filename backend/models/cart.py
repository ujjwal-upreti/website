from datetime import datetime
from backend.extensions import db


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.String(64), nullable=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variant = db.relationship("ProductVariant", backref="cart_items")

    __table_args__ = (
        db.UniqueConstraint("user_id", "product_id", "variant_id", name="uq_user_product_variant"),
    )

    def subtotal(self):
        return self.product.price * self.quantity

    def __repr__(self):
        return f"<CartItem product={self.product_id} variant={self.variant_id} qty={self.quantity}>"
