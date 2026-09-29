from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from backend.extensions import db
from backend.models import User, Product, ProductVariant, Category, Brand, Order, SalesLog
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def _variant_values(form, product=None):
    raw_sizes = form.get("sizes", "").strip()
    raw_colors = form.get("colors", "").strip()
    if not raw_sizes and product:
        raw_sizes = product.size or "9"
    if not raw_colors and product:
        raw_colors = product.color or "Black"
    sizes = [v.strip() for v in raw_sizes.split(",") if v.strip()]
    colors = [v.strip() for v in raw_colors.split(",") if v.strip()]
    default_stock = form.get("variant_stock", type=int)
    return sizes or ["9"], colors or ["Black"], max(0, default_stock if default_stock is not None else 0)


def _replace_variants(product, sizes, colors, stock_each):
    product.variants.clear()
    for size in sizes:
        for color in colors:
            product.variants.append(ProductVariant(size=size, color=color, stock=stock_each))
    product.size = sizes[0]
    product.color = colors[0]
    product.stock = sum(v.stock for v in product.variants)


@admin_bp.route("/")
@login_required
@role_required("admin", "staff", "shopkeeper")
def dashboard():
    total_products = Product.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    total_users = User.query.filter_by(role="customer").count()
    revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.status.in_(["paid", "shipped", "delivered"])
    ).scalar() or 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    today = datetime.utcnow().date()
    daily = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        amount = db.session.query(func.sum(SalesLog.amount)).filter(
            func.date(SalesLog.sold_at) == day
        ).scalar() or 0
        daily.append({"date": day.strftime("%Y-%m-%d"), "amount": float(amount)})

    return render_template("admin/dashboard.html", total_products=total_products,
        total_orders=total_orders, total_users=total_users, revenue=revenue,
        recent_orders=recent_orders, daily=daily)


@admin_bp.route("/products")
@login_required
@role_required("admin", "staff", "shopkeeper")
def manage_products():
    products = Product.query.order_by(Product.name).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff", "shopkeeper")
def add_product():
    categories = Category.query.all()
    brands = Brand.query.all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", type=float)
        if not name or price is None:
            flash("Name and price required.", "danger")
            return render_template("admin/product_form.html", categories=categories, brands=brands, product=None)
        slug = name.lower().replace(" ", "-")[:150]
        base = slug
        c = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base}-{c}"
            c += 1
        sizes, colors, stock_each = _variant_values(request.form)
        product = Product(
            name=name, slug=slug, price=price, stock=0,
            category_id=request.form.get("category_id", type=int),
            brand_id=request.form.get("brand_id", type=int),
            size=sizes[0], color=colors[0],
            description=request.form.get("description", ""),
            image_url=request.form.get("image_url", "/static/images/products/air-max-90.jpg"),
            image_url_2=request.form.get("image_url_2", "").strip() or None,
            image_url_3=request.form.get("image_url_3", "").strip() or None,
        )
        _replace_variants(product, sizes, colors, stock_each)
        db.session.add(product)
        db.session.commit()
        flash("Product added with size/color variants.", "success")
        return redirect(url_for("admin.manage_products"))
    return render_template("admin/product_form.html", categories=categories, brands=brands, product=None)


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff", "shopkeeper")
def edit_product(pid):
    product = Product.query.get_or_404(pid)
    categories = Category.query.all()
    brands = Brand.query.all()
    if request.method == "POST":
        product.name = request.form.get("name", product.name).strip()
        product.price = request.form.get("price", type=float) or product.price
        product.category_id = request.form.get("category_id", type=int) or product.category_id
        product.brand_id = request.form.get("brand_id", type=int) or product.brand_id
        product.description = request.form.get("description", product.description)
        product.image_url = request.form.get("image_url", product.image_url).strip()
        product.image_url_2 = request.form.get("image_url_2", "").strip() or None
        product.image_url_3 = request.form.get("image_url_3", "").strip() or None
        product.is_active = bool(request.form.get("is_active"))
        sizes, colors, stock_each = _variant_values(request.form, product)
        _replace_variants(product, sizes, colors, stock_each)
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.manage_products"))
    return render_template("admin/product_form.html", categories=categories, brands=brands, product=product)


@admin_bp.route("/users")
@login_required
@role_required("admin")
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/orders")
@login_required
@role_required("admin", "staff")
def manage_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/orders/<int:oid>/status", methods=["POST"])
@login_required
@role_required("admin", "staff")
def update_order_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get("status")
    if new_status in ("pending", "paid", "shipped", "delivered", "cancelled"):
        order.status = new_status
        db.session.commit()
        flash(f"Status updated to {new_status}.", "success")
    return redirect(url_for("admin.manage_orders"))
