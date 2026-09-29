from flask import Blueprint, render_template, request, flash
from backend.models import Product, Category, Brand, Wishlist

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.all()
    brands = Brand.query.all()
    wishlist_ids = set()
    from flask_login import current_user
    if current_user.is_authenticated:
        wishlist_ids = {item.product_id for item in Wishlist.query.filter_by(user_id=current_user.id).all()}
    return render_template("index.html", featured=featured, categories=categories, brands=brands, wishlist_ids=wishlist_ids)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            flash("Thanks for contacting Sneaky Point. We received your message.", "success")
        else:
            flash("Please enter your name.", "warning")
    return render_template("contact.html")
