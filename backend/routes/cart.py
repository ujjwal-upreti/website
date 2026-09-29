from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import current_user
from backend.extensions import db
from backend.models import CartItem, Product, ProductVariant
import uuid

cart_bp = Blueprint("cart", __name__)


def _get_session_id():
    if "cart_session_id" not in session:
        session["cart_session_id"] = str(uuid.uuid4())
    return session["cart_session_id"]


def _get_cart_items():
    if current_user.is_authenticated:
        return CartItem.query.filter_by(user_id=current_user.id).all()
    return CartItem.query.filter_by(session_id=_get_session_id()).all()


def _get_variant(product, size, color):
    if not size or not color:
        return None
    return ProductVariant.query.filter_by(
        product_id=product.id, size=size, color=color
    ).first()


@cart_bp.route("/")
def view_cart():
    items = _get_cart_items()
    total = sum(item.subtotal() for item in items)
    return render_template("cart/view.html", items=items, total=total)


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = request.form.get("quantity", 1, type=int) or 1
    size = request.form.get("size", "").strip()
    color = request.form.get("color", "").strip()

    variant = _get_variant(product, size, color)
    if product.variants:
        if not variant:
            flash("Please choose a size and color.", "warning")
            return redirect(request.referrer or url_for("products.detail", slug=product.slug))
        if not variant.is_in_stock(qty):
            flash("Not enough stock available for that size and color.", "warning")
            return redirect(request.referrer or url_for("products.detail", slug=product.slug))
    elif not product.is_in_stock(qty):
        flash("Not enough stock available.", "warning")
        return redirect(request.referrer or url_for("products.list_products"))

    if current_user.is_authenticated:
        item = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product_id, variant_id=variant.id if variant else None
        ).first()
        if item:
            if variant and item.quantity + qty > variant.stock:
                flash("Not enough stock available for that variant.", "warning")
                return redirect(request.referrer or url_for("cart.view_cart"))
            item.quantity += qty
        else:
            db.session.add(CartItem(
                user_id=current_user.id, product_id=product_id,
                variant_id=variant.id if variant else None, quantity=qty
            ))
    else:
        sid = _get_session_id()
        item = CartItem.query.filter_by(
            session_id=sid, product_id=product_id, variant_id=variant.id if variant else None
        ).first()
        if item:
            if variant and item.quantity + qty > variant.stock:
                flash("Not enough stock available for that variant.", "warning")
                return redirect(request.referrer or url_for("cart.view_cart"))
            item.quantity += qty
        else:
            db.session.add(CartItem(
                session_id=sid, product_id=product_id,
                variant_id=variant.id if variant else None, quantity=qty
            ))
    db.session.commit()
    flash(f"Added {product.name} to cart.", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))


@cart_bp.route("/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if current_user.is_authenticated:
        if item.user_id != current_user.id:
            abort(403)
    elif item.session_id != _get_session_id():
        abort(403)

    qty = request.form.get("quantity", 1, type=int)
    available = item.variant.stock if item.variant else item.product.stock
    if qty < 1:
        db.session.delete(item)
    else:
        if available < qty or not item.product.is_active:
            flash("Not enough stock.", "warning")
            return redirect(url_for("cart.view_cart"))
        item.quantity = qty
    db.session.commit()
    flash("Cart updated.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    item = CartItem.query.get_or_404(item_id)
    if current_user.is_authenticated:
        if item.user_id != current_user.id:
            abort(403)
    elif item.session_id != _get_session_id():
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash("Item removed.", "info")
    return redirect(url_for("cart.view_cart"))
