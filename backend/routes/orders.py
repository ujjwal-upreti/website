from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from backend.extensions import db
from backend.models import CartItem, Order, OrderItem, Payment, Invoice, SalesLog

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view_cart"))
    total = sum(item.subtotal() for item in items)

    if request.method == "POST":
        address = request.form.get("shipping_address", "").strip()
        method = request.form.get("payment_method", "card")
        if not address:
            flash("Shipping address is required.", "danger")
            return render_template("orders/checkout.html", items=items, total=total)

        for item in items:
            available = item.variant.stock if item.variant else item.product.stock
            if not item.product.is_active or available < item.quantity:
                flash(f"Insufficient stock for {item.product.name}.", "danger")
                return redirect(url_for("cart.view_cart"))

        order = Order(
            order_number=Order.generate_order_number(),
            user_id=current_user.id,
            status="pending",
            total_amount=total,
            shipping_address=address,
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
                subtotal=item.subtotal(),
                variant_id=item.variant_id,
            ))
            if item.variant:
                item.variant.stock -= item.quantity
            item.product.stock = max(0, item.product.stock - item.quantity)
            db.session.add(SalesLog(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                amount=item.subtotal(),
            ))

        payment = Payment(
            order_id=order.id,
            amount=total,
            method=method,
            status="success" if method != "cod" else "pending",
            transaction_id=f"TXN-{order.order_number}",
            paid_at=datetime.utcnow() if method != "cod" else None,
        )
        db.session.add(payment)
        if method != "cod":
            order.status = "paid"

        db.session.add(Invoice(
            order_id=order.id,
            invoice_number=Invoice.generate_invoice_number(),
        ))

        for item in items:
            db.session.delete(item)
        db.session.commit()
        flash(f"Order {order.order_number} placed successfully!", "success")
        return redirect(url_for("orders.detail", order_id=order.id))

    return render_template("orders/checkout.html", items=items, total=total)


@orders_bp.route("/")
@login_required
def list_orders():
    if current_user.is_staff_or_above():
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    if not current_user.is_staff_or_above() and order.user_id != current_user.id:
        abort(403)
    return render_template("orders/detail.html", order=order)
